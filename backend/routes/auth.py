from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    d = request.get_json() or {}

    name = (d.get("name") or "").strip()
    email = (d.get("email") or "").strip().lower()
    phone = (d.get("phone") or "").strip()
    password = d.get("password") or ""
    role = d.get("role", "citizen")
    zone = (d.get("zone") or "").strip()

    if not name or len(name) < 2:
        return jsonify(msg="Name must be at least 2 characters"), 400
    if not email or "@" not in email:
        return jsonify(msg="Please provide a valid email"), 400
    if not password or len(password) < 6:
        return jsonify(msg="Password must be at least 6 characters"), 400
    if phone and (not phone.isdigit() or len(phone) != 10):
        return jsonify(msg="Phone must be 10 digits"), 400
    if role not in ("citizen", "admin", "worker"):
        role = "citizen"

    if User.query.filter_by(email=email).first():
        return jsonify(msg="Email already registered"), 400

    user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=generate_password_hash(password),
        role=role,
        zone=zone if role == "worker" else "",
    )
    db.session.add(user)
    db.session.commit()

    return jsonify(
        msg="Registered successfully",
        user_id=user.id,
        name=user.name,
        role=user.role,
    ), 201


@auth_bp.post("/login")
def login():
    d = request.get_json() or {}
    email = (d.get("email") or "").strip().lower()
    password = d.get("password") or ""

    if not email or not password:
        return jsonify(msg="Email and password required"), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify(msg="Invalid credentials"), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "name": user.name,
            "zone": user.zone or "",
        },
    )

    return jsonify(
        token=token,
        role=user.role,
        name=user.name,
        user_id=user.id,
        zone=user.zone or "",
    ), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return jsonify(msg="User not found"), 404
    return jsonify(user.to_dict()), 200