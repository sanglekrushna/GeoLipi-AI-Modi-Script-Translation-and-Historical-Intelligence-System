import re

# -----------------------------
# 1. MARATHI DICTIONARY
# -----------------------------
COMMON_MARATHI_WORDS = {
    "आणि", "आहे", "होता", "होते", "मध्ये", "या", "तर", "पण", "नाही", "करून",
    "असे", "येथे", "तेथे", "जेव्हा", "तेव्हा", "कसे", "कोठे", "काय", "कोण",
    "एक", "दोन", "तीन", "चार", "पाच", "सहा", "सात", "आठ", "नऊ", "दहा",
    "किल्ला", "महाराज", "शिवाजी", "मराठा", "इतिहास", "स्वराज्य", "पुणे",
    "महाराष्ट्र", "किल्ले", "गड", "राजधानी", "शासन", "प्रशासन", "पत्र",
    "दस्तऐवज", "कागदपत्रे", "मोडी", "लिपी", "देवनागरी", "मराठी"
}

def edit_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        new_distances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1],
                                             distances[index1 + 1],
                                             new_distances[-1])))
        distances = new_distances
    return distances[-1]

def correct_text(text, threshold=2):
    if not text:
        return ""
    
    words = text.split()
    corrected_words = []
    
    for word in words:
        if word in COMMON_MARATHI_WORDS:
            corrected_words.append(word)
            continue
            
        best_match = word
        min_dist = threshold + 1
        
        for dict_word in COMMON_MARATHI_WORDS:
            dist = edit_distance(word, dict_word)
            if dist < min_dist:
                min_dist = dist
                best_match = dict_word
                
        if min_dist <= threshold:
            corrected_words.append(best_match)
        else:
            corrected_words.append(word)
            
    return " ".join(corrected_words)
