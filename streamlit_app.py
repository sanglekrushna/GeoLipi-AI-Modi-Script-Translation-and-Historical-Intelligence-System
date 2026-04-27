import unicodedata
import streamlit as st
import torch
import json
import os
import cv2
import numpy as np
import base64
from PIL import Image
import pytesseract
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

import requests

from crnn_model import CRNN
from marathi_corrector import correct_text
from translator.modi_to_dev import convert_modi_to_devanagari
from utils.site_matcher import match_site
import pandas as pd
import random

# -----------------------------
# SETTINGS
# -----------------------------
st.set_page_config(page_title="Modi Script Translator", layout="wide")

# -----------------------------
# CUSTOM CSS FOR PREMIUM UI
# -----------------------------
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;700&family=Inter:wght@400;600&display=swap');

/* Main background */
.stApp {
    background-color: #0a0e17;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif !important;
}

/* Modi Script Font */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Modi&display=swap');
.modi-font {
    font-family: 'Noto Sans Modi', 'Inter', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #11151c;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Headers */
h1, h2, h3 {
    color: #c4a962 !important;
    font-family: 'Crimson Pro', serif !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    border: 1px solid rgba(196, 169, 98, 0.4);
    color: #c4a962;
    border-radius: 8px;
    transition: all 0.3s ease;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    background: rgba(196, 169, 98, 0.1);
    border: 1px solid #c4a962;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(196, 169, 98, 0.2);
    color: #ffd700;
}

/* Input fields */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background-color: rgba(255, 255, 255, 0.03);
    color: #e2e8f0;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color: rgba(196, 169, 98, 0.6);
    box-shadow: 0 0 8px rgba(196, 169, 98, 0.2);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
    background-color: transparent;
}
.stTabs [data-baseweb="tab"] {
    color: #e2e8f0;
    transition: all 0.2s ease;
    font-family: 'Inter', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background-color: rgba(196, 169, 98, 0.1) !important;
    color: #c4a962 !important;
    border-bottom: 2px solid #c4a962 !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------
# RESOURCE CACHING
# -----------------------------
@st.cache_resource
def _load_translation_model():
    model_name = "facebook/m2m100_418M"
    try:
        tokenizer = M2M100Tokenizer.from_pretrained(model_name)
        model = M2M100ForConditionalGeneration.from_pretrained(model_name)
        return tokenizer, model
    except Exception as e:
        st.error(f"Error loading translation model: {e}")
        return None, None

@st.cache_data
def load_known_sites():
    """Load known sites from modi_locations.json for accurate lookup."""
    try:
        with open('modi_locations.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

_GEMINI_KEY = "AIzaSyAj-OVfsDIEBcpwCPAqLwlUPzT3fF6ywwc"
_GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={_GEMINI_KEY}"

# -----------------------------
# CHARACTER MAPPINGS & FACTS
# -----------------------------
DEVANAGARI_TO_MODI = {
    'अ': '𑘀', 'आ': '𑘁', 'इ': '𑘂', 'ई': '𑘃', 'उ': '𑘄', 'ऊ': '𑘅',
    'ऋ': '𑘆', 'ॠ': '𑘇', 'ऌ': '𑘈', 'ॡ': '𑘉', 'ए': '𑘊', 'ऐ': '𑘋',
    'ओ': '𑘌', 'औ': '𑘍', 'ा': '𑘰', 'ि': '𑘱', 'ी': '𑘲', 'ु': '𑘳', 'ू': '𑘴', 
    'ृ': '𑘵', 'ॄ': '𑘶', 'ॢ': '𑘷', 'ॣ': '𑘸', 'े': '𑘹', 'ै': '𑘺', 'ो': '𑘻',
    'ौ': '𑘼', 'क': '𑘎', 'ख': '𑘏', 'ग': '𑘐', 'घ': '𑘑', 'ङ': '𑘒',
    'च': '𑘓', 'छ': '𑘔', 'ज': '𑘕', 'झ': '𑘖', 'ञ': '𑘗',
    'ट': '𑘘', 'ठ': '𑘙', 'ड': '𑘚', 'ढ': '𑘛', 'ण': '𑘜',
    'त': '𑘝', 'थ': '𑘞', 'द': '𑘟', 'ध': '𑘠', 'न': '𑘡',
    'प': '𑘢', 'फ': '𑘣', 'ब': '𑘤', 'भ': '𑘥', 'म': '𑘦',
    'य': '𑘧', 'र': '𑘨', 'ल': '𑘩', 'व': '𑘪',
    'श': '𑘫', 'ष': '𑘬', 'स': '𑘭', 'ह': '𑘮',
    'ं': '𑘽', 'ः': '𑘾', 'ँ': '𑙀', '्': '𑘿',
    '०': '𑙐', '१': '𑙑', '२': '𑙒', '३': '𑙓', '४': '𑙔',
    '५': '𑙕', '६': '𑙖', '७': '𑙗', '८': '𑙘', '९': '𑙙'
}

# Mapping Devanagari to dataset folder paths
DATASET_PATH_MAP = {
    'अ': 'vowels/a', 'आ': 'vowels/aa', 'इ': 'vowels/i', 'ई': 'vowels/ii', 
    'उ': 'vowels/u', 'ऊ': 'vowels/oo', 'ए': 'vowels/e', 'ऐ': 'vowels/ai', 
    'ओ': 'vowels/o', 'औ': 'vowels/ou', 'ं': 'vowels/am', 'ः': 'vowels/ah',
    'क': 'consonants/k', 'ख': 'consonants/kh', 'ग': 'consonants/g', 'घ': 'consonants/gh',
    'च': 'consonants/ch', 'छ': 'consonants/chh', 'ज': 'consonants/ja', 'झ': 'consonants/jh',
    'ट': 'consonants/ta', 'ठ': 'consonants/th', 'ड': 'consonants/d', 'ढ': 'consonants/dh',
    'ण': 'consonants/nn', 'त': 'consonants/tha', 'थ': 'consonants/thh', 'द': 'consonants/dha',
    'ध': 'consonants/thha', 'न': 'consonants/n', 'प': 'consonants/p', 'फ': 'consonants/ph',
    'ब': 'consonants/b', 'भ': 'consonants/bh', 'म': 'consonants/m', 'य': 'consonants/y',
    'र': 'consonants/r', 'ल': 'consonants/l', 'व': 'consonants/v', 'श': 'consonants/sh',
    'ष': 'consonants/s', 'स': 'consonants/s', 'ह': 'consonants/h', 'ळ': 'consonants/lh',
    '०': 'digits/zero', '१': 'digits/one', '२': 'digits/two', '३': 'digits/three',
    '४': 'digits/four', '५': 'digits/five', '६': 'digits/six', '७': 'digits/seven',
    '८': 'digits/eight', '९': 'digits/nine'
}

def get_random_archival_image(char):
    """Retrieve a random image path from the archival dataset for a given character."""
    base_dir = "data/MODI_HChar"
    sub_path = DATASET_PATH_MAP.get(char)
    if not sub_path:
        return None
    
    full_path = os.path.join(base_dir, sub_path)
    if os.path.exists(full_path):
        images = [f for f in os.listdir(full_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if images:
            return os.path.join(full_path, random.choice(images))
    return None

MODI_FACTS = [
    "Modi Lipi originated in the 12th century and is primarily used for writing Marathi.",
    "It was developed by the Maharashtrian community to simplify the writing of Marathi.",
    "Modi Lipi was the official script of the Maratha Empire for administrative purposes.",
    "The word 'Modi' in the script's name is thought to mean 'to fold' or 'to break'.",
    "Modi is an abugida, meaning each character represents a consonant with an inherent vowel.",
    "The script was designed to be written continuously without lifting the pen, which contributed to its speed.",
    "Shivaji Maharaj's administration adopted Modi Lipi to simplify official Marathi documentation.",
    "The British government initially used Modi Lipi in official documents before phasing it out."
]

def lookup_known_site(modi_text):
    """Exact-match the input against the known sites database."""
    sites = load_known_sites()
    clean = modi_text.strip()
    for site in sites:
        if site.get('modi_text', '').strip() == clean:
            return site
    return None

def get_gemini_interpretation(devanagari, description=None):
    """Use Gemini to generate a rich historical interpretation."""
    try:
        if description:
            prompt = (
                f"Translate the following Marathi Devanagari text to English: '{devanagari}'. "
                f"Historical Context: {description}. "
                f"Provide a direct, accurate translation first, followed by a very brief (1 sentence) historical significance. "
                f"Output format: 'Translation: [Direct Translation]. Significance: [Context]'."
            )
        else:
            prompt = (
                f"Translate the following Marathi Devanagari text to English: '{devanagari}'. "
                f"If it is a single word, give its primary meaning. If it is a sentence, translate it accurately. "
                f"Strictly prioritize historical accuracy. Do not provide literal translations for names (e.g., 'Shivaji Maharaj' must remain as such, never 'Shiva Majesty'). Focus on the Maratha Empire context."
            )
        resp = requests.post(
            _GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if 'candidates' in data:
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception:
        pass
    return None

@st.cache_resource
def load_crnn_bundle():
    """Load Custom CRNN model and vocab."""
    vocab_path = "best_vocab.json"
    ckpt_path = "best_model.pth"
    
    if not os.path.exists(vocab_path) or not os.path.exists(ckpt_path):
        return None, None
        
    with open(vocab_path, encoding='utf-8') as f:
        vocab_data = json.load(f)
    
    # vocab_data is likely a list of chars
    vocab_size = len(vocab_data) + 1 # +1 for blank
    model = CRNN(vocab_size=vocab_size)
    model.load_state_dict(torch.load(ckpt_path, map_location='cpu'))
    model.eval()
    
    return model, vocab_data

# -----------------------------
# OCR HELPERS
# -----------------------------
def _ctc_decode_greedy(logits, vocab, blank_idx=0):
    pred_ids = torch.argmax(logits, dim=2)  # [T, B]
    seq = pred_ids[:, 0].tolist()
    out = []
    prev = None
    for idx in seq:
        if idx != prev and idx != blank_idx:
            # Map index to char
            if 0 < idx <= len(vocab):
                out.append(vocab[idx-1])
        prev = idx
    return "".join(out)

def run_hybrid_ocr(uploaded_file):
    """Router: Tesseract for printed, CRNN for handwritten."""
    pil_img = Image.open(uploaded_file)
    
    # 1. Try Tesseract (Marathi) first for printed reliability
    try:
        # Strictly follow the requested Tesseract config
        tess_text = pytesseract.image_to_string(
            pil_img, 
            lang='mar', 
            config='--oem 3 --psm 6'
        )
        if len(tess_text.strip()) > 5:
            return {"text": tess_text.strip(), "confidence": 0.85, "engine": "Tesseract"}
    except:
        pass
        
    # 2. Fallback to Custom CRNN
    model, vocab = load_crnn_bundle()
    if model is None:
        return {"text": "? Model files missing", "confidence": 0.0, "engine": "None"}
        
    # Preprocess
    img = np.array(pil_img.convert('L'))
    h, w = img.shape
    new_w = int(64 * (w / h))
    new_w = min(new_w, 1024)
    img_resized = cv2.resize(img, (new_w, 64))
    
    # Pad
    padded = np.ones((64, 1024), dtype=np.uint8) * 255
    padded[:, :new_w] = img_resized
    
    tensor = torch.from_numpy(padded).float().unsqueeze(0).unsqueeze(0) / 255.0
    
    with torch.no_grad():
        logits = model(tensor)
        text = _ctc_decode_greedy(logits, vocab)
        
    return {"text": text, "confidence": 0.45, "engine": "CRNN (Experimental)"}

# -----------------------------
# MAIN UI
# -----------------------------
st.markdown("""
<div style='margin-bottom:8px;'>
    <h1 style='color:#c4a962;font-family:Georgia,serif;font-size:2rem;margin-bottom:2px;'>
        Modi Lipi Intelligence
    </h1>
    <p style='color:#7a8fa6;font-size:0.85rem;margin-top:0;'>
        Premium Historical Script Discovery &amp; Visual AI Pipeline
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["\u270f\ufe0f Script Interpretation", "\U0001f4f7 Visual Recognition (OCR)"])

with tab1:
    # Header row

    # --- Session State Initialization ---
    if 'dev_out' not in st.session_state: st.session_state['dev_out'] = ""
    if 'eng_out' not in st.session_state: st.session_state['eng_out'] = ""

    def run_interpretation():
        raw = st.session_state.get('modi_input_box', '').strip()
        if not raw:
            return
            
        # -- Step 1: Devanagari Conversion --
        devanagari = convert_modi_to_devanagari(raw)
        
        # -- Step 2: High-Precision Translation --
        english = ""
        engine_used = ""
        m2m_success = False
        
        # Robust Historical Mapping (for common terms)
        HISTORICAL_MAP = {
            "स्वराज्य": "Self-rule / Independence",
            "किल्ला": "Fort / Fortress",
            "कील्ला": "Fort / Fortress",
            "गड": "Hill Fort",
            "राजा": "King / Monarch",
            "छत्रपती": "Emperor (Chhatrapati)",
            "शिवाजी महाराज": "Chhatrapati Shivaji Maharaj",
            "शिवाजी": "Shivaji",
            "महाराज": "Majesty / King",
            "पुणे": "Pune (Historical Capital)",
            "महाराष्ट्र": "Maharashtra"
        }
        
        # A. Try Historical Map first (with Normalization fix)
        clean_dev = unicodedata.normalize('NFC', devanagari.strip())
        
        # Exact match or substring match for safety
        found_key = None
        for key in HISTORICAL_MAP:
            if unicodedata.normalize('NFC', key) == clean_dev:
                found_key = key
                break
        
        if found_key:
            english = HISTORICAL_MAP[found_key]
            engine_used = "Historical Dictionary"
            m2m_success = True
            english = HISTORICAL_MAP[devanagari]
            engine_used = "Historical Dictionary"
            m2m_success = True
        
        # B. Try M2M100 (Deep Learning Translator)
        if not m2m_success:
            try:
                tokenizer, t_model = _load_translation_model()
                if tokenizer and t_model:
                    tokenizer.src_lang = "mr"
                    enc = tokenizer(devanagari, return_tensors="pt")
                    gen = t_model.generate(**enc, forced_bos_token_id=tokenizer.get_lang_id("en"))
                    english = tokenizer.batch_decode(gen, skip_special_tokens=True)[0].strip()
                    if len(english) > 2:
                        engine_used = "M2M100 Neural Engine"
                        m2m_success = True
            except Exception:
                pass
        
        # C. Fallback to Gemini AI (Historical Expert)
        if not m2m_success or len(english) < 3:
            gemini_res = get_gemini_interpretation(devanagari)
            if gemini_res:
                english = gemini_res
                engine_used = "Gemini AI (Historical Expert)"
                m2m_success = True
            else:
                if not english: english = "[Translation unavailable]"

        # Update session state for UI display
        st.session_state['dev_out'] = devanagari
        st.session_state['eng_out'] = english
        st.session_state['engine_info'] = engine_used
        st.session_state['final_dev_box'] = devanagari
        st.session_state['final_eng_box'] = english

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Source Inscription")
        modi_input = st.text_area(
            label="", height=180,
            placeholder="Paste Modi Lipi Unicode characters here...",
            label_visibility="collapsed", key="modi_input_box"
        )
        with st.spinner("Analyzing Script..."):
            st.button("Generate Interpretation", on_click=run_interpretation)

    # --- UI Components ---
    with col2:
        st.markdown("### Processed Output")
        
        # Devanagari Transcription
        st.markdown("<div style='color:#7a8fa6; font-size:0.8rem; margin-bottom:4px;'>Devanagari Transcription</div>", unsafe_allow_html=True)
        st.text_area(
            "Devanagari Output",
            height=100,
            label_visibility="collapsed",
            key="final_dev_box"
        )
        
        # English Interpretation
        st.markdown("<div style='color:#7a8fa6; font-size:0.8rem; margin-bottom:4px; margin-top:12px;'>English Interpretation</div>", unsafe_allow_html=True)
        st.text_area(
            "English Output",
            height=140,
            label_visibility="collapsed",
            key="final_eng_box"
        )
        
        # Engine indicator for verification
        engine = st.session_state.get('engine_info', '')
        if engine:
            st.markdown(f"""
                <div style='background:rgba(196,169,98,0.1); border:1px solid rgba(196,169,98,0.2); 
                            border-radius:4px; padding:4px 8px; font-size:0.7rem; color:#c4a962; 
                            display:inline-block; margin-top:4px;'>
                    ⚙️ Engine: {engine}
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Interactive Character Explorer")
    
    st.markdown("""
        <style>
        .character-preview-card {
            background: linear-gradient(145deg, rgba(196,169,98,0.05), rgba(0,0,0,0.2));
            border: 1px solid rgba(196,169,98,0.2);
            border-radius: 16px;
            padding: 30px;
            margin: 20px 0;
            display: flex;
            justify-content: space-around;
            align-items: center;
            text-align: center;
        }
        .preview-box {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .preview-label {
            color: #7a8fa6;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }
        .preview-char {
            font-size: 5rem;
            color: #c4a962;
            line-height: 1;
        }
        .preview-divider {
            width: 1px;
            height: 80px;
            background: rgba(196,169,98,0.2);
        }
        .explorer-controls {
            background: rgba(255,255,255,0.02);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

    # State for selection
    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
        selected_char = st.selectbox(
            "Select Devanagari Character", 
            list(DEVANAGARI_TO_MODI.keys()), 
            index=0,
            key="source_select"
        )
        st.markdown("""
            <div style='font-size:0.85rem; color:#7a8fa6; margin-top:10px;'>
                Select a character from the Devanagari script to see its historical Modi Lipi equivalent.
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # Premium 3-Column Intelligence Card
        modi_char = DEVANAGARI_TO_MODI.get(selected_char, "")
        archival_img = get_random_archival_image(selected_char)
        
        img_html = "<span style='color:#ccc; font-size:0.6rem;'>No Sample</span>"
        if archival_img:
            ext = archival_img.split('.')[-1].lower()
            mime = "image/png" if ext == "png" else "image/jpeg"
            with open(archival_img, "rb") as f:
                data = base64.b64encode(f.read()).decode()
                img_html = f"<img src='data:{mime};base64,{data}' style='max-width:80px; max-height:80px; filter: contrast(1.1); border-radius: 4px;'>"

        # IMPORTANT: No indentation here to prevent Streamlit from creating a code block
        st.markdown(f"""
<div style='background: linear-gradient(145deg, #1a1f25, #0a0c10); 
            border: 1px solid rgba(196,169,98,0.3); border-radius: 20px; padding: 25px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin: 10px 0;'>
    <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; align-items: center; text-align: center;'>
        <!-- Column 1: Devanagari -->
        <div style='display: flex; flex-direction: column; gap: 8px;'>
            <div style='color: #7a8fa6; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>Devanagari</div>
            <div style='font-size: 4rem; color: #ffffff; line-height: 1;'>{selected_char}</div>
        </div>
        <!-- Column 2: Modi Unicode -->
        <div style='display: flex; flex-direction: column; gap: 8px; border-left: 1px solid rgba(255,255,255,0.1); border-right: 1px solid rgba(255,255,255,0.1);'>
            <div style='color: #7a8fa6; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>Modi Unicode</div>
            <div class='modi-font' style='font-size: 4rem; color: #ffd700; line-height: 1;'>{modi_char}</div>
        </div>
        <!-- Column 3: Archival Sample -->
        <div style='display: flex; flex-direction: column; gap: 8px; align-items: center;'>
            <div style='color: #7a8fa6; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>Archival Sample</div>
            <div style='background: #fff; width: 100px; height: 100px; border-radius: 12px; display: flex; align-items: center; justify-content:center; padding: 5px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);'>
                {img_html}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mapping Chart Box
    with st.expander("📜 Full Character Mapping Chart", expanded=False):
        st.markdown("<div style='border:1px solid rgba(255,255,255,0.05); border-radius:8px; overflow:hidden;'>", unsafe_allow_html=True)
        df = pd.DataFrame(list(DEVANAGARI_TO_MODI.items()), columns=['Devanagari', 'Modi Lipi'])
        st.dataframe(df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    uploaded_file = st.file_uploader("Upload a Modi script image...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("**Archival Evidence**")
            st.image(uploaded_file, use_container_width=True)

        with c2:
            st.markdown("**Visual AI Controls**")
            if st.button("Begin Visual Recognition"):
                with st.spinner("Analyzing image..."):
                    res = run_hybrid_ocr(uploaded_file)

                    dev_text = res['text']
                    # Local OCR Result Display
                    st.text_area("Devanagari Output", dev_text, height=100)
                    
                    # --- Translation Pipeline with Fallback ---
                    ocr_english = ""
                    ocr_engine = ""
                    m2m_success = False
                    
                    try:
                        # Step A: M2M100
                        corrected = correct_text(dev_text)
                        tokenizer, t_model = _load_translation_model()
                        if tokenizer and t_model:
                            tokenizer.src_lang = "mr"
                            enc = tokenizer(corrected, return_tensors="pt")
                            gen = t_model.generate(**enc, forced_bos_token_id=tokenizer.get_lang_id("en"))
                            ocr_english = tokenizer.batch_decode(gen, skip_special_tokens=True)[0].strip()
                            if len(ocr_english) > 2:
                                ocr_engine = "M2M100 Neural Engine"
                                m2m_success = True
                    except Exception:
                        pass
                        
                    if not m2m_success:
                        # Step B: Gemini AI Fallback
                        gemini_res = get_gemini_interpretation(dev_text)
                        if gemini_res:
                            ocr_english = gemini_res
                            ocr_engine = "Gemini AI (Historical Expert)"
                            m2m_success = True
                    
                    if not ocr_english: ocr_english = "[Translation unavailable]"
                    
                    st.text_area("English Output", ocr_english, height=150)
                    if ocr_engine:
                        st.markdown(f"""
                            <div style='background:rgba(196,169,98,0.1); border:1px solid rgba(196,169,98,0.2); 
                                        border-radius:4px; padding:4px 8px; font-size:0.7rem; color:#c4a962; 
                                        display:inline-block; margin-top:4px;'>
                                ⚙️ Engine: {ocr_engine}
                            </div>
                        """, unsafe_allow_html=True)

# -----------------------------
# SIDEBAR INSTRUCTIONS
# -----------------------------
st.sidebar.divider()
st.sidebar.subheader("📋 Usage Instructions")
st.sidebar.markdown("""
**1. Script Interpretation**
- Paste or type Modi Unicode text in the 'Source Inscription' box.
- Click **Generate Interpretation** to view Devanagari and English results.

**2. Visual Recognition (OCR)**
- Go to the **Visual Recognition** tab.
- Upload a clear image of archival script.
- Click **Begin Visual Recognition** to extract and translate text.

**3. Character Explorer**
- Use the dropdown in the **Interactive Explorer** to see character-by-character equivalents.
""")

st.sidebar.divider()
st.sidebar.markdown("<p style='color:#7a8fa6; font-size:0.8rem;'>Modi Lipi Intelligence Platform</p>", unsafe_allow_html=True)
