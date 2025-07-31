import streamlit as st
import os
import tempfile
from pathlib import Path
from utils.audio_processor import AudioProcessor
from utils.transcription import WhisperTranscriber
from utils.summarizer import HuggingFaceSummarizer
from utils.pdf_generator import PDFGenerator
import time
from st_audiorec import st_audiorec

# Page config
st.set_page_config(
    page_title="ai Voice Summarizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'transcription' not in st.session_state:
    st.session_state.transcription = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None

# Initialize components
@st.cache_resource
def load_components():
    audio_processor = AudioProcessor()
    transcriber = WhisperTranscriber()
    summarizer = HuggingFaceSummarizer()
    pdf_generator = PDFGenerator()
    return audio_processor, transcriber, summarizer, pdf_generator

audio_processor, transcriber, summarizer, pdf_generator = load_components()

# Main app
def main():
    st.title("🎙️ AI Voice Summarizer")
    st.markdown("Record or upload audio to get AI-powered summaries as downloadable PDFs")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        
        # Summary settings
        st.subheader("Summary Options")
        summary_length = st.selectbox(
            "Summary Length",
            ["Short (1-2 sentences)", "Medium (3-5 sentences)", "Long (6+ sentences)"],
            index=1
        )
        
        summary_style = st.selectbox(
            "Summary Style",
            ["Bullet Points", "Paragraph", "Executive Summary"],
            index=1
        )
        
        focus_area = st.selectbox(
            "Focus Area",
            ["General", "Key Points", "Action Items", "Decisions Made"],
            index=0
        )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Audio Input")
        
        # Audio input tabs
        tab1, tab2 = st.tabs(["Record Audio", "Upload File"])
        
        with tab1:
    st.subheader("Record Audio")
    
    try:
        audio_bytes = st_audiorec()
        
        if audio_bytes is not None:
            st.audio(audio_bytes, format='audio/wav')

            # Save audio to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_bytes)
                st.session_state.audio_file = tmp_file.name

            st.success("Audio recorded successfully!")
        else:
            st.info("Click the mic to record your voice.")
    
    except ImportError:
        st.error("Audio recorder not available. Please install it with: `pip install streamlit-audiorec`")
        st.info("For now, please use the file upload option.")

        
        with tab2:
            st.subheader("Upload Audio File")
            
            uploaded_file = st.file_uploader(
                "Choose an audio file",
                type=['wav', 'mp3', 'm4a', 'flac', 'ogg', 'aac', 'wma'],
                help="Supported formats: WAV, MP3, M4A, FLAC, OGG, AAC, WMA"
            )
            
            if uploaded_file is not None:
                # Save uploaded file to temp directory
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    st.session_state.audio_file = tmp_file.name
                
                st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    with col2:
        st.header("🔄 Processing")
        
        if st.session_state.audio_file:
            # Process audio button
            if st.button("Process Audio", type="primary", use_container_width=True):
                try:
                    # Step 1: Process audio
                    with st.spinner("Processing audio file..."):
                        processed_audio = audio_processor.process_audio(st.session_state.audio_file)
                        st.success("Audio processed")
                    
                    # Step 2: Transcribe
                    with st.spinner("Transcribing audio..."):
                        transcription = transcriber.transcribe(processed_audio)
                        st.session_state.transcription = transcription
                        st.success("Transcription complete")
                    
                    # Step 3: Summarize
                    with st.spinner("Generating summary..."):
                        summary_config = {
                            'length': summary_length,
                            'style': summary_style,
                            'focus': focus_area
                        }
                        summary = summarizer.summarize(transcription, summary_config)
                        st.session_state.summary = summary
                        st.success("Summary generated")
                    
                except Exception as e:
                    st.error(f"Error processing audio: {str(e)}")
        else:
            st.info("Please record or upload an audio file to begin processing.")
    
    # Results section
    if st.session_state.transcription or st.session_state.summary:
        st.header("📄 Results")
        
        result_col1, result_col2 = st.columns([1, 1])
        
        with result_col1:
            st.subheader("Transcription")
            if st.session_state.transcription:
                st.text_area(
                    "Raw Transcription",
                    st.session_state.transcription,
                    height=200,
                    key="transcription_display"
                )
            else:
                st.info("Transcription will appear here after processing.")
        
        with result_col2:
            st.subheader("Summary")
            if st.session_state.summary:
                st.text_area(
                    "Generated Summary",
                    st.session_state.summary,
                    height=200,
                    key="summary_display"
                )
                
                # PDF Generation section
                st.subheader("📋 Export Options")
                
                col_pdf1, col_pdf2 = st.columns([1, 1])
                
                with col_pdf1:
                    if st.button("Generate PDF", type="secondary", use_container_width=True):
                        try:
                            with st.spinner("Generating PDF..."):
                                pdf_path = pdf_generator.create_pdf(
                                    transcription=st.session_state.transcription,
                                    summary=st.session_state.summary,
                                    settings={
                                        'length': summary_length,
                                        'style': summary_style,
                                        'focus': focus_area
                                    }
                                )
                                st.success("PDF generated successfully!")
                                
                                # Provide download button
                                with open(pdf_path, "rb") as pdf_file:
                                    st.download_button(
                                        label="📥 Download PDF",
                                        data=pdf_file.read(),
                                        file_name=f"voice_summary_{int(time.time())}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                        except Exception as e:
                            st.error(f"Error generating PDF: {str(e)}")
                
                with col_pdf2:
                    if st.button("Clear All", type="secondary", use_container_width=True):
                        st.session_state.transcription = ""
                        st.session_state.summary = ""
                        st.session_state.audio_file = None
                        st.rerun()
            else:
                st.info("Summary will appear here after processing.")

if __name__ == "__main__":
    main()