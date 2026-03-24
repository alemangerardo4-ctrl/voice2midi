"""
py2app setup for Voice2MIDI
"""
from setuptools import setup

APP = ['voice2midi.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['rumps'],
    'iconfile': None,
    'plist': {
        'CFBundleName': 'Voice2MIDI',
        'CFBundleDisplayName': 'Voice2MIDI',
        'CFBundleIdentifier': 'design.publicworks.voice2midi',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'LSUIElement': True,  # Background app (no dock icon)
        'NSHighResolutionCapable': True,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
