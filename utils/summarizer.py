import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re
from typing import Dict, List

class HuggingFaceSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        """
        Initialize the summarizer with a pre-trained model
        
        Args:
            model_name: Name of the HuggingFace model to use
        """
        self.model_name = model_name
        self.summarizer = None
        self.tokenizer = None
        self.max_input_length = 1024
        self.load_model()
    
    @st.cache_resource
    def load_model(_self):
        """
        Load the summarization model (cached to avoid reloading)
        """
        try:
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(_self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(_self.model_name)
            
            # Create summarization pipeline
            summarizer = pipeline(
                "summarization",
                model=model,
                tokenizer=tokenizer,
                device=0 if torch.cuda.is_available() else -1,
                framework="pt"
            )
            
            return summarizer, tokenizer
            
        except Exception as e:
            st.error(f"Error loading summarization model: {str(e)}")
            return None, None
    
    def chunk_text(self, text: str, max_length: int = 1024) -> List[str]:
        """
        Split text into chunks that fit within the model's token limit
        
        Args:
            text: Input text to chunk
            max_length: Maximum length per chunk
        
        Returns:
            List of text chunks
        """
        try:
            if self.tokenizer is None:
                self.summarizer, self.tokenizer = self.load_model()
            
            # Tokenize the text
            tokens = self.tokenizer.encode(text, truncation=False)
            
            # If text is within limit, return as single chunk
            if len(tokens) <= max_length:
                return [text]
            
            # Split into sentences for better chunking
            sentences = re.split(r'[.!?]+', text)
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                test_chunk = current_chunk + sentence + ". "
                test_tokens = self.tokenizer.encode(test_chunk, truncation=False)
                
                if len(test_tokens) <= max_length:
                    current_chunk = test_chunk
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
                    else:
                        # If single sentence is too long, truncate it
                        truncated = self.tokenizer.decode(
                            self.tokenizer.encode(sentence, max_length=max_length, truncation=True)
                        )
                        chunks.append(truncated)
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            return chunks
            
        except Exception as e:
            st.warning(f"Error chunking text: {str(e)}")
            return [text[:2000]]  # Fallback to simple truncation
    
    def summarize(self, text: str, config: Dict) -> str:
        """
        Summarize the input text based on configuration
        
        Args:
            text: Input text to summarize
            config: Configuration dictionary with length, style, focus
        
        Returns:
            Summarized text
        """
        try:
            if not text or len(text.strip()) < 50:
                return "Text too short to summarize effectively."
            
            if self.summarizer is None:
                self.summarizer, self.tokenizer = self.load_model()
            
            if self.summarizer is None:
                raise Exception("Failed to load summarization model")
            
            # Clean and prepare text
            cleaned_text = self.clean_text(text)
            
            # Determine summary parameters based on config
            min_length, max_length = self.get_length_params(config['length'])
            
            # Chunk text if necessary
            chunks = self.chunk_text(cleaned_text)
            
            # Summarize each chunk
            chunk_summaries = []
            for chunk in chunks:
                try:
                    summary = self.summarizer(
                        chunk,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False,
                        num_beams=4,
                        length_penalty=2.0,
                        early_stopping=True
                    )
                    
                    if summary and len(summary) > 0:
                        chunk_summaries.append(summary[0]['summary_text'])
                
                except Exception as e:
                    st.warning(f"Error summarizing chunk: {str(e)}")
                    continue
            
            # Combine chunk summaries
            if not chunk_summaries:
                return "Could not generate summary."
            
            combined_summary = " ".join(chunk_summaries)
            
            # Post-process based on style and focus
            final_summary = self.post_process_summary(combined_summary, config)
            
            return final_summary
            
        except Exception as e:
            st.error(f"Error during summarization: {str(e)}")
            return f"Summarization failed: {str(e)}"
    
    def clean_text(self, text: str) -> str:
        """
        Clean and prepare text for summarization
        
        Args:
            text: Input text
        
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might confuse the model
        text = re.sub(r'[^\w\s\.\,\!\?\;]', '', text)
        
        # Ensure proper sentence endings
        text = re.sub(r'([a-z])([A-Z])', r'\1. \2', text)
        
        return text.strip()
    
    def get_length_params(self, length_setting: str) -> tuple:
        """
        Get min and max length parameters based on setting
        
        Args:
            length_setting: Length setting from config
        
        Returns:
            Tuple of (min_length, max_length)
        """
        if "Short" in length_setting:
            return 10, 50
        elif "Medium" in length_setting:
            return 50, 150
        elif "Long" in length_setting:
            return 100, 300
        else:
            return 50, 150  # Default to medium
    
    def post_process_summary(self, summary: str, config: Dict) -> str:
        """
        Post-process summary based on style and focus
        
        Args:
            summary: Raw summary text
            config: Configuration dictionary
        
        Returns:
            Post-processed summary
        """
        try:
            # Apply style formatting
            if config['style'] == "Bullet Points":
                summary = self.format_as_bullets(summary)
            elif config['style'] == "Executive Summary":
                summary = self.format_as_executive_summary(summary)
            # Paragraph style needs no special formatting
            
            # Apply focus filtering (basic implementation)
            if config['focus'] == "Key Points":
                summary = self.emphasize_key_points(summary)
            elif config['focus'] == "Action Items":
                summary = self.extract_action_items(summary)
            elif config['focus'] == "Decisions Made":
                summary = self.extract_decisions(summary)
            
            return summary
            
        except Exception as e:
            st.warning(f"Error in post-processing: {str(e)}")
            return summary
    
    def format_as_bullets(self, text: str) -> str:
        """Convert text to bullet points"""
        sentences = re.split(r'[.!?]+', text)
        bullets = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                bullets.append(f"• {sentence}")
        
        return "\n".join(bullets)
    
    def format_as_executive_summary(self, text: str) -> str:
        """Format as executive summary"""
        return f"**Executive Summary:**\n\n{text}"
    
    def emphasize_key_points(self, text: str) -> str:
        """Emphasize key points in the summary"""
        # Simple implementation - you can enhance this
        key_words = ['important', 'key', 'main', 'primary', 'significant', 'crucial']
        
        for word in key_words:
            text = re.sub(f'\\b{word}\\b', f'**{word}**', text, flags=re.IGNORECASE)
        
        return text
    
    def extract_action_items(self, text: str) -> str:
        """Extract action items from summary"""
        # Simple implementation - look for action verbs
        action_patterns = [
            r'[Nn]eed to \w+',
            r'[Ss]hould \w+',
            r'[Ww]ill \w+',
            r'[Mm]ust \w+',
            r'[Pp]lan to \w+'
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, text)
            actions.extend(matches)
        
        if actions:
            return f"**Action Items:**\n" + "\n".join([f"• {action}" for action in actions])
        
        return text
    
    def extract_decisions(self, text: str) -> str:
        """Extract decisions from summary"""
        # Simple implementation - look for decision indicators
        decision_patterns = [
            r'[Dd]ecided to \w+',
            r'[Aa]greed to \w+',
            r'[Cc]hose to \w+',
            r'[Rr]esolved to \w+'
        ]
        
        decisions = []
        for pattern in decision_patterns:
            matches = re.findall(pattern, text)
            decisions.extend(matches)
        
        if decisions:
            return f"**Decisions Made:**\n" + "\n".join([f"• {decision}" for decision in decisions])
        
        return text
    
    def get_model_info(self) -> dict:
        """Get information about the current model"""
        return {
            'model_name': self.model_name,
            'model_loaded': self.summarizer is not None,
            'max_input_length': self.max_input_length,
            'device': 'cuda' if torch.cuda.is_available() else 'cpu'
        }