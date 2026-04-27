import os

def fix_app_startup():
    path = r'd:\ACADEMICS\SY\Semester 4th\ML\COURSE PROJECT\app.py'
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # 1. Fix the wrong import name in the translate route
    content = content.replace("from translator.modi_to_dev import convert_modi_to_dev", "from translator.modi_to_dev import convert_modi_to_devanagari as convert_modi_to_dev")
    
    # 2. Disable debug mode to prevent reloader crashes
    content = content.replace("app.run(debug=True, port=5000)", "app.run(debug=False, port=5000)")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully patched app.py for stable startup")

if __name__ == "__main__":
    fix_app_startup()
