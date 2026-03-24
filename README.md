# Voice2MIDI

A lightweight macOS menu bar tool that converts audio files to MIDI using AI.

Powered by Spotify's [basic-pitch](https://github.com/spotify/basic-pitch) — drop in an audio file, get a MIDI file on your Desktop.

---

## What it does

- Sits in your menu bar (🎵)
- Click **Convert Audio…** → pick any audio file (WAV, MP3, FLAC, etc.)
- Runs basic-pitch in the background
- Saves the resulting `.mid` file to `~/Desktop/midi/` and reveals it in Finder

That's it. No microphone recording, no real-time processing, no AU/VST3 plugins.

---

## Requirements

- macOS 11+
- Python 3.10+

---

## Install

```bash
git clone https://github.com/your-org/voice2midi.git
cd voice2midi
bash setup_backend.sh
```

The setup script creates a dedicated Python environment at `~/.voice2midi/venv` and installs all dependencies.

---

## Run

```bash
~/.voice2midi/venv/bin/python voice2midi.py
```

The 🎵 icon appears in your menu bar.

---

## Build a standalone .app (optional)

```bash
~/.voice2midi/venv/bin/pip install py2app
~/.voice2midi/venv/bin/python setup.py py2app
# Output: dist/Voice2MIDI.app
```

---

## How it works

1. You select an audio file via the macOS file picker.
2. Voice2MIDI calls basic-pitch with the `onnx` model serialization for fast, offline inference.
3. basic-pitch outputs a standard `.mid` file to `~/Desktop/midi/`.

---

## Notes

- Best results with monophonic audio (single melody line, vocals, single instrument).
- Polyphonic audio will be transcribed but results vary.
- First conversion may be slow while the ONNX model loads.

---

## License

MIT — Part of [PUBLIC WORKS](https://publicworks.design), open source audio tools for creators.
