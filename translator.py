import streamlit as st
from deep_translator import GoogleTranslator
from docx import Document
import PyPDF2
from PIL import Image
import pytesseract

# Page Configuration
st.set_page_config(page_title="Universal Doc & Image Translator", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #6200EA;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to read text from PDF
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

# Function to read text from DOCX
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

# Function to read text from Image (OCR)
def read_image(file):
    try:
        image = Image.open(file)
        # Extract text using Tesseract OCR
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error reading Image: {e}")
        return None

# App UI
st.title("📸 Universal Doc & Image Translator")
st.markdown("### Upload a Document or Image to translate")

# Sidebar for language selection
with st.sidebar:
    st.header("Settings")
    lang_options = {
        'Bangla': 'bn',
        'English': 'en',
        'Spanish': 'es',
        'Hindi': 'hi',
        'Arabic': 'ar',
        'French': 'fr',
        'Russian': 'ru',
        'German': 'de',
        'Japanese': 'ja'
    }
    target_lang_name = st.selectbox('Select Target Language', list(lang_options.keys()))
    target_lang_code = lang_options[target_lang_name]

# File Uploader supports Images now
uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Display image preview if it's an image
    if uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    if st.button("Extract Text & Translate"):
        file_text = ""
        
        with st.spinner('Extracting text...'):
            # Detect file type and extract text
            if uploaded_file.name.endswith('.pdf'):
                file_text = read_pdf(uploaded_file)
            elif uploaded_file.name.endswith('.docx'):
                file_text = read_docx(uploaded_file)
            elif uploaded_file.name.endswith('.txt'):
                file_text = str(uploaded_file.read(), "utf-8")
            elif uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_text = read_image(uploaded_file)
        
        if file_text and file_text.strip():
            st.success("Text Extracted Successfully!")
            with st.expander("See Extracted Original Text"):
                st.text(file_text[:1000] + "..." if len(file_text) > 1000 else file_text)
            
            st.info(f"Translating to {target_lang_name}...")
            
            try:
                # Chunking logic
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
                
                st.success("Translation Complete! 🎉")
                
                # Show preview
                st.text_area("Translation Preview:", translated_full_text, height=300)
                
                # Download button
                st.download_button(
                    label="Download Translated Text (.txt)",
                    data=translated_full_text,
                    file_name=f"translated_{uploaded_file.name}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Translation failed: {e}")
        else:
            st.warning("Could not find any clear text in this file/image.")
