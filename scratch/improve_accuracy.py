import os

def improve_accuracy():
    path = r'd:\ACADEMICS\SY\Semester 4th\ML\COURSE PROJECT\streamlit_app.py'
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Expand the Historical Map
    old_map = """        HISTORICAL_MAP = {
            "स्वराज्य": "Self-rule / Independence",
            "किल्ला": "Fort / Fortress",
            "कील्ला": "Fort / Fortress",
            "गड": "Hill Fort",
            "राजा": "King / Monarch",
            "छत्रपती": "Emperor (Chhatrapati)"
        }"""
    
    new_map = """        HISTORICAL_MAP = {
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
        }"""

    if old_map in content:
        content = content.replace(old_map, new_map)
    
    # Update Gemini Prompt to be more strict about names
    old_prompt = "Prioritize historical accuracy for terms relating to the Maratha Empire or Modi script."
    new_prompt = "Strictly prioritize historical accuracy. Do not provide literal translations for names (e.g., 'Shivaji Maharaj' must remain as such, never 'Shiva Majesty'). Focus on the Maratha Empire context."
    
    content = content.replace(old_prompt, new_prompt)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully improved translation accuracy and mapping")

if __name__ == "__main__":
    improve_accuracy()
