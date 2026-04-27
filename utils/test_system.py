from translator.modi_to_dev import convert_modi_to_devanagari

def test_conversion():
    # Test Ka, Kha, Ga in Modi
    # Ka: \U0001160E, Kha: \U0001160F, Ga: \U00011610
    modi_text = "\U0001160E\U0001160F\U00011610"
    dev_text = convert_modi_to_devanagari(modi_text)
    
    # Check if correct (कखग)
    if dev_text == "कखग":
        print("Conversion Test Passed!")
    else:
        # We use repr() to see exactly what's there without terminal encoding issues
        print(f"Conversion Test Failed! Expected 'कखग', got {repr(dev_text)}")

if __name__ == "__main__":
    test_conversion()
