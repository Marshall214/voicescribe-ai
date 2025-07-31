import os
import tempfile
from pydub import AudioSegment
from pydub.utils import which
import streamlit as st

class AudioProcessor:
    def __init__(self):
        # Set up ffmpeg path if needed
        AudioSegment.converter = which("ffmpeg")
        AudioSegment.ffmpeg = which("ffmpeg")
        AudioSegment.ffprobe = which("ffprobe")
        
        # Create temp directory if it doesn't exist
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def process_audio(self, audio_file_path):
        """
        Process audio file to ensure it's in the right format for transcription
        """
        try:
            # Load audio file
            if audio_file_path.lower().endswith('.wav'):
                audio = AudioSegment.from_wav(audio_file_path)
            elif audio_file_path.lower().endswith('.mp3'):
                audio = AudioSegment.from_mp3(audio_file_path)
            elif audio_file_path.lower().endswith('.m4a'):
                audio = AudioSegment.from_file(audio_file_path, format="m4a")
            elif audio_file_path.lower().endswith('.flac'):
                audio = AudioSegment.from_file(audio_file_path, format="flac")
            elif audio_file_path.lower().endswith('.ogg'):
                audio = AudioSegment.from_ogg(audio_file_path)
            elif audio_file_path.lower().endswith('.aac'):
                audio = AudioSegment.from_file(audio_file_path, format="aac")
            elif audio_file_path.lower().endswith('.wma'):
                audio = AudioSegment.from_file(audio_file_path, format="wma")
            else:
                # Try to load as generic audio file
                audio = AudioSegment.from_file(audio_file_path)
            
            # Normalize audio
            audio = self.normalize_audio(audio)
            
            # Convert to WAV format for Whisper (16kHz, mono)
            audio = audio.set_frame_rate(16000)
            audio = audio.set_channels(1)
            
            # Save processed audio
            output_path = os.path.join(self.temp_dir, "processed_audio.wav")
            audio.export(output_path, format="wav")
            
            return output_path
            
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")
            raise e
    
    def normalize_audio(self, audio):
        """
        Normalize audio levels and remove silence
        """
        try:
            # Normalize volume
            normalized = audio.normalize()
            
            # Remove silence from beginning and end
            normalized = normalized.strip_silence(silence_threshold=-50)
            
            # If audio is too quiet, amplify it
            if normalized.dBFS < -20:
                normalized = normalized + (abs(normalized.dBFS) - 20)
            
            return normalized
            
        except Exception as e:
            st.warning(f"Warning: Could not normalize audio: {str(e)}")
            return audio
    
    def get_audio_info(self, audio_file_path):
        """
        Get information about the audio file
        """
        try:
            audio = AudioSegment.from_file(audio_file_path)
            
            info = {
                'duration': len(audio) / 1000.0,  # in seconds
                'frame_rate': audio.frame_rate,
                'channels': audio.channels,
                'format': audio_file_path.split('.')[-1].upper(),
                'file_size': os.path.getsize(audio_file_path) / (1024 * 1024)  # in MB
            }
            
            return info
            
        except Exception as e:
            st.warning(f"Could not get audio info: {str(e)}")
            return None
    
    def cleanup_temp_files(self):
        """
        Clean up temporary files
        """
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            st.warning(f"Could not clean up temp files: {str(e)}")
    
    def __del__(self):
        """
        Clean up when object is destroyed
        """
        self.cleanup_temp_files()