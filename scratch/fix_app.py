import os

def fix_streamlit_app():
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
        "        # If it's a single word, check map first\n",
        "        words = devanagari.strip().split()\n",
        "        is_single_word = len(words) == 1\n",
        "        \n",
        "        if is_single_word and devanagari in HISTORICAL_MAP:\n",
        "            english = HISTORICAL_MAP[devanagari]\n",
        "            m2m_success = True\n",
        "        \n",
        "        # If it's a sentence or not in map, use Gemini for high-accuracy translation\n",
        "        if not m2m_success:\n",
        "            gemini_res = get_gemini_interpretation(devanagari, description=None)\n",
        "            if gemini_res:\n",
        "                english = gemini_res\n",
        "                m2m_success = True\n",
        "            else:\n",
        "                english = \"[Translation unavailable]\"\n",
        "\n",
        "        # Update session state for UI display\n",
        "        st.session_state['dev_out'] = devanagari\n",
        "        st.session_state['eng_out'] = english\n",
        "        st.session_state['final_dev_box'] = devanagari\n",
        "        st.session_state['final_eng_box'] = english\n",
        "\n"
    ]

    new_lines = lines[:start_line] + new_func + lines[end_line:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Successfully updated streamlit_app.py")

if __name__ == "__main__":
    fix_streamlit_app()
