from flask import Blueprint, jsonify

awareness_bp = Blueprint("awareness", __name__)


@awareness_bp.get("/")
def list_content():
    """Static awareness content — frontend bhi hardcoded use karta hai,
    but API se bhi milta hai (future dynamic content ke liye)."""
    return jsonify([
        {
            "type": "wet",
            "title": "Wet Waste",
            "description": "Kitchen waste, vegetable peels, food scraps, tea leaves, egg shells, garden waste, flowers.",
            "bin": "Green bin",
            "color": "#00C896",
        },
        {
            "type": "dry",
            "title": "Dry Waste",
            "description": "Paper, cardboard, plastic bottles, glass, metal cans, tetra packs, packaging material, rubber.",
            "bin": "Blue bin",
            "color": "#4DA6FF",
        },
        {
            "type": "hazardous",
            "title": "Hazardous Waste",
            "description": "Batteries, medicines, syringes, e-waste, paints, chemicals, CFL bulbs, sanitary waste.",
            "bin": "Red bin / Special collection",
            "color": "#FF6B6B",
        },
    ]), 200


@awareness_bp.get("/facts")
def fun_facts():
    return jsonify([
        {"title": "1.5 Lakh Tonnes", "desc": "India daily waste generate karta hai"},
        {"title": "Only 20% Recycled", "desc": "Baaki landfill mein jata hai"},
        {"title": "Compost = Gold", "desc": "Wet waste se best fertilizer banta hai"},
        {"title": "500+ Years", "desc": "Plastic decompose hone mein time leta hai"},
    ]), 200