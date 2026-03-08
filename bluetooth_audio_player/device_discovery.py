"""
Module for detecting and filtering Bluetooth audio devices.
"""
import re
import platform
import subprocess
import pyaudio

def get_windows_bluetooth_devices():
    """Get list of active Bluetooth device names on Windows."""
    try:
        cmd = "Get-PnpDevice | Where-Object { $_.Class -eq 'Bluetooth' -and $_.Status -eq 'OK' -and $_.ConfigManagerErrorCode -eq 0 } | Select-Object FriendlyName"
        result = subprocess.run(["powershell", "-Command", cmd], 
                               capture_output=True, text=True, check=True)
        
        bt_device_names = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line and not line.startswith("FriendlyName") and not line.startswith("-"):
                bt_device_names.append(line)
        
        return bt_device_names
        
    except subprocess.CalledProcessError as e:
        print(f"Error getting Windows Bluetooth devices: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def match_with_pyaudio(bt_device_names):
    """
    Matches Bluetooth device names with PyAudio output devices.
    Returns list of tuples with (device_index, device_name)
    """
    p = pyaudio.PyAudio()
    matching_devices = []
    
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxOutputChannels'] > 0: 
            dev_name = dev['name']
            
            for bt_name in bt_device_names:
                if bt_name.lower() in dev_name.lower():
                    matching_devices.append((i, dev_name))
                    print(f"  -> Matched with Bluetooth device: {bt_name}")
                    break
    
    p.terminate()
    return matching_devices

def get_bluetooth_devices():
    """Detect Bluetooth devices across different operating systems."""
    system = platform.system()
    
    if system == "Windows":
        bt_device_names = get_windows_bluetooth_devices()
    elif system == "Linux":
        bt_device_names = get_linux_bluetooth_devices()
    elif system == "Darwin":  # macOS
        bt_device_names = get_macos_bluetooth_devices()
    else:
        print(f"System {system} not currently supported")
        return []
        
    return match_with_pyaudio(bt_device_names)

def extract_base_device_name(device_name):
    """Extract the base name of a device from its full name."""
    match = re.search(r'\(([^()]+)\)$', device_name)
    if match:
        return match.group(1).strip()
    
    match = re.search(r'\(([^()]+)\)', device_name)
    if match:
        return match.group(1).strip()
    
    return device_name

def filter_best_device_instances(devices):
    """Filter multiple instances of the same device to get the best one."""
    unique_devices = {}
    device_scores = {}
    
    for idx, name in devices:
        base_name = extract_base_device_name(name)
        
        if base_name not in device_scores:
            device_scores[base_name] = {}
            
        score = 0
        if "stereo" in name.lower():
            score += 10
        if "hands-free" in name.lower():
            score -= 5
        if "headset" in name.lower():
            score -= 3
            
        device_scores[base_name][idx] = score
    
    for base_name, scores in device_scores.items():
        if scores:  
            best_idx = max(scores, key=scores.get)
            
            for idx, name in devices:
                if idx == best_idx:
                    unique_devices[base_name] = (idx, name)
                    break
    
    return list(unique_devices.values())

def verify_device_connection(device_index):
    """Verify that a device is actually connected and responsive."""
    try:
        p = pyaudio.PyAudio()
        
        test_stream = p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            output=True,
            output_device_index=device_index,
            frames_per_buffer=1024,
            start=False  
        )
        test_stream.close()
        p.terminate()
        return True
    except:
        p.terminate()
        return False

def verify_connected_devices(filtered_devices):
    """Verify all devices are connected and responding."""
    connected_devices = []
    
    for idx, name in filtered_devices:
        if verify_device_connection(idx):
            connected_devices.append((idx, name))
            print(f"  Device index: {idx}, Name: {name} - CONNECTION VERIFIED")
        else:
            print(f"  Device index: {idx}, Name: {name} - NOT RESPONDING (SKIPPED)")
            
    return connected_devices
