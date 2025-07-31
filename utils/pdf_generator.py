import os
import streamlit as st
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import textwrap

class PDFGenerator:
    def __init__(self):
        """Initialize PDF generator"""
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up styles
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.darkblue
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20
        )
        
        # Metadata style
        self.meta_style = ParagraphStyle(
            'CustomMeta',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=colors.grey
        )
    
    def create_pdf(self, transcription: str, summary: str, settings: dict) -> str:
        """
        Create a PDF document with transcription and summary
        
        Args:
            transcription: The original transcription text
            summary: The generated summary
            settings: Dictionary with summary settings
        
        Returns:
            Path to the generated PDF file
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_summary_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Add title
            story.append(Paragraph("Voice Recording Summary", self.title_style))
            story.append(Spacer(1, 12))
            
            # Add metadata
            story.extend(self.create_metadata_section(settings))
            story.append(Spacer(1, 20))
            
            # Add summary section
            story.extend(self.create_summary_section(summary))
            story.append(Spacer(1, 20))
            
            # Add transcription section
            story.extend(self.create_transcription_section(transcription))
            
            # Add footer
            story.append(Spacer(1, 30))
            story.extend(self.create_footer())
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            st.error(f"Error creating PDF: {str(e)}")
            raise e
    
    def create_metadata_section(self, settings: dict) -> list:
        """Create metadata section for PDF"""
        story = []
        
        # Create metadata table
        metadata = [
            ['Generated:', datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ['Summary Length:', settings.get('length', 'Medium')],
            ['Summary Style:', settings.get('style', 'Paragraph')],
            ['Focus Area:', settings.get('focus', 'General')]
        ]
        
        # Create table
        table = Table(metadata, colWidths=[1.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        return story
    
    def create_summary_section(self, summary: str) -> list:
        """Create summary section for PDF"""
        story = []
        
        # Add section title
        story.append(Paragraph("Summary", self.subtitle_style))
        story.append(Spacer(1, 12))
        
        # Process summary text
        if summary:
            # Handle bullet points
            if summary.startswith('•') or '\n•' in summary:
                # Split by bullet points
                lines = summary.split('\n')
                for line in lines:
                    if line.strip():
                        # Clean up bullet formatting
                        clean_line = line.strip()
                        if clean_line.startswith('•'):
                            clean_line = clean_line[1:].strip()
                        
                        # Add bullet point
                        bullet_text = f"• {clean_line}"
                        story.append(Paragraph(bullet_text, self.body_style))
            else:
                # Regular paragraph text
                # Split into paragraphs
                paragraphs = summary.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        # Handle bold text
                        formatted_para = self.format_text(para.strip())
                        story.append(Paragraph(formatted_para, self.body_style))
                        story.append(Spacer(1, 6))
        else:
            story.append(Paragraph("No summary available.", self.body_style))
        
        return story
    
    def create_transcription_section(self, transcription: str) -> list:
        """Create transcription section for PDF"""
        story = []
        
        # Add section title
        story.append(Paragraph("Full Transcription", self.subtitle_style))
        story.append(Spacer(1, 12))
        
        # Process transcription text
        if transcription:
            # Split long transcription into manageable chunks
            max_chars_per_para = 1000
            if len(transcription) > max_chars_per_para:
                # Split by sentences to maintain readability
                sentences = transcription.split('. ')
                current_para = ""
                
                for sentence in sentences:
                    if len(current_para + sentence) < max_chars_per_para:
                        current_para += sentence + ". "
                    else:
                        if current_para:
                            story.append(Paragraph(current_para.strip(), self.body_style))
                            story.append(Spacer(1, 6))
                        current_para = sentence + ". "
                
                # Add remaining text
                if current_para:
                    story.append(Paragraph(current_para.strip(), self.body_style))
            else:
                # Add as single paragraph
                story.append(Paragraph(transcription, self.body_style))
        else:
            story.append(Paragraph("No transcription available.", self.body_style))
        
        return story
    
    def create_footer(self) -> list:
        """Create footer section"""
        story = []
        
        # Add separator line
        story.append(Spacer(1, 20))
        
        # Add footer text
        footer_text = "Generated by Voice Summarizer App"
        story.append(Paragraph(footer_text, self.meta_style))
        
        return story
    
    def format_text(self, text: str) -> str:
        """
        Format text for PDF (handle bold, etc.)
        
        Args:
            text: Input text
        
        Returns:
            Formatted text with reportlab markup
        """
        # Convert markdown-style bold to reportlab bold
        text = text.replace('**', '<b>').replace('**', '</b>')
        
        # Ensure proper closing tags
        if text.count('<b>') > text.count('</b>'):
            text += '</b>'
        
        return text
    
    def create_advanced_pdf(self, transcription: str, summary: str, settings: dict, 
                          audio_info: dict = None) -> str:
        """
        Create an advanced PDF with additional features
        
        Args:
            transcription: The original transcription text
            summary: The generated summary
            settings: Dictionary with summary settings
            audio_info: Optional audio file information
        
        Returns:
            Path to the generated PDF file
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_summary_advanced_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Add title page
            story.extend(self.create_title_page(settings, audio_info))
            
            # Add page break
            story.append(Spacer(1, 100))
            
            # Add summary section
            story.extend(self.create_summary_section(summary))
            story.append(Spacer(1, 30))
            
            # Add transcription section
            story.extend(self.create_transcription_section(transcription))
            
            # Add footer
            story.extend(self.create_footer())
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            st.error(f"Error creating advanced PDF: {str(e)}")
            raise e
    
    def create_title_page(self, settings: dict, audio_info: dict = None) -> list:
        """Create a title page with comprehensive information"""
        story = []
        
        # Main title
        story.append(Paragraph("Voice Recording Analysis", self.title_style))
        story.append(Spacer(1, 30))
        
        # Document info
        doc_info = [
            ['Document Type:', 'Voice Recording Summary'],
            ['Generated:', datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ['Summary Configuration:', ''],
            ['• Length:', settings.get('length', 'Medium')],
            ['• Style:', settings.get('style', 'Paragraph')],
            ['• Focus:', settings.get('focus', 'General')]
        ]
        
        # Add audio info if available
        if audio_info:
            doc_info.extend([
                ['Audio Information:', ''],
                ['• Duration:', f"{audio_info.get('duration', 'N/A')} seconds"],
                ['• Format:', audio_info.get('format', 'N/A')],
                ['• Sample Rate:', f"{audio_info.get('frame_rate', 'N/A')} Hz"],
                ['• Channels:', str(audio_info.get('channels', 'N/A'))],
                ['• File Size:', f"{audio_info.get('file_size', 'N/A'):.2f} MB"]
            ])
        
        # Create table
        table = Table(doc_info, colWidths=[2*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        return story
    
    def cleanup_old_files(self, days_old: int = 7):
        """
        Clean up old PDF files
        
        Args:
            days_old: Files older than this many days will be deleted
        """
        try:
            import time
            current_time = time.time()
            
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                if os.path.isfile(file_path) and filename.endswith('.pdf'):
                    file_age = current_time - os.path.getctime(file_path)
                    if file_age > (days_old * 24 * 60 * 60):  # Convert days to seconds
                        os.remove(file_path)
                        
        except Exception as e:
            st.warning(f"Could not clean up old files: {str(e)}")
    
    def get_output_files(self) -> list:
        """Get list of generated PDF files"""
        try:
            files = []
            for filename in os.listdir(self.output_dir):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(self.output_dir, filename)
                    file_info = {
                        'name': filename,
                        'path': filepath,
                        'size': os.path.getsize(filepath),
                        'created': datetime.fromtimestamp(os.path.getctime(filepath))
                    }
                    files.append(file_info)
            
            # Sort by creation time (newest first)
            files.sort(key=lambda x: x['created'], reverse=True)
            return files
            
        except Exception as e:
            st.warning(f"Could not get output files: {str(e)}")
            return []