import os

def fix_multi_word_mapping():
    path = r'd:\ACADEMICS\SY\Semester 4th\ML\COURSE PROJECT\streamlit_app.py'
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Change the logic to allow multi-word mapping
    old_logic = "if len(words) == 1 and devanagari in HISTORICAL_MAP:"
    new_logic = "if devanagari in HISTORICAL_MAP:"

    if old_logic in content:
        content = content.replace(old_logic, new_logic)
    else:
        print("Could not find the word length constraint logic")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully enabled multi-word historical mapping")

if __name__ == "__main__":
    fix_multi_word_mapping()
