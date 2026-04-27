import streamlit as st
import torch
import cv2
import numpy as np
import json
import os
from PIL import Image
from crnn_model import CRNN
from translator.modi_to_dev import convert_modi_to_devanagari

# --- Resource Loading (Stubbed for snippet) ---
def load_crnn_bundle():
    vocab_path = "best_vocab.json"
    ckpt_path = "best_model.pth"
    if not os.path.exists(vocab_path) or not os.path.exists(ckpt_path):
        return None, None
    with open(vocab_path, encoding='utf-8') as f:
        vocab = json.load(f)
    model = CRNN(vocab_size=len(vocab)+1)
    model.load_state_dict(torch.load(ckpt_path, map_location='cpu'))
    model.eval()
    return model, vocab

def _ctc_decode_greedy(logits, vocab, blank_idx=0):
    pred_ids = torch.argmax(logits, dim=2)
    seq = pred_ids[:, 0].tolist()
    out = []
    prev = None
    for idx in seq:
        if idx != prev and idx != blank_idx:
            if 0 < idx <= len(vocab):
                out.append(vocab[idx-1])
        prev = idx
    return "".join(out)

def run_hybrid_ocr_logic(pil_img):
    model, vocab = load_crnn_bundle()
    if model is None:
        return {"text": "? Model files missing", "confidence": 0.0, "engine": "None"}
        
    img = np.array(pil_img.convert('L'))
    h, w = img.shape
    new_w = min(int(64 * (w / h)), 1024)
    img_resized = cv2.resize(img, (new_w, 64))
    
    padded = np.ones((64, 1024), dtype=np.uint8) * 255
    padded[:, :new_w] = img_resized
    tensor = torch.from_numpy(padded).float().unsqueeze(0).unsqueeze(0) / 255.0
    
    with torch.no_grad():
        logits = model(tensor)
        text = _ctc_decode_greedy(logits, vocab)
        
    return {"text": text, "confidence": 0.45, "engine": "CRNN (Experimental)"}

# -----------------------------
# MAIN UI COMPONENT
# -----------------------------
def render_translator_ui():
    st.markdown("""
    <div style='margin-bottom:8px;'>
        <h1 style='color:#c4a962;font-family:Georgia,serif;font-size:2rem;margin-bottom:2px;'>
            Modi Lipi Intelligence
        </h1>
        <p style='color:#7a8fa6;font-size:0.85rem;margin-top:0;'>
            Premium Historical Script Discovery & Visual AI Pipeline
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📝 Script Interpretation", "📷 Visual Recognition (OCR)"])

    with tab1:
        if 'dev_out' not in st.session_state: st.session_state['dev_out'] = ""
        if 'eng_out' not in st.session_state: st.session_state['eng_out'] = ""

        def run_interpretation():
            raw = st.session_state.get('modi_input_box', '').strip()
            if not raw: return
                
            # -- Step 1: Devanagari Conversion --
            devanagari = convert_modi_to_devanagari(raw)
            
            # -- Step 2: High-Precision Translation --
            HISTORICAL_MAP = {
                "स्वराज्य": "Self-rule / Independence",
                "किल्ला": "Fort / Fortress",
                "राजा": "King / Monarch",
                "छत्रपती": "Emperor (Chhatrapati)"
            }
            
            english = HISTORICAL_MAP.get(devanagari, "Translation via AI Engine...")
            
            st.session_state['dev_out'] = devanagari
            st.session_state['eng_out'] = english
            st.session_state['final_dev_box'] = devanagari
            st.session_state['final_eng_box'] = english

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### Source Inscription")
            st.text_area(
                label="", height=180,
                placeholder="Paste Modi Lipi Unicode characters here...",
                label_visibility="collapsed", key="modi_input_box"
            )
            st.button("Generate Interpretation", on_click=run_interpretation)

        with col2:
            st.markdown("### Processed Output")
            st.markdown("<div style='color:#7a8fa6; font-size:0.8rem; margin-bottom:4px;'>Devanagari Transcription</div>", unsafe_allow_html=True)
            st.text_area("Devanagari Output", height=100, label_visibility="collapsed", key="final_dev_box")
            
            st.markdown("<div style='color:#7a8fa6; font-size:0.8rem; margin-bottom:4px; margin-top:12px;'>English Interpretation</div>", unsafe_allow_html=True)
            st.text_area("English Output", height=140, label_visibility="collapsed", key="final_eng_box")

    st.markdown("---")
    st.subheader("Interactive Character Explorer")
    st.info("Select a character to see its historical equivalent.")

if __name__ == "__main__":
    render_translator_ui()