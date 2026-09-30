"""
NLP utilities for SwachhSetu
- Category Detection (Option 2)
- Hindi-English Multi-language (Option 3)
"""

import re

# ============================================
# CATEGORY KEYWORDS (English + Hindi)
# ============================================
CATEGORY_KEYWORDS = {
    "overflow": [
        # English
        "overflow", "overflowing", "bin", "dustbin", "trash can",
        "full", "filled", "spilling", "brimming", "container",
        # Hindi (Devanagari)
        "भर", "भरा", "ओवरफ्लो", "कूड़ेदान", "डिब्बा", "डिब्बे",
        "बह", "बहना", "कचरा डिब्बा",
        # Hinglish (Roman)
        "bhar", "bhara", "bhar gaya", "kooda dan", "kuda dan",
    ],
    "road": [
        # English
        "road", "street", "gutter", "pavement", "footpath",
        "sidewalk", "highway", "lane", "alley", "roadside",
        # Hindi
        "सड़क", "गली", "रास्ता", "फुटपाथ", "गटर", "नाली",
        "रोड", "मार्ग",
        # Hinglish
        "sadak", "gali", "rasta", "footpath", "nalli",
    ],
    "illegal": [
        # English
        "illegal", "dump", "dumping", "construction", "debris",
        "rubble", "unauthorized", "midnight", "waste dump",
        "construction waste", "building material",
        # Hindi
        "अवैध", "कूड़ा डाल", "निर्माण", "मलबा", "गैरकानूनी",
        "कचरा डाल", "बर्बाद",
        # Hinglish
        "avaidh", "malba", "construction waste", "dump",
    ],
    "missed": [
        # English
        "missed", "not collected", "not picked", "no pickup",
        "days", "week", "repeat", "again", "delay", "late",
        "forgotten", "ignored",
        # Hindi
        "नहीं", "नहीं आया", "नहीं उठाया", "दिन", "हफ्ता", "देरी",
        "नहीं आए", "बार-बार", "इंतजार",
        # Hinglish
        "nahi aaya", "nahi uthaya", "din", "hafte", "deri",
    ],
}

# ============================================
# PRIORITY KEYWORDS (Optional - agar pehle se nahi hai)
# ============================================
PRIORITY_KEYWORDS = {
    "high": [
        "school", "hospital", "children", "bachhe", "bachcha",
        "college", "market", "busy", "urgent", "emergency",
        "stink", "smell", "infection", "disease", "health",
        "बच्चे", "स्कूल", "अस्पताल", "बीमारी", "गंदगी", "तुरंत",
        "शिक्षा", "स्वास्थ्य", "आपातकाल",
    ],
    "medium": [
        "park", "garden", "road", "street", "public",
        "सड़क", "बाज़ार", "बगीचा", "पार्क", "सार्वजनिक",
    ],
    "low": [
        "small", "tiny", "sometimes", "occasional",
        "छोटा", "कभी-कभी", "कम",
    ],
}


# ============================================
# UTILITY FUNCTIONS
# ============================================

def contains_hindi(text):
    """Check karo text mein Hindi (Devanagari) hai ya nahi."""
    if not text:
        return False
    return any('\u0900' <= c <= '\u097F' for c in text)


def normalize_text(text):
    """Text ko lowercase + strip karo."""
    if not text:
        return ""
    return text.lower().strip()


def detect_category(description):
    """
    Description se category detect karo.
    English + Hindi + Hinglish support.
    Returns: overflow | road | illegal | missed | other
    """
    if not description:
        return "other"

    text = normalize_text(description)
    scores = {}

    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in text:
                # Longer keywords get higher weight
                score += len(kw_lower) / 5.0
        scores[cat] = score

    max_score = max(scores.values()) if scores else 0
    if max_score < 1:  # Threshold
        return "other"

    return max(scores, key=scores.get)


def detect_priority(description):
    """
    Description se priority detect karo.
    Returns: high | medium | low
    """
    if not description:
        return "medium"

    text = normalize_text(description)

    for word in PRIORITY_KEYWORDS["high"]:
        if word.lower() in text:
            return "high"

    for word in PRIORITY_KEYWORDS["medium"]:
        if word.lower() in text:
            return "medium"

    return "low"


def extract_keywords(description, max_keywords=10):
    """
    Description se important keywords nikaalo.
    English + Hindi support.
    """
    if not description:
        return []

    # English + Hindi words
    words = re.findall(r'\b[a-zA-Z\u0900-\u097F]{3,}\b', description.lower())

    # Stopwords (English + Hindi)
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "i", "me",
        "my", "we", "our", "you", "your", "it", "its", "this",
        "that", "these", "those", "there", "here", "and", "or",
        "but", "for", "of", "to", "in", "on", "at", "by", "with",
        "from", "पर", "में", "से", "को", "है", "हैं", "था", "थे",
        "और", "या", "एक", "यह", "वह", "जो", "कि", "के", "की", "का",
    }

    keywords = [w for w in words if w not in stopwords]
    return keywords[:max_keywords]


def auto_detect_all(description):
    """
    Ek call mein sab kuch detect karo.
    Returns dict with category, priority, keywords, language.
    """
    return {
        "category": detect_category(description),
        "priority": detect_priority(description),
        "keywords": extract_keywords(description),
        "language": "hindi" if contains_hindi(description) else "english",
    }