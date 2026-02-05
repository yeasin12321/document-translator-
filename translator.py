import streamlit as st
from deep_translator import GoogleTranslator
from docx import Document
import PyPDF2
from PIL import Image
import pytesseract
from gtts import gTTS
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

# 1. Page Configuration
st.set_page_config(page_title="Elite Translator", layout="centered", page_icon="💎")

# 2. LUXURY DESIGN CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    h1 {
        color: #FFD700 !important;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        text-shadow: 0px 4px 10px rgba(255, 215, 0, 0.3);
        font-weight: 700;
        margin-bottom: 10px;
    }
    h3 {
        color: #E0E0E0 !important;
        text-align: center;
        font-weight: 300;
        font-size: 1.2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #D4AF37 0%, #C5A028 100%);
        color: #000000;
        border: none;
        padding: 12px 20px;
        text-transform: uppercase;
        font-weight: bold;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
        transition: all 0.3s ease;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.6);
        background: linear-gradient(90deg, #F1D06E 0%, #D4AF37 100%);
        color: #000000;
    }
    .stFileUploader {
        border: 2px dashed #D4AF37;
        border-radius: 10px;
        padding: 20px;
        background-color: rgba(0, 0, 0, 0.2);
    }
    .stTextArea>div>div>textarea {
        background-color: #1E212B;
        color: #ffffff;
        border: 1px solid #D4AF37;
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] {
        background-color: #0b0c10;
        border-right: 1px solid #333;
    }
    /* অডিও প্লেয়ার ডিজাইন */
    .stAudio {
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Helper Functions
def read_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            extract = page.extract_text()
            if extract:
                text += extract + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def read_docx(file):
    try:
        doc = Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return None

def read_image(file):
    try:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error reading Image: {e}")
        return None

# PDF Generator Function
def create_pdf(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Font setup (Standard Helvetica)
    c.setFont("Helvetica", 12)
    
    # Text wrapping logic
    margin = 40
    text_width = width - 2 * margin
    y_position = height - margin
    
    # Wrap text manually
    lines = []
    for paragraph in text.split('\n'):
        lines.extend(textwrap.wrap(paragraph, width=90)) # Adjust width based on font size
    
    for line in lines:
        if y_position < margin: # New page if out of space
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - margin
        
        # Note: Standard PDF libraries struggle with Bangla unicode without custom fonts
        try:
            c.drawString(margin, y_position, line)
        except:
            c.drawString(margin, y_position, "Error: Character not supported in PDF mode")
        y_position -= 15 # Line spacing
        
    c.save()
    buffer.seek(0)
    return buffer

# 4. App Interface
st.title("💎 Premium Doc Translator")
st.markdown("### Transform your documents with AI-powered translation")
st.write("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    lang_options = {
        'Bangla': 'bn',
        'English': 'en',
        'Spanish': 'es',
        'Hindi': 'hi',
        'Arabic': 'ar',
        'French': 'fr',
        'Russian': 'ru',
        'German': 'de',
        'Japanese': 'ja',
        'Italian': 'it',
        'Korean': 'ko'
    }
    target_lang_name = st.selectbox('Select Target Language', list(lang_options.keys()))
    target_lang_code = lang_options[target_lang_name]
    st.markdown("---")
    st.info("💡 Supports: PDF, DOCX, TXT, Images")

# Main Content
uploaded_file = st.file_uploader("Upload File", type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    if uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    else:
        st.success(f"📂 File Uploaded: {uploaded_file.name}")

    st.write("") 
    
    if st.button("✨ Translate Document Now"):
        file_text = ""
        
        with st.spinner('Processing & Translating...'):
            if uploaded_file.name.endswith('.pdf'):
                file_text = read_pdf(uploaded_file)
            elif uploaded_file.name.endswith('.docx'):
                file_text = read_docx(uploaded_file)
            elif uploaded_file.name.endswith('.txt'):
                file_text = str(uploaded_file.read(), "utf-8")
            elif uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_text = read_image(uploaded_file)
        
        if file_text and file_text.strip():
            try:
                # Translation Chunking
                chunk_size = 4000
                chunks = [file_text[i:i+chunk_size] for i in range(0, len(file_text), chunk_size)]
                
                translated_full_text = ""
                progress_bar = st.progress(0)
                
                translator = GoogleTranslator(source='auto', target=target_lang_code)

                for idx, chunk in enumerate(chunks):
                    translated_part = translator.translate(chunk)
                    if translated_part:
                        translated_full_text += translated_part + " "
                    progress_bar.progress((idx + 1) / len(chunks))
                
                # --- RESULT SECTION ---
                st.success("Translation Complete! 🎉")
                
                # 1. Text Preview
                st.markdown("### ✅ Translated Text")
                st.text_area("", translated_full_text, height=250)
                
                # 2. Audio Player Feature
                st.markdown("### 🔊 Listen to Translation")
                try:
                    tts = gTTS(text=translated_full_text, lang=target_lang_code, slow=False)
                    audio_buffer = BytesIO()
                    tts.write_to_fp(audio_buffer)
                    st.audio(audio_buffer, format='audio/mp3')
                except Exception as e:
                    st.warning("Audio not available for this length or language.")

                # 3. Download Options (TXT & PDF)
                st.markdown("### ⬇️ Download Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📄 Download as .TXT",
                        data=translated_full_text,
                        file_name=f"translated_{uploaded_file.name}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    # PDF only works well for English/Latin scripts
                    if target_lang_code in ['en', 'es', 'fr', 'de', 'it']:
                        pdf_data = create_pdf(translated_full_text)
                        st.download_button(
                            label="📑 Download as .PDF",
                            data=pdf_data,
                            file_name=f"translated_{uploaded_file.name}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.warning("⚠️ PDF Download is available for English/Latin languages only (to avoid font errors). Please use TXT for Bangla/Hindi.")
                
            except Exception as e:
                st.error(f"Translation failed: {e}")
        else:
            st.warning("Could not extract text. Please try a clearer file.")
