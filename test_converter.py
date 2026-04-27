import sys
import io

# Force UTF-8 output to avoid Windows cp1252 crash
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from translator.modi_to_dev import convert_modi_to_devanagari, detect_script

tests = [
    ("𑘭𑘱𑘽𑘮𑘐𑘞",         "Sinhagad (known)"),
    ("𑘫𑘡𑘱𑘪𑘰𑘨 𑘪𑘰𑘚𑘰",  "Shaniwar Wada (space test)"),
    ("𑘨𑘰𑘕𑘐𑘚",            "Rajgad (consonant+matra)"),
    ("𑘎𑘿𑘭",               "KSA conjunct (halant test)"),
    ("शिवाजी",               "Devanagari passthrough"),
    ("hello",                 "English passthrough"),
    ("",                      "Empty string"),
]

print("=" * 60)
print("Modi → Devanagari Conversion Engine Test")
print("=" * 60)
for inp, label in tests:
    script = detect_script(inp) if inp else "empty"
    result = convert_modi_to_devanagari(inp) if inp else "(empty)"
    print(f"\n[{label}]")
    print(f"  Script : {script}")
    print(f"  Input  : {inp}")
    print(f"  Output : {result}")
print("\n" + "=" * 60)
print("All tests complete.")
