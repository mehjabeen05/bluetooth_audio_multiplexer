"""
Module for processing and converting audio files.
"""
import os
import wave
import tempfile
import subprocess
from pathlib import Path

def check_ffmpeg():
    """Check if FFmpeg is installed and available."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Warning: ffmpeg not found. Audio format conversion may not work properly.")
        return False

def get_audio_info(audio_path):
    """Get audio file information using FFmpeg."""
    if not check_ffmpeg():
        return None
        
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", 
               "stream=codec_name,channels,sample_rate,bits_per_sample", 
               "-of", "default=noprint_wrappers=1:nokey=0", audio_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        info = {}
        for line in result.stdout.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                info[key.strip()] = value.strip()
                
        return info
    except Exception as e:
        print(f"Error getting audio info: {e}")
        return None

def check_audio_file(audio_file):
    """Check if an audio file exists and get its details."""
    if not os.path.exists(audio_file):
        print(f"ERROR: Audio file not found: {audio_file}")
        return False
    
    # Get file extension
    file_extension = Path(audio_file).suffix.lower()
    
    if file_extension == '.wav':
        try:
            with wave.open(audio_file, 'rb') as wf:
                print(f"WAV file details: {audio_file}")
                print(f"  Channels: {wf.getnchannels()}")
                print(f"  Sample width: {wf.getsampwidth()} bytes")
                print(f"  Frame rate: {wf.getframerate()} Hz")
                print(f"  Frames: {wf.getnframes()}")
                print(f"  Duration: {wf.getnframes() / wf.getframerate():.2f} seconds")
            return True
        except Exception as e:
            print(f"Error reading WAV file: {e}")
            return False
    else:
        # For non-WAV files, use FFmpeg to gather information
        info = get_audio_info(audio_file)
        if info:
            print(f"Audio file details: {audio_file}")
            for key, value in info.items():
                print(f"  {key}: {value}")
            return True
        return False

def convert_audio_to_wav(input_path):
    """Convert any audio file to WAV format using FFmpeg."""
    if not check_ffmpeg():
        print("FFmpeg not found. Cannot convert audio format.")
        return None
    
    try:
        temp_dir = tempfile.gettempdir()
        output_wav_path = os.path.join(temp_dir, f"converted_{os.path.basename(input_path)}.wav")
        
        print(f"Converting audio to 16-bit PCM WAV at 44.1kHz...")
        cmd = ["ffmpeg", "-i", input_path, "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", "-y", output_wav_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        print(f"Conversion successful: {output_wav_path}")
        return output_wav_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting audio format: {e}")
        print(f"ffmpeg stderr: {e.stderr.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Unexpected error during conversion: {e}")
        return None

def check_wav_format(wav_path):
    """Check if a WAV file needs conversion to 16-bit PCM."""
    try:
        with wave.open(wav_path, 'rb') as wf:
            sample_width = wf.getsampwidth()
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            
            print(f"Audio format check: Sample width={sample_width}, Sample rate={sample_rate}, Channels={channels}")
            
            # Check if conversion is needed
            needs_conversion = sample_width != 2 or sample_rate != 44100 or channels > 2
            
            if needs_conversion:
                print(f"Conversion needed: Current format is {sample_width*8}-bit, {sample_rate} Hz, {channels} channels")
            else:
                print("No conversion needed: Already 16-bit PCM at 44.1kHz with 1-2 channels")
                
            return needs_conversion
    except Exception as e:
        print(f"Error checking WAV format: {e}")
        return True  # Assume conversion needed if there's an error

def prepare_audio_file(audio_path):
    """
    Prepare any audio file for playback.
    Returns the path to a playable WAV file.
    """
    # Check if the file exists
    if not os.path.exists(audio_path):
        print(f"ERROR: Audio file not found: {audio_path}")
        return None
        
    file_extension = Path(audio_path).suffix.lower()
    
    # If not a WAV file, convert it
    if file_extension != '.wav':
        converted_path = convert_audio_to_wav(audio_path)
        return converted_path
    else:
        # Check if the WAV file needs conversion
        if check_wav_format(audio_path):
            converted_path = convert_audio_to_wav(audio_path)
            return converted_path
        else:
            return audio_path