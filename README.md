# Bluetooth Audio Player

A modular Python application for playing audio files to multiple Bluetooth devices simultaneously. This package supports various audio formats and will automatically convert them to a compatible format for playback.

## Features

- Automatically detect Bluetooth audio devices in Windows 10/11.
- Play audio to multiple Bluetooth devices simultaneously
- Support for various audio formats (MP3, FLAC, AAC, OGG, etc.) with automatic conversion
- Filter and select the best audio profiles for each device
- Modular architecture for easy customization and extension

## Requirements

- Python 3.6+
- PyAudio
- FFmpeg (for audio format conversion)

## Installation

### From source

```bash
git clone https://github.com/int33k/bluetooth-audio-multiplexer.git
cd bluetooth-audio-player
pip install -e .
```

## Usage

### Command-line interface

```bash
# Play an audio file to all detected Bluetooth devices
bt-audio-multiplexer path/to/audio/file.mp3

# List all available audio devices
bt-audio-multiplexer --list-devices path/to/audio/file.mp3

# Play to specific devices
bt-audio-multiplexer --device-indices 1,3,5 path/to/audio/file.mp3

# Enable debug mode
bt-audio-multiplexer --debug path/to/audio/file.mp3
```

### As a Python package

```python
from bluetooth_audio_player import device_discovery, audio_processor, playback

# Get available Bluetooth devices
devices = device_discovery.get_bluetooth_devices()
filtered_devices = device_discovery.filter_best_device_instances(devices)
connected_devices = device_discovery.verify_connected_devices(filtered_devices)

# Prepare any audio file for playback
wav_file = audio_processor.prepare_audio_file("my_audio.mp3")

# Play to multiple devices
device_indices = [idx for idx, _ in connected_devices]
playback.play_audio_to_multiple_devices(wav_file, device_indices)
```

## Configuration

The application creates a configuration file at `~/.bluetooth_audio_multiplexer/config.json`. You can modify this file to customize the behavior:

```json
{
  "output_format": {
    "sample_rate": 44100,
    "sample_width": 2,
    "channels": 2
  },
  "playback": {
    "chunk_size": 1024,
    "buffer_size": 4096
  },
  "detection": {
    "prefer_stereo": true,
    "avoid_hands_free": true
  },
  "debug": false
}
```

## License

MIT
