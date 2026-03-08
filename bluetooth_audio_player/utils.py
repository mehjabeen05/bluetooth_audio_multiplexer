"""
Utility functions for the Bluetooth audio player.
"""
import os
import platform
import sys
import shutil

def is_tool_available(name):
    """Check if a command-line tool is available."""
    return shutil.which(name) is not None

def clean_temp_files(file_path):
    """Remove temporary files."""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Temporary file removed: {file_path}")
            return True
        except Exception as e:
            print(f"Error removing temporary file: {e}")
            return False
    return False

def get_system_info():
    """Get and print system information."""
    system_info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Architecture": platform.machine(),
        "Python Version": sys.version,
    }
    
    print("\nSystem Information:")
    for key, value in system_info.items():
        print(f"  {key}: {value}")
        
    # Check for required tools
    tools = {
        "FFmpeg": is_tool_available("ffmpeg"),
        "FFprobe": is_tool_available("ffprobe")
    }
    
    print("\nRequired Tools:")
    for tool, available in tools.items():
        status = "Available" if available else "Not Found"
        print(f"  {tool}: {status}")
        
    return system_info, tools

def print_devices_info(devices, title="Detected Audio Devices"):
    """Print information about audio devices."""
    if not devices:
        print("No audio devices detected.")
        return
        
    print(f"\n{title}:")
    for idx, name in devices:
        print(f"  Device index: {idx}, Name: {name}")