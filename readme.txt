# Voice Summarizer App

A Streamlit application that converts voice recordings to text using OpenAI Whisper and generates AI-powered summaries using HuggingFace transformers, with PDF export functionality.

## Features

- 🎤 **Voice Recording**: Record audio directly in the browser
- 📁 **File Upload**: Support for multiple audio formats (WAV, MP3, M4A, FLAC, OGG, AAC, WMA)
- 🔤 **Speech-to-Text**: Local transcription using OpenAI Whisper (free)
- 🤖 **AI Summarization**: Intelligent summaries using HuggingFace transformers
- 📋 **PDF Export**: Generate professional PDF reports
- ⚙️ **Customizable**: Adjustable summary length, style, and focus areas

## Installation

### 1. Create Conda Environment

```bash
# Create new conda environment
conda create -n voice-summarizer python=3.9

# Activate environment
conda activate voice-summarizer
```

### 2. Install Dependencies

```bash
# Install core packages via conda
conda install streamlit pandas numpy

# Install remaining packages via pip
pip install -r requirements.txt
```

### 3. Install FFmpeg (Required for audio processing)

**Windows:**
- Download FFmpeg from https://ffmpeg.org/download.html
- Add FFmpeg to your system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 4. Create Project Structure

```
voice-summarizer/
├── app.py
├── requirements.txt
├── utils/
│   ├── __init__.py
│   ├── audio_processor.py
│   ├── transcription.py
│   ├── summarizer.py
│   └── pdf_generator.py
├── temp/
└── outputs/
```

## Usage

### 1. Start the Application

```bash
streamlit run app.py
```

### 2. Use the App

1. **Record Audio**: Click the microphone button to record directly in the browser
2. **Or Upload File**: Upload an audio file in supported formats
3. **Configure Settings**: Choose summary length, style, and focus area in the sidebar
4. **Process**: Click "Process Audio" to transcribe and summarize
5. **Export**: Generate and download a PDF report

## Configuration Options

### Summary Length
- **Short**: 1-2 sentences
- **Medium**: 3-5 sentences  
- **Long**: 6+ sentences

### Summary Style
- **Paragraph**: Standard paragraph format
- **Bullet Points**: Organized bullet list
- **Executive Summary**: Business-style summary

### Focus Areas
- **General**: Overall content summary
- **Key Points**: Emphasizes important information
- **Action Items**: Extracts actionable tasks
- **Decisions Made**: Highlights decisions and conclusions

## Technical Details

### Audio Processing
- Supports multiple formats via pydub
- Auto-normalization and noise reduction
- Converts to 16kHz WAV for optimal Whisper performance

### Transcription
- Uses OpenAI Whisper (runs locally, no API costs)
- Automatic language detection
- High accuracy for various accents and audio qualities

### Summarization
- HuggingFace BART model (facebook/bart-large-cnn)
- Handles long texts via intelligent chunking
- Customizable output based on user preferences

### PDF Generation
- Professional formatting with ReportLab
- Includes metadata and timestamps
- Supports various text formatting options

## Troubleshooting

### Common Issues

1. **Audio Recording Not Working**
   - Install: `pip install streamlit-audio-recorder`
   - Check browser permissions for microphone access

2. **FFmpeg Not Found**
   - Ensure FFmpeg is installed and in PATH
   - Restart terminal/command prompt after installation

3. **Model Loading Errors**
   - First run downloads models (may take time)
   - Ensure stable internet connection
   - Check available disk space (models ~1-2GB)

4. **Memory Issues**
   - Reduce audio file size
   - Use smaller Whisper model (change in transcription.py)
   - Close other applications to free RAM

### Performance Tips

1. **Audio Quality**
   - Use clear, noise-free recordings
   - Speak at moderate pace
   - Avoid background noise

2. **Processing Speed**
   - Shorter audio files process faster
   - GPU acceleration available for compatible systems
   - Consider chunking very long recordings

3. **Resource Usage**
   - First run downloads models (one-time)
   - Subsequent runs use cached models
   - Clear temp files periodically

## File Structure Details

```
voice-summarizer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── utils/                 # Utility modules
│   ├── __init__.py       # Package initialization
│   ├── audio_processor.py # Audio handling and processing
│   ├── transcription.py   # Whisper transcription
│   ├── summarizer.py      # HuggingFace summarization
│   └── pdf_generator.py   # PDF creation
├── temp/                  # Temporary audio files
└── outputs/               # Generated PDF reports
```

## Dependencies

- **streamlit**: Web interface
- **openai-whisper**: Speech-to-text
- **transformers**: AI summarization
- **pydub**: Audio processing
- **reportlab**: PDF generation
- **torch**: Deep learning framework
- **streamlit-audio-recorder**: Browser audio recording

## License

This project is for educational and personal use. Please respect the licenses of the underlying models and libraries used.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure FFmpeg is properly configured
4. Check that your Python environment is activated