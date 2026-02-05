import streamlit as st
from deep_translator import GoogleTranslator
from docx import Document
import PyPDF2
from PIL import Image
import pytesseract

# 1. Page Configuration (Title and Icon)
st.set_page_config(page_title="Yeasin Elite Translator", layout="centered", page_icon="💎")

# 2. LUXURY DESIGN CSS (Custom Styling)
st.markdown("""
    <style>
    /* মেইন ব্যাকগ্রাউন্ড - প্রিমিয়াম গ্রেডিয়েন্ট */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    
    /* টাইটেল ডিজাইন (গোল্ডেন ইফেক্ট) */
    h1 {
        color: #FFD700 !important;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        text-shadow: 0px 4px 10px rgba(255, 215, 0, 0.3);
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    /* সাব-হেডার ডিজাইন */
    h3 {
        color: #E0E0E0 !important;
        text-align: center;
        font-weight: 300;
        font-size: 1.2rem;
    }
    
    /* বাটন ডিজাইন (গোল্ডেন গ্রেডিয়েন্ট) */
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
    
    /* ফাইল আপলোডার বক্স ডিজাইন */
    .stFileUploader {
        border: 2px dashed #D4AF37;
        border-radius: 10px;
        padding: 20px;
        background-color: rgba(0, 0, 0, 0.2);
    }
    
    /* টেক্সট এরিয়া (ইনপুট/আউটপুট বক্স) */
    .stTextArea>div>div>textarea {
        background-color: #1E212B;
        color: #ffffff;
        border: 1px solid #D4AF37;
        border-radius: 8px;
    }
    
    /* সাইডবার ডিজাইন */
    section[data-testid="stSidebar"] {
        background-color: #0b0c10;
        border-right: 1px solid #333;
    }
    
    /* ডাউনলোড বাটন স্পেশাল ইফেক্ট */
    .stDownloadButton>button {
        background: transparent;
        border: 2px solid #FFD700;
        color: #FFD700;
    }
    .stDownloadButton>button:hover {
        background: #FFD700;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Helper Functions (PDF, DOCX, IMAGE)
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

# 4. App Interface Logic
st.title("💎 Premium Doc Translator")
st.markdown("### Transform your documents with AI-powered translation")
st.write("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("Customize your translation preference.")
    
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
    # Show image preview if applicable
    if uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    else:
        st.success(f"📂 File Uploaded: {uploaded_file.name}")

    st.write("") # Spacer
    
    # Translate Button
    if st.button("✨ Translate Document Now"):
        file_text = ""
        
        with st.spinner('Processing & Translating... Please wait...'):
            # Text Extraction Logic
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
                # Translation Logic with Chunking
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
                
                # Success & Output
                st.success("Translation Complete! 🎉")
                st.markdown("### ✅ Translated Result")
                st.text_area("", translated_full_text, height=300)
                
                # Download Button
                st.download_button(
                    label="⬇️ Download Translation (.txt)",
                    data=translated_full_text,
                    file_name=f"translated_{uploaded_file.name}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Translation failed: {e}")
        else:
            st.warning("Could not extract text. Please try a clearer file.")
