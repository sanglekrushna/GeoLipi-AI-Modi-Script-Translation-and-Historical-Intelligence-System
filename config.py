import os

# Gemini API Key
GEMINI_API_KEY = "AIzaSyAj-OVfsDIEBcpwCPAqLwlUPzT3fF6ywwc"

# Use gemini-1.5-flash (fastest, free tier supported)
# NOTE: Gemini API authenticates via ?key= in the URL — NO Bearer header
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

def get_headers():
    """Gemini only needs Content-Type — no Authorization header."""
    return {
        "Content-Type": "application/json"
    }
