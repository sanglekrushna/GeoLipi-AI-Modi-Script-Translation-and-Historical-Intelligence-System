from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# STEP 1 — LOAD M2M100 MODEL (ONCE, GLOBAL)
model_name = "facebook/m2m100_418M"
try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
except Exception as e:
    print(f"CRITICAL ERROR loading M2M100: {e}")
    tokenizer = None
    model = None

# STEP 2 & 7 — CREATE FINAL TRANSLATION FUNCTION WITH SAFETY
def translate_to_english(dev_text):
    if not dev_text or not dev_text.strip():
        return ""
    
    if model is None or tokenizer is None:
        return "[Model Error] Translation unavailable"

    try:
        tokenizer.src_lang = "mr"
        encoded = tokenizer(dev_text, return_tensors="pt").to(model.device)
        
        generated = model.generate(
            **encoded,
            forced_bos_token_id=tokenizer.get_lang_id("en")
        )

        output = tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
        return output.strip()
    except Exception as e:
        # Avoid printing 'e' if it contains unicode script to prevent Windows crash
        print("TRANSLATION ERROR occurred")
        return "Translation failed"

# Alias for backward compatibility if needed
translate_marathi_to_english = translate_to_english
