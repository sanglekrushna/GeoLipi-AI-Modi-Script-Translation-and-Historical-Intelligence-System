import os

def update_ui_for_verification():
    path = r'd:\ACADEMICS\SY\Semester 4th\ML\COURSE PROJECT\streamlit_app.py'
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # 1. Update Tab 1 UI to show Engine Info
    old_tab1_ui = """        st.text_area(
            "English Output",
            height=140,
            label_visibility="collapsed",
            key="final_eng_box"
        )"""
    
    new_tab1_ui = """        st.text_area(
            "English Output",
            height=140,
            label_visibility="collapsed",
            key="final_eng_box"
        )
        
        # Engine indicator for verification
        engine = st.session_state.get('engine_info', '')
        if engine:
            st.markdown(f\"\"\"
                <div style='background:rgba(196,169,98,0.1); border:1px solid rgba(196,169,98,0.2); 
                            border-radius:4px; padding:4px 8px; font-size:0.7rem; color:#c4a962; 
                            display:inline-block; margin-top:4px;'>
                    \u2699\ufe0f Engine: {engine}
                </div>
            \"\"\", unsafe_allow_html=True)"""

    if old_tab1_ui in content:
        content = content.replace(old_tab1_ui, new_tab1_ui)
    else:
        print("Could not find Tab 1 UI block")

    # 2. Update Tab 2 (OCR) to use the same logic and show engine
    old_tab2_logic = """                    try:
                        corrected = correct_text(dev_text)
                        tokenizer, t_model = _load_translation_model()
                        tokenizer.src_lang = "mr"
                        enc = tokenizer(corrected, return_tensors="pt")
                        gen = t_model.generate(**enc, forced_bos_token_id=tokenizer.get_lang_id("en"))
                        ocr_english = tokenizer.batch_decode(gen, skip_special_tokens=True)[0].strip()
                    except Exception:
                        ocr_english = "[Translation unavailable]"
                    
                    st.text_area("English Output", ocr_english, height=150)"""

    new_tab2_logic = """                    # --- Translation Pipeline with Fallback ---
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
                        st.markdown(f\"\"\"
                            <div style='background:rgba(196,169,98,0.1); border:1px solid rgba(196,169,98,0.2); 
                                        border-radius:4px; padding:4px 8px; font-size:0.7rem; color:#c4a962; 
                                        display:inline-block; margin-top:4px;'>
                                \u2699\ufe0f Engine: {ocr_engine}
                            </div>
                        \"\"\", unsafe_allow_html=True)"""

    if old_tab2_logic in content:
        content = content.replace(old_tab2_logic, new_tab2_logic)
    else:
        print("Could not find Tab 2 logic block")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated UI for verification")

if __name__ == "__main__":
    update_ui_for_verification()
