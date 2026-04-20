"""
py2app setup for Voice2MIDI.

Build the .app bundle:
    ~/.voice2midi/venv/bin/python setup.py py2app

Run from the dedicated venv so all dependencies are bundled correctly:
    ~/.voice2midi/venv/bin/python setup.py py2app

Note: basic_pitch/scipy/onnxruntime are NOT bundled here — they run inside
~/.voice2midi/venv via subprocess and don't need to be in the .app itself.
This keeps the bundle small and allows building with Python 3.9.
"""
from setuptools import setup

APP = ['voice2midi.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['rumps'],
    'resources': ['setup_backend.sh', 'requirements.txt'],
    'iconfile': None,
    'plist': {
        'CFBundleName': 'Voice2MIDI',
        'CFBundleDisplayName': 'Voice2MIDI',
        'CFBundleIdentifier': 'design.publicworks.voice2midi',
        'CFBundleVersion': '2.2.0',
        'CFBundleShortVersionString': '2.2',
        'LSUIElement': True,           # Menu bar only — no Dock icon
        'NSHighResolutionCapable': True,
        'NSMicrophoneUsageDescription': 'Voice2MIDI does not use the microphone.',
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
