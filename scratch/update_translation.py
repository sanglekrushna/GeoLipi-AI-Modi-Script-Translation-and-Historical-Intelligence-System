import os

def update_interpretation_logic():
    path = r'd:\ACADEMICS\SY\Semester 4th\ML\COURSE PROJECT\streamlit_app.py'
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    start_line = -1
    end_line = -1
    for i, line in enumerate(lines):
        if 'def run_interpretation():' in line:
            start_line = i
        if start_line != -1 and 'col1, col2 = st.columns([1, 1])' in line:
            end_line = i
            break

    if start_line == -1 or end_line == -1:
        print(f"Could not find boundaries: start={start_line}, end={end_line}")
        return

    new_func = [
        "    def run_interpretation():\n",
        "        raw = st.session_state.get('modi_input_box', '').strip()\n",
        "        if not raw:\n",
        "            return\n",
        "            \n",
        "        # -- Step 1: Devanagari Conversion --\n",
        "        devanagari = convert_modi_to_devanagari(raw)\n",
        "        \n",
        "        # -- Step 2: High-Precision Translation --\n",
        "        english = \"\"\n",
        "        engine_used = \"\"\n",
        "        m2m_success = False\n",
        "        \n",
        "        # Robust Historical Mapping (for common terms)\n",
        "        HISTORICAL_MAP = {\n",
        "            \"स्वराज्य\": \"Self-rule / Independence\",\n",
        "            \"किल्ला\": \"Fort / Fortress\",\n",
        "            \"कील्ला\": \"Fort / Fortress\",\n",
        "            \"गड\": \"Hill Fort\",\n",
        "            \"राजा\": \"King / Monarch\",\n",
        "            \"छत्रपती\": \"Emperor (Chhatrapati)\"\n",
        "        }\n",
        "        \n",
        "        # A. Try Historical Map first\n",
        "        words = devanagari.strip().split()\n",
        "        if len(words) == 1 and devanagari in HISTORICAL_MAP:\n",
        "            english = HISTORICAL_MAP[devanagari]\n",
        "            engine_used = \"Historical Dictionary\"\n",
        "            m2m_success = True\n",
        "        \n",
        "        # B. Try M2M100 (Deep Learning Translator)\n",
        "        if not m2m_success:\n",
        "            try:\n",
        "                tokenizer, t_model = _load_translation_model()\n",
        "                if tokenizer and t_model:\n",
        "                    tokenizer.src_lang = \"mr\"\n",
        "                    enc = tokenizer(devanagari, return_tensors=\"pt\")\n",
        "                    gen = t_model.generate(**enc, forced_bos_token_id=tokenizer.get_lang_id(\"en\"))\n",
        "                    english = tokenizer.batch_decode(gen, skip_special_tokens=True)[0].strip()\n",
        "                    if len(english) > 2:\n",
        "                        engine_used = \"M2M100 Neural Engine\"\n",
        "                        m2m_success = True\n",
        "            except Exception:\n",
        "                pass\n",
        "        \n",
        "        # C. Fallback to Gemini AI (Historical Expert)\n",
        "        if not m2m_success or len(english) < 3:\n",
        "            gemini_res = get_gemini_interpretation(devanagari)\n",
        "            if gemini_res:\n",
        "                english = gemini_res\n",
        "                engine_used = \"Gemini AI (Historical Expert)\"\n",
        "                m2m_success = True\n",
        "            else:\n",
        "                if not english: english = \"[Translation unavailable]\"\n",
        "\n",
        "        # Update session state for UI display\n",
        "        st.session_state['dev_out'] = devanagari\n",
        "        st.session_state['eng_out'] = english\n",
        "        st.session_state['engine_info'] = engine_used\n",
        "        st.session_state['final_dev_box'] = devanagari\n",
        "        st.session_state['final_eng_box'] = english\n",
        "\n"
    ]

    new_lines = lines[:start_line] + new_func + lines[end_line:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Successfully updated translation logic in streamlit_app.py")

if __name__ == "__main__":
    update_interpretation_logic()
