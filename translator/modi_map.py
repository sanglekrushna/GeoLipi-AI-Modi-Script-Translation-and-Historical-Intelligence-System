"""
Modi Script Character Maps — Structured 3-Layer System
Unicode block: U+11600 – U+1165F

Layer 1: BASE_MAP  — independent vowels + consonants
Layer 2: MATRA_MAP — dependent vowel signs (matras)
Layer 3: SPECIAL   — virama (halant), anusvara, visarga, digits, punctuation
"""

# ── Layer 1: Base Characters ──────────────────────────────────────────────────

BASE_MAP = {
    # Independent Vowels
    '𑘀': 'अ',   # U+11600
    '𑘁': 'आ',   # U+11601
    '𑘂': 'इ',   # U+11602
    '𑘃': 'ई',   # U+11603
    '𑘄': 'उ',   # U+11604
    '𑘅': 'ऊ',   # U+11605
    '𑘆': 'ऋ',   # U+11606
    '𑘇': 'ॠ',   # U+11607
    '𑘈': 'ऌ',   # U+11608
    '𑘉': 'ॡ',   # U+11609
    '𑘊': 'ए',   # U+1160A
    '𑘋': 'ऐ',   # U+1160B
    '𑘌': 'ओ',   # U+1160C
    '𑘍': 'औ',   # U+1160D

    # Consonants
    '𑘎': 'क',   # U+1160E  KA
    '𑘏': 'ख',   # U+1160F  KHA
    '𑘐': 'ग',   # U+11610  GA
    '𑘑': 'घ',   # U+11611  GHA
    '𑘒': 'ङ',   # U+11612  NGA
    '𑘓': 'च',   # U+11613  CA
    '𑘔': 'छ',   # U+11614  CHA
    '𑘕': 'ज',   # U+11615  JA
    '𑘖': 'झ',   # U+11616  JHA
    '𑘗': 'ञ',   # U+11617  NYA
    '𑘘': 'ट',   # U+11618  TTA
    '𑘙': 'ठ',   # U+11619  TTHA
    '𑘚': 'ड',   # U+1161A  DDA
    '𑘛': 'ढ',   # U+1161B  DDHA
    '𑘜': 'ण',   # U+1161C  NNA
    '𑘝': 'त',   # U+1161D  TA
    '𑘞': 'थ',   # U+1161E  THA
    '𑘟': 'द',   # U+1161F  DA
    '𑘠': 'ध',   # U+11620  DHA
    '𑘡': 'न',   # U+11621  NA
    '𑘢': 'प',   # U+11622  PA
    '𑘣': 'फ',   # U+11623  PHA
    '𑘤': 'ब',   # U+11624  BA
    '𑘥': 'भ',   # U+11625  BHA
    '𑘦': 'म',   # U+11626  MA
    '𑘧': 'य',   # U+11627  YA
    '𑘨': 'र',   # U+11628  RA
    '𑘩': 'ल',   # U+11629  LA
    '𑘪': 'व',   # U+1162A  VA
    '𑘫': 'श',   # U+1162B  SHA
    '𑘬': 'ष',   # U+1162C  SSA
    '𑘭': 'स',   # U+1162D  SA
    '𑘮': 'ह',   # U+1162E  HA
    '𑘯': 'ळ',   # U+1162F  LLA
}

# ── Layer 2: Dependent Vowel Signs (Matras) ───────────────────────────────────

MATRA_MAP = {
    '𑘰': 'ा',   # U+11630  Sign AA
    '𑘱': 'ि',   # U+11631  Sign I
    '𑘲': 'ी',   # U+11632  Sign II
    '𑘳': 'ु',   # U+11633  Sign U
    '𑘴': 'ू',   # U+11634  Sign UU
    '𑘵': 'ृ',   # U+11635  Sign Vocalic R
    '𑘶': 'ॄ',   # U+11636  Sign Vocalic RR
    '𑘷': 'ॢ',   # U+11637  Sign Vocalic L
    '𑘸': 'ॣ',   # U+11638  Sign Vocalic LL
    '𑘹': 'े',   # U+11639  Sign E
    '𑘺': 'ै',   # U+1163A  Sign AI
    '𑘻': 'ो',   # U+1163B  Sign O  (base + matra pair)
    '𑘼': 'ौ',   # U+1163C  Sign AU (base + matra pair)
}

# ── Layer 3: Special / Diacritics ────────────────────────────────────────────

# Virama — suppresses inherent 'a' vowel of a consonant (halant)
HALANT = '𑘿'           # U+1163F
HALANT_DEV = '्'

ANUSVARA     = '𑘽'     # U+1163D  → ं
VISARGA      = '𑘾'     # U+1163E  → ः
AVAGRAHA     = '𑙀'     # U+11640  → ऽ

SPECIAL_MAP = {
    ANUSVARA:  'ं',
    VISARGA:   'ः',
    HALANT:    HALANT_DEV,
    AVAGRAHA:  'ऽ',
    '𑙁':      '।',    # U+11641 Danda
    '𑙂':      '॥',   # U+11642 Double Danda
}

# ── Digits ────────────────────────────────────────────────────────────────────

DIGIT_MAP = {
    '𑙐': '०',  '𑙑': '१',  '𑙒': '२',  '𑙓': '३',  '𑙔': '४',
    '𑙕': '५',  '𑙖': '६',  '𑙗': '७',  '𑙘': '८',  '𑙙': '९',
}

# Combined set for quick membership tests
ALL_MODI = set(BASE_MAP) | set(MATRA_MAP) | set(SPECIAL_MAP) | set(DIGIT_MAP)
