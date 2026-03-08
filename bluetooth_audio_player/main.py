"""
Main application entry point for the Bluetooth audio player.
"""
import os
import argparse
from pathlib import Path

from bluetooth_audio_player import device_discovery
from bluetooth_audio_player import audio_processor
from bluetooth_audio_player import playback
from bluetooth_audio_player import utils
from bluetooth_audio_player import config

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Play audio files to multiple Bluetooth devices simultaneously"
    )
    
    parser.add_argument(
        "audio_file", 
        help="Path to the audio file to play"
    )
    
    parser.add_argument(
        "--list-devices", 
        action="store_true",
        help="List all detected audio output devices and exit"
    )
    
    parser.add_argument(
        "--device-indices", 
        type=str,
        help="Comma-separated list of device indices to play on (overrides auto-detection)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode with verbose output"
    )
    
    return parser.parse_args()

def main():
    """Main application function."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Load configuration
    cfg = config.load_config()
    
    # Set debug mode
    if args.debug:
        cfg["debug"] = True
    
    # Print system info in debug mode
    if cfg["debug"]:
        utils.get_system_info()
    
    # List devices if requested
    if args.list_devices:
        p = __import__('pyaudio').PyAudio()
        print("\nAll Audio Output Devices:")
        
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxOutputChannels'] > 0:
                print(f"  Device index: {i}, Name: {dev['name']}")
                
        p.terminate()
        return
    
    # Validate the audio file
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        return 1
    
    print(f"Processing audio file: {args.audio_file}")
    
    # Check and prepare the audio file
    converted_audio_file = audio_processor.prepare_audio_file(args.audio_file)
    if not converted_audio_file:
        print("Failed to prepare audio file for playback")
        return 1
    
    # Use specified device indices if provided
    if args.device_indices:
        try:
            device_indices = [int(idx.strip()) for idx in args.device_indices.split(',')]
            
            # Create list of devices with names for display
            p = __import__('pyaudio').PyAudio()
            selected_devices = []
            
            for idx in device_indices:
                try:
                    info = p.get_device_info_by_index(idx)
                    selected_devices.append((idx, info['name']))
                except:
                    print(f"Warning: Device index {idx} not found")
            
            p.terminate()
            
            if not selected_devices:
                print("No valid device indices specified")
                return 1
                
            utils.print_devices_info(selected_devices, "Using specified devices")
            
        except ValueError:
            print("Error: Device indices must be comma-separated integers")
            return 1
    else:
        # Auto-detect Bluetooth devices
        print("Detecting active Bluetooth audio devices...")
        bt_devices = device_discovery.get_bluetooth_devices()
        
        if not bt_devices:
            print("No active Bluetooth audio devices detected.")
            return 0
            
        utils.print_devices_info(bt_devices, "All detected Bluetooth audio devices")
        
        # Filter best device instances
        filtered_devices = device_discovery.filter_best_device_instances(bt_devices)
        utils.print_devices_info(filtered_devices, "Filtered active Bluetooth audio devices")
        
        # Verify devices are connected
        selected_devices = device_discovery.verify_connected_devices(filtered_devices)
        
        if not selected_devices:
            print("\nNo connected Bluetooth audio devices found for playback.")
            print("Please ensure your devices are properly connected.")
            return 1
            
        utils.print_devices_info(selected_devices, "Selected devices for playback")
        device_indices = [idx for idx, _ in selected_devices]
    
    # Start playback
    print("\nStarting playback process...")
    playback.play_audio_to_multiple_devices(converted_audio_file, device_indices)
    
    # Clean up temporary files
    if converted_audio_file != args.audio_file:
        utils.clean_temp_files(converted_audio_file)
    
    print("Playback completed successfully")
    return 0

if __name__ == "__main__":
    exit(main())