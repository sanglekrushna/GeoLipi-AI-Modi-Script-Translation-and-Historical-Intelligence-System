"""
Site Matcher Utility
Matches extracted Devanagari text against the known historical sites database.
Keyword-based matching — no AI, no guessing.
"""

import json
import os

_SITES_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'sites.json')

def _load_sites():
    """Load sites.json once."""
    try:
        with open(_SITES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# Module-level cache — loaded once per process
_SITES = _load_sites()


def match_site(dev_text: str) -> dict | None:
    """
    Try to match Devanagari text against known sites using keyword search.

    Returns a dict with: name, devanagari, year, type, summary
    Returns None if no match found.
    """
    if not dev_text or not dev_text.strip():
        return None

    clean = dev_text.strip()

    for site in _SITES:
        for keyword in site.get('keywords', []):
            if keyword in clean:
                return {
                    'name':       site['name'],
                    'devanagari': site['devanagari'],
                    'year':       site.get('year', 'Unknown'),
                    'type':       site.get('type', 'Historical Site'),
                    'summary':    site['summary'],
                    'matched_by': keyword
                }

    return None
