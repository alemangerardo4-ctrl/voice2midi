#!/usr/bin/env python3
import os
import rumps
import subprocess
import threading
import logging
from pathlib import Path
import sys
import tempfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

VENV_PYTHON = Path.home() / ".voice2midi" / "venv" / "bin" / "python3"


def find_venv_python():
    """Find the venv python to use for basic-pitch conversion.

    Priority:
    1. Already running inside a venv (sys.prefix != sys.base_prefix)
    2. ~/.voice2midi/venv
    """
    if sys.prefix != sys.base_prefix:
        py = Path(sys.prefix) / "bin" / "python3"
        if py.exists():
            return py
    if VENV_PYTHON.exists():
        return VENV_PYTHON
    return None


def _find_bundle_resource(filename):
    """Find a resource file in the .app bundle Resources or alongside this script."""
    resource_path = os.environ.get('RESOURCEPATH')
    if resource_path:
        candidate = Path(resource_path) / filename
        if candidate.exists():
            return candidate
    candidate = Path(__file__).parent / filename
    if candidate.exists():
        return candidate
    return None


def _osascript(script):
    return subprocess.run(['osascript', '-e', script], capture_output=True, text=True)


def auto_setup_if_needed():
    """Run first-time backend setup if the venv is missing. Returns False to abort launch."""
    if find_venv_python():
        return True

    setup_script = _find_bundle_resource('setup_backend.sh')
    if not setup_script:
        _osascript(
            'display alert "Voice2MIDI \u2014 Setup Required" '
            'message "The backend setup script was not found inside the app bundle. '
            'Please re-download Voice2MIDI." '
            'as critical buttons {"Quit"} default button "Quit"'
        )
        return False

    r = _osascript(
        'button returned of (display dialog '
        '"Voice2MIDI needs to install its AI backend.\n\n'
        'This is a one-time setup that downloads about 1.5 GB '
        'and takes several minutes.\n'
        'The app will launch automatically when complete.\n\n'
        'Click Install to begin." '
        'buttons {"Cancel", "Install"} default button "Install" '
        'with title "Voice2MIDI \u2014 First-Time Setup")'
    )
    if r.returncode != 0 or r.stdout.strip() != 'Install':
        return False

    _osascript(
        'display notification "Installing Voice2MIDI backend. This will take several minutes..." '
        'with title "Voice2MIDI" subtitle "First-time setup in progress"'
    )

    proc = subprocess.run(['bash', str(setup_script)], capture_output=True, text=True)

    if proc.returncode == 0:
        _osascript(
            'display notification "Voice2MIDI is ready to use!" '
            'with title "Voice2MIDI" subtitle "Setup complete"'
        )
        return True

    _osascript(
        'display alert "Voice2MIDI Setup Failed" '
        'message "Installation failed.\n\n'
        'Please ensure Python 3.10+ is installed:\n\n'
        '    brew install python@3.12\n\n'
        'Then relaunch Voice2MIDI." '
        'as critical buttons {"OK"} default button "OK"'
    )
    return False


class Voice2MIDIApp(rumps.App):
    def __init__(self):
        super().__init__("🎵", quit_button=rumps.MenuItem('Quit'))
        self.output_dir = Path.home() / "Desktop" / "midi"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.venv_python = find_venv_python()
        if not self.venv_python:
            rumps.alert(
                "Voice2MIDI — Backend Not Found",
                "Could not find the Python backend.\n\n"
                "Please run the setup script first:\n\n"
                "    bash setup_backend.sh\n\n"
                "Then relaunch Voice2MIDI.",
            )
            rumps.quit_application()
            return

        logger.info("Using venv python: %s", self.venv_python)

        self.converting = False
        self.status_item = rumps.MenuItem('Status: Ready')
        self.menu = [
            rumps.MenuItem('Convert Audio...', callback=self.select_file),
            rumps.separator,
            rumps.MenuItem('Output: ~/Desktop/midi/'),
            self.status_item,
        ]

    @rumps.clicked('Convert Audio...')
    def select_file(self, _):
        if self.converting:
            rumps.alert("Busy", "A conversion is already in progress.")
            return
        script = (
            'tell app "Finder"\n'
            'activate\n'
            'POSIX path of (choose file with prompt "Select an audio file to convert:")\n'
            'end tell'
        )
        try:
            r = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=120
            )
            if r.returncode == 0 and r.stdout.strip():
                f = Path(r.stdout.strip())
                if f.exists():
                    threading.Thread(target=self.convert, args=(f,), daemon=True).start()
        except Exception as e:
            logger.error("File picker error: %s", e)

    def convert(self, f):
        self.converting = True
        self.title = "🎵⏳"
        self.status_item.title = 'Status: Converting...'
        rumps.notification("Voice2MIDI", f.name, "Processing...", sound=False)
        try:
            # scipy >= 1.12 removed scipy.signal.gaussian (moved to
            # scipy.signal.windows.gaussian). basic-pitch calls the old path,
            # so we patch it back before importing basic_pitch.
            code = (
                'import scipy.signal.windows as _w, scipy.signal as _s\n'
                '_s.gaussian = _w.gaussian\n'
                'from basic_pitch.predict import main\n'
                'import sys\n'
                f'sys.argv = ["basic-pitch", "{self.output_dir}", "{f}", '
                '"--save-midi", "--model-serialization", "onnx"]\n'
                'main()\n'
            )
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
                tf.write(code)
                tmp_path = tf.name

            r = subprocess.run(
                [str(self.venv_python), tmp_path],
                capture_output=True, timeout=300
            )
            Path(tmp_path).unlink(missing_ok=True)

            if r.returncode == 0:
                out = self.output_dir / (f.stem + "_basic_pitch.mid")
                if out.exists():
                    rumps.notification("Voice2MIDI ✅", "Done!", out.name, sound=True)
                    subprocess.run(["open", "-R", str(out)])
                else:
                    stderr = r.stderr.decode(errors='replace')
                    logger.error("basic-pitch stderr: %s", stderr)
                    raise RuntimeError("Output MIDI file not found after conversion")
            else:
                stderr = r.stderr.decode(errors='replace')
                logger.error("basic-pitch failed (exit %d): %s", r.returncode, stderr)
                raise RuntimeError(f"Conversion failed (exit {r.returncode})")

        except Exception as e:
            logger.error("Conversion error: %s", e)
            rumps.notification("Voice2MIDI ❌", "Error", str(e)[:120], sound=True)
        finally:
            self.converting = False
            self.title = "🎵"
            self.status_item.title = 'Status: Ready'


if __name__ == '__main__':
    if not auto_setup_if_needed():
        sys.exit(0)
    Voice2MIDIApp().run()
