import os
import uuid
import requests
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models import Complaint, StatusLog, User, Feedback
from nlp import (
    detect_category,
    detect_priority,
    extract_keywords,
    contains_hindi,
)

complaints_bp = Blueprint("complaints", __name__)


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", set())


# ============================================
# AI CLASSIFICATION (VALIDATION DISABLED FOR DEMO)
# ============================================
HF_WASTE_URL = "https://api-inference.huggingface.co/models/wanghaofan/waste-classification"

CONFIDENCE_THRESHOLD = 0.30


def classify_waste(image_path):
    """
    Classify waste image.
    NOTE: Validation disabled for demo — always returns valid=True.
    """
    hf_token = os.getenv("HF_TOKEN", "").strip()

    # If no token, return unknown but valid
    if not hf_token:
        return {
            "tag": "unknown",
            "confidence": 0,
            "valid": True,
            "reason": "AI not configured",
        }

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        r = requests.post(
            HF_WASTE_URL,
            headers={"Authorization": f"Bearer {hf_token}"},
            data=image_bytes,
            timeout=15,
        )

        if r.status_code != 200:
            return {
                "tag": "unknown",
                "confidence": 0,
                "valid": True,
                "reason": f"API error {r.status_code}",
            }

        data = r.json()
        if not isinstance(data, list) or not data:
            return {
                "tag": "unknown",
                "confidence": 0,
                "valid": True,
                "reason": "Invalid response",
            }

        best = max(data[0], key=lambda x: x.get("score", 0))
        confidence = best.get("score", 0)
        label = best.get("label", "").lower()

        # Normalize label
        if "wet" in label or "organic" in label or "food" in label:
            tag = "wet"
        elif "dry" in label or "recycl" in label or "paper" in label or "plastic" in label:
            tag = "dry"
        elif "hazard" in label or "toxic" in label or "e-waste" in label or "medical" in label:
            tag = "hazardous"
        else:
            tag = "unknown"

        # ALWAYS VALID — no rejection
        return {
            "tag": tag,
            "confidence": round(confidence, 2),
            "valid": True,
            "reason": "Accepted",
        }

    except Exception as e:
        print(f"AI error: {e}")
        return {
            "tag": "unknown",
            "confidence": 0,
            "valid": True,
            "reason": "AI processing failed",
        }


# ============================================
# CREATE COMPLAINT
# ============================================
@complaints_bp.post("/")
@jwt_required()
def create_complaint():
    uid = int(get_jwt_identity())

    form = request.form
    category = (form.get("category") or "").strip()
    description = (form.get("description") or "").strip()
    address = (form.get("address") or "").strip()
    lat = form.get("lat", "0")
    lng = form.get("lng", "0")

    if len(description) < 10:
        return jsonify(msg="Description must be at least 10 characters"), 400

    try:
        lat = float(lat)
        lng = float(lng)
    except (ValueError, TypeError):
        lat, lng = 0.0, 0.0

    if lat == 0 and lng == 0:
        return jsonify(msg="Please detect location first"), 400

    # NLP Auto-detection
    nlp_category = detect_category(description)
    nlp_priority = detect_priority(description)
    nlp_keywords = extract_keywords(description)
    detected_language = "hindi" if contains_hindi(description) else "english"

    final_category = category if category else (nlp_category if nlp_category != "other" else "other")

    # ===== IMAGE HANDLING =====
    img_url = ""
    ai_tag = "unknown"
    ai_confidence = 0

    file = request.files.get("image")
    if file and file.filename:
        if not allowed_file(file.filename):
            return jsonify(msg="Invalid image format. Use JPG, PNG, or WEBP."), 400

        safe_name = secure_filename(file.filename)
        fn = f"{uuid.uuid4().hex}_{safe_name}"
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], fn)
        file.save(save_path)

        # AI Classification — NO REJECTION
        ai_result = classify_waste(save_path)
        ai_tag = ai_result["tag"]
        ai_confidence = ai_result["confidence"]

        img_url = f"/uploads/{fn}"

    # Generate ticket ID
    ticket_id = "WM" + uuid.uuid4().hex[:8].upper()

    complaint = Complaint(
        ticket_id=ticket_id,
        user_id=uid,
        category=final_category,
        description=description,
        image_url=img_url,
        ai_tag=ai_tag,
        priority=nlp_priority,
        nlp_category=nlp_category,
        keywords=",".join(nlp_keywords),
        language=detected_language,
        lat=lat,
        lng=lng,
        address=address,
        status="submitted",
    )
    db.session.add(complaint)
    db.session.flush()

    db.session.add(StatusLog(
        complaint_id=complaint.id,
        old_status="",
        new_status="submitted",
        remark="Complaint received",
        changed_by=uid,
    ))

    db.session.commit()

    return jsonify(
        msg="Complaint submitted",
        ticket_id=complaint.ticket_id,
        id=complaint.id,
        ai_tag=ai_tag,
        ai_confidence=ai_confidence,
        priority=nlp_priority,
        nlp_category=nlp_category,
        keywords=nlp_keywords,
        language=detected_language,
    ), 201


@complaints_bp.get("/my")
@jwt_required()
def my_complaints():
    uid = int(get_jwt_identity())
    items = (
        Complaint.query
        .filter_by(user_id=uid)
        .order_by(Complaint.id.desc())
        .all()
    )
    return jsonify([c.to_dict() for c in items]), 200


@complaints_bp.get("/track/<ticket_id>")
def track(ticket_id):
    c = Complaint.query.filter_by(ticket_id=ticket_id.upper()).first()
    if not c:
        return jsonify(msg="Complaint not found"), 404
    return jsonify(c.to_dict(with_logs=True)), 200


@complaints_bp.post("/<int:cid>/feedback")
@jwt_required()
def submit_feedback(cid):
    uid = int(get_jwt_identity())

    c = Complaint.query.get(cid)
    if not c:
        return jsonify(msg="Complaint not found"), 404
    if c.user_id != uid:
        return jsonify(msg="This is not your complaint"), 403
    if c.status != "resolved":
        return jsonify(msg="You can only rate resolved complaints"), 400
    if Feedback.query.filter_by(complaint_id=cid).first():
        return jsonify(msg="Feedback already submitted"), 400

    d = request.get_json() or {}
    try:
        rating = int(d.get("rating", 0))
    except (ValueError, TypeError):
        rating = 0

    if rating < 1 or rating > 5:
        return jsonify(msg="Rating must be between 1 and 5"), 400

    comment = (d.get("comment") or "").strip()[:500]

    fb = Feedback(
        complaint_id=cid,
        user_id=uid,
        rating=rating,
        comment=comment,
    )
    db.session.add(fb)
    db.session.commit()

    return jsonify(msg="Thanks for your feedback!", feedback=fb.to_dict()), 201


@complaints_bp.post("/analyze")
def analyze_text():
    d = request.get_json() or {}
    description = (d.get("description") or "").strip()

    if not description or len(description) < 5:
        return jsonify(
            category="",
            priority="",
            keywords=[],
            language="english",
        ), 200

    return jsonify(
        category=detect_category(description),
        priority=detect_priority(description),
        keywords=extract_keywords(description),
        language="hindi" if contains_hindi(description) else "english",
    ), 200