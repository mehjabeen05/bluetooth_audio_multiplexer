"""
Setup script for the Bluetooth Audio Player package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bluetooth-audio-player",
    version="1.0.0",
    author="Intekhab",
    author_email="mintekhabahmad@gmail.com",
    description="Play audio to multiple Bluetooth devices simultaneously",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/bluetooth-audio-player",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyaudio>=0.2.11",
    ],
    entry_points={
        "console_scripts": [
            "bt-audio-multiplexer=bluetooth_audio_player.main:main",
        ],
    },
)