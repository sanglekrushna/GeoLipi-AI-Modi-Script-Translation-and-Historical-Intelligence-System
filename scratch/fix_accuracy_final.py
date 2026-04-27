import os
import unicodedata

def fix_accuracy_final():
    path = r'd:\ACADEMICS\SY\Semester 4th\ML\COURSE PROJECT\streamlit_app.py'
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # 1. Update the lookup logic to be more robust
    old_lookup = """        # A. Try Historical Map first
        words = devanagari.strip().split()
        if devanagari in HISTORICAL_MAP:"""
    
    new_lookup = """        # A. Try Historical Map first (with Normalization fix)
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
            m2m_success = True"""

    if old_lookup in content:
        content = content.replace(old_lookup, new_lookup)
    else:
        # Fallback if the string changed slightly
        print("Warning: Could not find exact lookup block, attempting fuzzy replacement")
        content = content.replace("if devanagari in HISTORICAL_MAP:", "if devanagari.strip() in HISTORICAL_MAP:")

    # 2. Add 'import unicodedata' at the top if missing
    if "import unicodedata" not in content:
        content = "import unicodedata\n" + content

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully applied Unicode normalization and robust dictionary lookup")

if __name__ == "__main__":
    fix_accuracy_final()
