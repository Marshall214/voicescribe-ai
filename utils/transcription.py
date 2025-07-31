import whisper
import os
import streamlit as st
from typing import Optional

class WhisperTranscriber:
    def __init__(self, model_size="base"):
        """
        Initialize Whisper transcriber
        
        Args:
            model_size: Size of the Whisper model to use
                       Options: tiny, base, small, medium, large
        """
        self.model_size = model_size
        self.model = None
        self.load_model()
    
    @st.cache_resource
    def load_model(_self):
        """
        Load the Whisper model (cached to avoid reloading)
        """
        try:
            model = whisper.load_model(_self.model_size)
            return model
        except Exception as e:
            st.error(f"Error loading Whisper model: {str(e)}")
            return None
    
    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to the audio file
            language: Language code (e.g., 'en' for English, 'es' for Spanish)
                     If None, Whisper will auto-detect
        
        Returns:
            Transcribed text
        """
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            if self.model is None:
                self.model = self.load_model()
            
            if self.model is None:
                raise Exception("Failed to load Whisper model")
            
            # Transcribe audio
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                task="transcribe",
                verbose=False
            )
            
            # Extract text
            transcribed_text = result["text"].strip()
            
            if not transcribed_text:
                return "No speech detected in the audio file."
            
            return transcribed_text
            
        except Exception as e:
            st.error(f"Error during transcription: {str(e)}")
            return f"Transcription failed: {str(e)}"
    
    def transcribe_with_timestamps(self, audio_file_path: str, language: Optional[str] = None) -> dict:
        """
        Transcribe audio with word-level timestamps
        
        Args:
            audio_file_path: Path to the audio file
            language: Language code
        
        Returns:
            Dictionary with text and segments with timestamps
        """
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            if self.model is None:
                self.model = self.load_model()
            
            if self.model is None:
                raise Exception("Failed to load Whisper model")
            
            # Transcribe with timestamps
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                task="transcribe",
                verbose=False,
                word_timestamps=True
            )
            
            return {
                'text': result["text"].strip(),
                'segments': result.get("segments", []),
                'language': result.get("language", "unknown")
            }
            
        except Exception as e:
            st.error(f"Error during transcription with timestamps: {str(e)}")
            return {
                'text': f"Transcription failed: {str(e)}",
                'segments': [],
                'language': "unknown"
            }
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages
        
        Returns:
            List of supported language codes
        """
        try:
            # Whisper supported languages
            languages = [
                "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
                "ar", "hi", "th", "vi", "uk", "pl", "nl", "sv", "da", "no"
            ]
            return languages
        except Exception as e:
            st.warning(f"Could not get supported languages: {str(e)}")
            return ["en"]
    
    def detect_language(self, audio_file_path: str) -> str:
        """
        Detect the language of the audio file
        
        Args:
            audio_file_path: Path to the audio file
        
        Returns:
            Detected language code
        """
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            if self.model is None:
                self.model = self.load_model()
            
            if self.model is None:
                raise Exception("Failed to load Whisper model")
            
            # Load audio and detect language
            audio = whisper.load_audio(audio_file_path)
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram and move to the same device as the model
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect the spoken language
            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            
            return detected_language
            
        except Exception as e:
            st.warning(f"Could not detect language: {str(e)}")
            return "en"  # Default to English
    
    def get_model_info(self) -> dict:
        """
        Get information about the current model
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_size': self.model_size,
            'model_loaded': self.model is not None,
            'supported_languages': self.get_supported_languages()
        }