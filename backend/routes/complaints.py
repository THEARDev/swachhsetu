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


def classify_waste(image_path):
    """Hugging Face API se waste classify karo."""
    hf_token = os.getenv("HF_TOKEN", "").strip()
    if not hf_token:
        return "unknown"

    hf_url = "https://api-inference.huggingface.co/models/wanghaofan/waste-classification"

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        r = requests.post(
            hf_url,
            headers={"Authorization": f"Bearer {hf_token}"},
            data=image_bytes,
            timeout=12,
        )

        if r.status_code != 200:
            print("HF error status:", r.status_code, r.text[:200])
            return "unknown"

        data = r.json()
        if not isinstance(data, list) or not data:
            return "unknown"

        best = max(data[0], key=lambda x: x.get("score", 0))
        label = best.get("label", "").lower()

        if "wet" in label or "organic" in label:
            return "wet"
        if "dry" in label or "recycl" in label or "paper" in label or "plastic" in label:
            return "dry"
        if "hazard" in label or "toxic" in label or "e-waste" in label or "medical" in label:
            return "hazardous"
        return "unknown"

    except Exception as e:
        print("AI classify error:", e)
        return "unknown"


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

    # 🤖 NLP Auto-detection
    nlp_category = detect_category(description)
    nlp_priority = detect_priority(description)
    nlp_keywords = extract_keywords(description)
    detected_language = "hindi" if contains_hindi(description) else "english"

    # Agar user ne category select nahi ki, toh NLP ka use karo
    final_category = category if category else (nlp_category if nlp_category != "other" else "other")

    # Handle image upload
    img_url = ""
    ai_tag = "unknown"
    file = request.files.get("image")
    if file and file.filename:
        if not allowed_file(file.filename):
            return jsonify(msg="Invalid image format"), 400
        safe_name = secure_filename(file.filename)
        fn = f"{uuid.uuid4().hex}_{safe_name}"
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], fn)
        file.save(save_path)
        img_url = f"/uploads/{fn}"
        ai_tag = classify_waste(save_path)

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
        return jsonify(msg="Feedback already submitted for this complaint"), 400

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
    """NLP live preview endpoint."""
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