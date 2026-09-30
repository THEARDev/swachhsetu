"""
SwachhSetu AI Chatbot
Uses Groq API (Llama 3.1) for smart, context-aware responses.
Falls back to rule-based if API fails.
"""

import os
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt, verify_jwt_in_request

chatbot_bp = Blueprint("chatbot", __name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"


SYSTEM_PROMPT = """You are SwachhSetu AI Assistant — a friendly, helpful chatbot for the SwachhSetu waste management platform.

ABOUT SWACHHSETU:
- Smart waste management platform for Indian cities
- Connects Citizens, Admins, and Workers in one ecosystem
- Tech: Flask backend, HTML/CSS/JS frontend, SQLite DB, AI (Hugging Face), NLP (Hindi + English), Leaflet maps
- Deployed on Render: swachhsetu-imgz.onrender.com

3-ROLE WORKFLOW:
1. Citizen reports waste issue (photo + GPS + description)
2. Admin sees dashboard, assigns to a worker
3. Worker completes task, uploads proof photo
4. Citizen tracks status live and gives feedback

HOW TO USE:
- Report issue: Login as citizen -> "Report Issue" -> fill form -> get Ticket ID
- Track complaint: Go to "Track" page -> enter Ticket ID (format: WMXXXXXXXX)
- Admin login: admin@demo.com / admin123
- Citizen login: citizen@demo.com / citizen123
- Worker login: ramesh@demo.com / worker123

KEY FEATURES:
- AI waste classification (wet/dry/hazardous auto-detect via Hugging Face)
- NLP priority detection (Hindi + English support)
- Real-time tracking (Submitted -> In Progress -> Resolved)
- Interactive hotspot map with color-coded pins
- Worker proof-of-work upload
- Multi-language support (Hindi + English)
- Dark mode
- Custom cursor, animations, confetti

YOUR JOB:
- Answer user's questions about SwachhSetu politely
- Reply in user's language (Hindi -> Hindi, English -> English, Hinglish -> Hinglish)
- Keep answers SHORT (2-4 sentences max)
- Be friendly and helpful
- Use emojis sparingly (1-2 per message max)
"""


def get_rule_based_response(message):
    msg = message.lower().strip()
    rules = [
        (["hello", "hi", "hey", "namaste", "hii"],
         "Namaste! 🙏 Main SwachhSetu AI Assistant hoon. Aap kaise madad chahiye — complaint report, tracking, ya kuch aur?"),
        (["report", "complaint", "file", "kaise darj", "issue"],
         "Complaint report karne ke liye:\n1. Login karo (citizen)\n2. 'Report Issue' click karo\n3. Category + description + photo + GPS daalo\n4. Submit → Ticket ID milega ✅"),
        (["track", "status", "kahan", "ticket", "update"],
         "Track karne ke liye 'Track' page kholo aur Ticket ID daalo (jaise WM12345ABC). Real-time timeline dikhega. 📍"),
        (["login", "sign in", "register", "account", "signup"],
         "Login/Register ke liye top-right 'Login' click karo. Demo:\n👤 citizen@demo.com / citizen123\n🛡️ admin@demo.com / admin123\n👷 ramesh@demo.com / worker123"),
        (["admin", "worker", "role"],
         "3 roles hain:\n👤 Citizen — complaint file karta hai\n🛡️ Admin — assign + manage karta hai\n👷 Worker — task complete karta hai"),
        (["ai", "nlp", "smart", "intelligent", "classif"],
         "AI waste classification (wet/dry/hazardous) Hugging Face se hoti hai. NLP priority detection Hindi + English dono support karta hai. 🤖"),
        (["map", "location", "hotspot", "pin"],
         "Interactive map pe complaints color-coded pins ke saath dikhti hain. Admin ko hotspots identify karne mein help karta hai. 🗺️"),
        (["feedback", "rating", "star", "review"],
         "Resolved complaint ke baad citizen feedback de sakta hai — 1 se 5 stars. ⭐"),
        (["thanks", "thank you", "shukriya", "dhanyavad"],
         "Aapka swagat! 😊 Koi aur sawaal ho toh zaroor puchein."),
        (["bye", "goodbye", "alvida"],
         "Phir milenge! Swachh sheher banane mein madad ke liye shukriya! 🌿"),
    ]
    for keywords, response in rules:
        if any(kw in msg for kw in keywords):
            return response
    return "Main SwachhSetu AI Assistant hoon. Complaint report karna, tracking, ya koi aur madad chahiye? Puchhiye! 🌿"


def call_groq_api(message, user_context=None):
    if not GROQ_API_KEY:
        return None
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if user_context:
            ctx = f"Current user: {user_context.get('name', 'Guest')} (role: {user_context.get('role', 'visitor')})"
            messages.append({"role": "system", "content": ctx})
        messages.append({"role": "user", "content": message})

        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 250,
                "top_p": 0.9,
            },
            timeout=15,
        )
        if response.status_code != 200:
            print(f"Groq error {response.status_code}: {response.text[:200]}")
            return None
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        return None
    except Exception as e:
        print(f"Groq exception: {e}")
        return None


@chatbot_bp.post("/message")
def chat():
    d = request.get_json() or {}
    message = (d.get("message") or "").strip()
    if not message:
        return jsonify(reply="Kuch likhiye toh sahi! 😅", source="system"), 200
    if len(message) > 500:
        message = message[:500]

    user_context = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            claims = get_jwt()
            user_context = {
                "name": claims.get("name", "User"),
                "role": claims.get("role", "citizen"),
            }
    except Exception:
        pass

    ai_reply = call_groq_api(message, user_context)
    if ai_reply:
        return jsonify(reply=ai_reply, source="ai"), 200

    rule_reply = get_rule_based_response(message)
    return jsonify(reply=rule_reply, source="rule"), 200


@chatbot_bp.get("/health")
def chat_health():
    return jsonify(
        status="ok",
        ai_enabled=bool(GROQ_API_KEY),
        model=GROQ_MODEL if GROQ_API_KEY else "rule-based-fallback",
    ), 200