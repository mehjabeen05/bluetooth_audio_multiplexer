"""
Configuration settings for the Bluetooth audio player.
"""
import os
import json
from pathlib import Path

# Default configuration values
DEFAULT_CONFIG = {
    "output_format": {
        "sample_rate": 44100,
        "sample_width": 2,  # 16-bit
        "channels": 2       # stereo
    },
    "playback": {
        "chunk_size": 1024,
        "buffer_size": 4096
    },
    "detection": {
        "prefer_stereo": True,
        "avoid_hands_free": True
    },
    "debug": False
}

def get_config_path():
    """Get the path to the configuration file."""
    config_dir = os.path.join(str(Path.home()), ".bluetooth_audio_player")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return os.path.join(config_dir, "config.json")

def load_config():
    """Load configuration from file or create default."""
    config_path = get_config_path()
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                
            # Merge with defaults to ensure all options are present
            config = DEFAULT_CONFIG.copy()
            for category, options in user_config.items():
                if category in config:
                    config[category].update(options)
                else:
                    config[category] = options
                    
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG
    else:
        # Create default config
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to file."""
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False