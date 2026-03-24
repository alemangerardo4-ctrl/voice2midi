#!/usr/bin/env python3
import rumps
import subprocess
import threading
from pathlib import Path
import tempfile

class Voice2MIDIApp(rumps.App):
    def __init__(self):
        super(Voice2MIDIApp, self).__init__("🎵", quit_button=rumps.MenuItem('Quit'))
        self.output_dir = Path.home() / "Desktop" / "midi"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.venv_python = None
        self.script_path = None
        for base in [Path.home() / "music-tools", Path.home() / "music-tools-FINAL-TEST"]:
            venv = base / "venv" / "bin" / "python3"
            if venv.exists():
                self.venv_python = venv
                self.script_path = base / "venv" / "lib" / "python3.12" / "site-packages"
                break
        if not self.venv_python:
            rumps.alert("Error", "Backend missing")
            rumps.quit_application()
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
            rumps.alert("Busy", "Converting...")
            return
        script = 'tell app "Finder"\nactivate\nPOSIX path of (choose file with prompt "Select audio:")\nend tell'
        try:
            r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=120)
            if r.returncode == 0 and r.stdout.strip():
                f = Path(r.stdout.strip())
                if f.exists():
                    threading.Thread(target=self.convert, args=(f,), daemon=True).start()
        except: pass
    
    def convert(self, f):
        self.converting = True
        self.title = "🎵⏳"
        self.status_item.title = 'Status: Converting...'
        rumps.notification("Voice2MIDI", f.name, "Processing...", sound=False)
        try:
            code = f'import sys\nsys.path.insert(0,"{self.script_path}")\nimport scipy.signal.windows as w,scipy.signal as s\ns.gaussian=w.gaussian\nfrom basic_pitch.predict import main\nsys.argv=["basic-pitch","{self.output_dir}","{f}","--save-midi","--model-serialization","onnx"]\nmain()'
            with tempfile.NamedTemporaryFile(mode='w',suffix='.py',delete=False) as tf:
                tf.write(code)
                t=tf.name
            r = subprocess.run([str(self.venv_python),t], capture_output=True, timeout=300)
            Path(t).unlink()
            if r.returncode == 0:
                out = self.output_dir / (f.stem + "_basic_pitch.mid")
                if out.exists():
                    rumps.notification("Voice2MIDI ✅", "Done!", out.name, sound=True)
                    subprocess.run(["open", "-R", str(out)])
                else:
                    raise Exception("Output missing")
            else:
                raise Exception("Failed")
        except Exception as e:
            rumps.notification("Voice2MIDI ❌", "Error", str(e)[:100], sound=True)
        finally:
            self.converting = False
            self.title = "🎵"
            self.status_item.title = 'Status: Ready'

if __name__ == '__main__':
    Voice2MIDIApp().run()
