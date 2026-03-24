"""
py2app setup for Voice2MIDI.

Build the .app bundle:
    python setup.py py2app

Run from the dedicated venv so all dependencies are bundled correctly:
    ~/.voice2midi/venv/bin/python setup.py py2app
"""
from setuptools import setup

APP = ['voice2midi.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['rumps', 'basic_pitch', 'scipy', 'onnxruntime'],
    'iconfile': None,
    'plist': {
        'CFBundleName': 'Voice2MIDI',
        'CFBundleDisplayName': 'Voice2MIDI',
        'CFBundleIdentifier': 'design.publicworks.voice2midi',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
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
