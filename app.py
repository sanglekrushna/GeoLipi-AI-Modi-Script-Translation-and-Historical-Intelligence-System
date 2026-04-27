import os
import csv
import json
import requests
import base64
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from PIL import Image
import torch
import cv2
import numpy as np
import pytesseract

from crnn_model import CRNN
from marathi_corrector import correct_text
from translator.modi_to_dev import convert_modi_to_devanagari as convert_modi_to_devanagari
from translator.translation import translate_marathi_to_english
from utils.site_matcher import match_site
from config import GEMINI_ENDPOINT, get_headers

# -----------------------------
# CONFIGURATION
# -----------------------------
app = Flask(__name__)
# Enable CORS for all routes to prevent 403/CORS errors from frontend
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------
# OCR / TRANSLATION MODELS
# -----------------------------
def _load_crnn_ocr_model():
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

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/sites")
def get_sites():
    sites = []
    try:
        if os.path.exists("modi_locations.json"):
            with open("modi_locations.json", encoding="utf-8") as f:
                sites = json.load(f)
    except Exception as e:
        print(f"Error loading sites: {e}")
    return jsonify(sites)

# STEP 4 — FIX TRANSLATE ROUTE PIPELINE
@app.route("/translate", methods=["POST"])
@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json()
    raw = data.get("text", "")
    
    from translator.modi_to_dev import convert_modi_to_devanagari as convert_modi_to_dev
    from translator.translation import translate_to_english
    
    # STEP 1: Modi -> Devanagari
    dev_text = convert_modi_to_dev(raw)
    
    try:
        print("DEV:", dev_text)
    except:
        print("DEV: [Unicode Print Suppressed]")
    
    # STEP 2: Dev -> English (M2M100)
    english = translate_to_english(dev_text)
    
    try:
        print("ENG:", english)
    except:
        print("ENG: [Unicode Print Suppressed]")
    
    return jsonify({
        "devanagari": dev_text,
        "english": english
    })

# STEP 5 — FIX OCR PIPELINE (TESSERACT)
def process_image(file):
    # Using cv2 as requested
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    text = pytesseract.image_to_string(gray, lang="mar") # use Marathi
    return text

# STEP 6 — CONNECT OCR -> TRANSLATION
@app.route("/api/ocr", methods=["POST"])
def ocr_pipeline():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image uploaded"}), 400
    
    try:
        ocr_text = process_image(file)
        
        from translator.modi_to_dev import convert_modi_to_devanagari as convert_modi_to_dev
        from translator.translation import translate_to_english
        
        # Connect Pipeline
        dev_text = convert_modi_to_dev(ocr_text)
        english = translate_to_english(dev_text)
        
        return jsonify({
            "ocr": ocr_text,
            "devanagari": dev_text,
            "english": english
        })
    except Exception as e:
        print(f"OCR ERROR: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/insight", methods=["POST"])
def get_insight():
    data = request.json
    place_name = data.get("name", "")
    place_year = data.get("year", "N/A")
    description = data.get("description", "")
    devanagari = data.get("devanagari", "")

    # ── Step 1: Try keyword match from our knowledge base ──
    matched = match_site(devanagari) if devanagari else None
    if not matched and place_name:
        # Also try matching by English name in sites
        matched = match_site(devanagari or place_name)

    if matched:
        insight = (
            f"🏛️ **{matched['name']}** | {matched['type']} · {matched['year']} CE\n\n"
            f"{matched['summary']}"
        )
        return jsonify({"insight": insight, "source": "Knowledge Base"})

    # ── Step 2: Try Gemini 1.5-flash ────────────────────
    prompt = (
        f"You are a historian specialising in the Maratha Empire and Modi Lipi. "
        f"Provide a concise 2-3 sentence historical insight about {place_name} "
        f"({place_year}). Context: {description}. "
        f"Focus on its significance during the Maratha period."
    )
    try:
        res = requests.post(
            GEMINI_ENDPOINT,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers=get_headers(),
            timeout=8
        )
        if res.status_code == 200:
            res_data = res.json()
            if 'candidates' in res_data:
                insight = res_data['candidates'][0]['content']['parts'][0]['text']
                return jsonify({"insight": insight, "source": "AI"})

        print(f"Gemini API returned {res.status_code}: {res.text[:200]}")
    except Exception as e:
        print(f"Gemini request failed: {e}")

    # ── Step 3: Rich local fallback ───────────────────────
    fallback = (
        f"🏛️ **{place_name}** (Est. {place_year})\n\n"
        f"{description}\n\n"
        f"This site held significant importance in the historical landscape of the "
        f"Deccan region during the Maratha Empire period."
    )
    return jsonify({"insight": fallback, "source": "Fallback"})

if __name__ == "__main__":
    app.run(debug=False, port=5000)
