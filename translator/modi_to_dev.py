"""
Modi Script → Devanagari Conversion Engine
==========================================
Smart 3-layer converter with:
  - Lookahead for matra attachment
  - Halant (virama) handling for conjuncts
  - Script auto-detection (Modi / Devanagari / unknown)
  - Normalization + confidence validation
  - Safe fallback — never returns garbage
"""

from .modi_map import (
    BASE_MAP, MATRA_MAP, SPECIAL_MAP, DIGIT_MAP,
    HALANT, HALANT_DEV, ALL_MODI
)


# ── Script Detection ──────────────────────────────────────────────────────────

def detect_script(text: str) -> str:
    """
    Detect whether input is Modi, Devanagari, or unknown.

    Returns: 'modi' | 'devanagari' | 'unknown'
    """
    for ch in text:
        if '\U00011600' <= ch <= '\U0001165F':
            return 'modi'
    for ch in text:
        if '\u0900' <= ch <= '\u097F':
            return 'devanagari'
    return 'unknown'


# ── Normalization ─────────────────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    """Strip and normalize whitespace in the input."""
    # Normalize various Unicode spaces to regular ASCII space
    text = text.strip()
    text = ' '.join(text.split())
    return text


# ── Confidence Validator ──────────────────────────────────────────────────────

def is_valid_devanagari(text: str) -> bool:
    """Return True if text contains at least one Devanagari character."""
    return any('\u0900' <= ch <= '\u097F' for ch in text)


# ── Core Conversion Engine ────────────────────────────────────────────────────

def _convert_word(word: str) -> str:
    """
    Convert a single Modi word (no spaces) to Devanagari using lookahead logic.

    Rules (applied left-to-right):
      1. Consonant + Matra     → attach matra directly (no inherent 'a')
      2. Consonant + Halant    → attach halant (virama), forms half-consonant
      3. Consonant alone       → consonant (inherent 'a' retained)
      4. Independent vowel     → convert directly
      5. Anusvara / Visarga    → append to previous output
      6. Digit / Punctuation   → convert directly
      7. Unknown               → pass through unchanged (safe fallback)
    """
    result = []
    i = 0
    n = len(word)

    while i < n:
        ch = word[i]

        # ── Digit ─────────────────────────────────────────
        if ch in DIGIT_MAP:
            result.append(DIGIT_MAP[ch])
            i += 1
            continue

        # ── Special (anusvara, visarga, danda…) ───────────
        if ch in SPECIAL_MAP:
            result.append(SPECIAL_MAP[ch])
            i += 1
            continue

        # ── Standalone matra (edge case: matra with no base) ─
        if ch in MATRA_MAP:
            result.append(MATRA_MAP[ch])
            i += 1
            continue

        # ── Base character (consonant or independent vowel) ──
        if ch in BASE_MAP:
            base_dev = BASE_MAP[ch]
            next_ch = word[i + 1] if i + 1 < n else None

            # Case A: Base + Matra → combine (suppresses inherent 'a')
            if next_ch and next_ch in MATRA_MAP:
                result.append(base_dev + MATRA_MAP[next_ch])
                i += 2
                continue

            # Case B: Base + Halant → half-consonant / conjunct
            if next_ch == HALANT:
                result.append(base_dev + HALANT_DEV)
                i += 2
                continue

            # Case C: Base alone → full syllable (with inherent 'a')
            result.append(base_dev)
            i += 1
            continue

        # ── Fallback: unknown character ────────────────────
        result.append(ch)
        i += 1

    return ''.join(result)


def convert_modi_to_devanagari(text: str) -> str:
    """
    Main public entry point.

    Pipeline:
      1. Detect script
      2. If already Devanagari / unknown → return as-is
      3. Normalize
      4. Convert word-by-word (preserves spaces)
      5. Validate output — fallback to input if no Devanagari produced
    """
    if not text or not text.strip():
        return text

    script = detect_script(text)

    # Pass-through for non-Modi input
    if script in ('devanagari', 'unknown'):
        return text

    # Normalize
    text = normalize_text(text)

    # Convert each word separately to preserve spacing
    words = text.split(' ')
    converted_words = [_convert_word(w) for w in words]
    result = ' '.join(converted_words)

    # Safety: if output has no Devanagari at all, return original
    if not is_valid_devanagari(result):
        return text

    return result

# STEP 3 — FIX MODI -> DEVANAGARI CONVERSION
def convert_modi_to_dev(text):
    """
    Requested entry point for the pipeline.
    Uses the advanced clustering logic to ensure Modi matras and halants 
    are handled correctly, never returning broken strings.
    """
    if not text:
        return ""
    return convert_modi_to_devanagari(text)
