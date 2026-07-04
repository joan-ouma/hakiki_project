"""Detect gendered disinformation patterns targeting female politicians."""
import re

# Patterns from research: body-shaming, emotional framing, sexual slurs, delegitimization
GENDERED_PATTERNS = [
    r'\b(slay queen|slayqueen)\b',
    r'\b(prostitut|malaya|kahaba|demu|lanye)\b',
    r'\b(too (old|emotional|aggressive|angry|weak))\b',
    r'\b(attention seeker|drama queen)\b',
    r'\b(cannot lead|can\'t lead|hawezi kuongoza)\b',
    r'\b(go back to (kitchen|home)|rudi jikoni)\b',
    r'\b(ugly|fat|old woman|mzee wa kike)\b',
    r'\b(sex tape|nudes|leaked video|leaked photos)\b',
    r'\b(dumb|stupid|foolish) (woman|lady|mama)\b',
    r'\b(hysteri|crazy woman|mwendawazimu)\b',
]

_compiled = [re.compile(p, re.IGNORECASE) for p in GENDERED_PATTERNS]

# Known female Kenyan politicians (for context-aware detection)
FEMALE_POLITICIANS = [
    "martha karua", "karua", "anne waiguru", "waiguru", "gladys wanga", "wanga",
    "susan kihika", "kihika", "cecily mbarire", "mbarire", "alice wahome", "wahome",
    "rachael omamo", "omamo", "charity ngilu", "ngilu", "sabina chege", "millie odhiambo",
]


def detect_gendered_disinfo(text: str) -> dict | None:
    """Check if text contains gendered disinformation patterns.
    Returns dict with flag and matched pattern, or None if clean."""
    text_lower = text.lower()

    for pattern in _compiled:
        match = pattern.search(text_lower)
        if match:
            targets_politician = any(name in text_lower for name in FEMALE_POLITICIANS)
            return {
                "flagged": True,
                "pattern": match.group(0),
                "targets_known_politician": targets_politician,
            }

    return None
