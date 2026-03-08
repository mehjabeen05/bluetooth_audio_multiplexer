"""
Module for audio playback functionality.
"""
import wave
import pyaudio
import threading
import os

def play_audio(device_index, wav_path, p=None):
    """
    Play audio on a specific device.
    
    Args:
        device_index: Index of the audio device
        wav_path: Path to the WAV file to play
        p: PyAudio instance (optional)
    """
    wf = None
    stream = None
    own_pyaudio = False
    
    try:
        wf = wave.open(wav_path, 'rb')
        
        # Create PyAudio instance if not provided
        if p is None:
            p = pyaudio.PyAudio()
            own_pyaudio = True
        
        # Get audio format details
        width = wf.getsampwidth()
        channels = wf.getnchannels()
        rate = wf.getframerate()
        
        print(f"Audio format: width={width}, channels={channels}, rate={rate}")
        format_type = p.get_format_from_width(width)
        print(f"Opening stream on device {device_index} with format {format_type}")
        
        try:
            stream = p.open(
                format=format_type,
                channels=channels,
                rate=rate,
                output=True,
                output_device_index=device_index
            )
            
            print(f"Stream opened successfully for device {device_index}")
            
            # Read and play audio data in chunks
            chunk_size = 1024
            data = wf.readframes(chunk_size)
            
            print(f"Starting data playback on device {device_index}")
            
            while data:
                try:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                except Exception as e:
                    print(f"Error writing to stream on device {device_index}: {e}")
                    break
            
            print(f"Closing stream for device {device_index}")
            
        except Exception as e:
            print(f"Error creating stream for device {device_index}: {e}")
        
    except Exception as e:
        print(f"Error playing to device {device_index}: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up resources
        if stream:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
        
        if wf:
            try:
                wf.close()
            except:
                pass
            
        if own_pyaudio and p:
            try:
                p.terminate()
            except:
                pass
                
        print(f"Playback completed on device {device_index}")

def play_audio_to_multiple_devices(wav_path, device_indices):
    """
    Play audio to multiple devices simultaneously.
    
    Args:
        wav_path: Path to the WAV file to play
        device_indices: List of device indices to play on
    """
    if not device_indices:
        print("No devices specified for playback")
        return
    
    # Create a single PyAudio instance to be shared
    p = pyaudio.PyAudio()
    
    try:
        # Create a thread for each device
        threads = []
        for idx in device_indices:
            thread = threading.Thread(target=play_audio, args=(idx, wav_path, p))
            thread.daemon = False
            threads.append(thread)
        
        # Start all threads
        print(f"Starting playback on {len(threads)} devices...")
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        print("Waiting for playback to complete...")
        for thread in threads:
            thread.join()
        
        print("Playback completed on all devices")
    
    finally:
        # Clean up PyAudio
        try:
            p.terminate()
            print("PyAudio terminated")
        except:
            pass