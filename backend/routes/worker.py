import os
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models import Complaint, StatusLog, User

worker_bp = Blueprint("worker", __name__)


def is_worker():
    claims = get_jwt()
    return claims.get("role") == "worker"


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", set())


@worker_bp.get("/tasks")
@jwt_required()
def my_tasks():
    """Worker ke assigned tasks."""
    if not is_worker():
        return jsonify(msg="Forbidden — worker only"), 403

    worker_id = int(get_jwt_identity())
    status_filter = request.args.get("status")

    q = Complaint.query.filter_by(assigned_to=worker_id)
    if status_filter and status_filter != "all":
        q = q.filter_by(status=status_filter)

    items = q.order_by(Complaint.priority.desc(), Complaint.id.desc()).all()
    return jsonify([c.to_dict() for c in items]), 200


@worker_bp.get("/stats")
@jwt_required()
def my_stats():
    """Worker performance stats."""
    if not is_worker():
        return jsonify(msg="Forbidden — worker only"), 403

    worker_id = int(get_jwt_identity())

    total = Complaint.query.filter_by(assigned_to=worker_id).count()
    completed = Complaint.query.filter_by(
        assigned_to=worker_id, status="resolved"
    ).count()
    in_progress = Complaint.query.filter_by(
        assigned_to=worker_id, status="in_progress"
    ).count()
    pending = Complaint.query.filter_by(
        assigned_to=worker_id, status="submitted"
    ).count()

    # Today's stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_completed = Complaint.query.filter(
        Complaint.assigned_to == worker_id,
        Complaint.status == "resolved",
        Complaint.completed_at >= today_start,
    ).count()

    # Avg completion time (in hours)
    completed_tasks = Complaint.query.filter(
        Complaint.assigned_to == worker_id,
        Complaint.status == "resolved",
        Complaint.completed_at.isnot(None),
        Complaint.started_at.isnot(None),
    ).all()

    avg_time = 0
    if completed_tasks:
        total_time = sum(
            (c.completed_at - c.started_at).total_seconds()
            for c in completed_tasks
        )
        avg_time = round(total_time / len(completed_tasks) / 3600, 1)

    # Performance rating (0-100)
    rating = 0
    if total > 0:
        rating = min(100, round((completed / total) * 100))

    return jsonify(
        total=total,
        completed=completed,
        in_progress=in_progress,
        pending=pending,
        today_completed=today_completed,
        avg_completion_hours=avg_time,
        rating=rating,
    ), 200


@worker_bp.patch("/tasks/<int:cid>/start")
@jwt_required()
def start_task(cid):
    """Worker task start karta hai."""
    if not is_worker():
        return jsonify(msg="Forbidden — worker only"), 403

    worker_id = int(get_jwt_identity())
    c = Complaint.query.get(cid)

    if not c:
        return jsonify(msg="Task not found"), 404
    if c.assigned_to != worker_id:
        return jsonify(msg="This task is not assigned to you"), 403
    if c.status not in ("submitted", "acknowledged"):
        return jsonify(msg="Task already started or completed"), 400

    old_status = c.status
    c.status = "in_progress"
    c.started_at = datetime.utcnow()

    db.session.add(StatusLog(
        complaint_id=c.id,
        old_status=old_status,
        new_status="in_progress",
        remark=f"Worker started task",
        changed_by=worker_id,
    ))
    db.session.commit()

    return jsonify(msg="Task started", complaint=c.to_dict()), 200


@worker_bp.post("/tasks/<int:cid>/complete")
@jwt_required()
def complete_task(cid):
    """Worker task complete karta hai with photo proof."""
    if not is_worker():
        return jsonify(msg="Forbidden — worker only"), 403

    worker_id = int(get_jwt_identity())
    c = Complaint.query.get(cid)

    if not c:
        return jsonify(msg="Task not found"), 404
    if c.assigned_to != worker_id:
        return jsonify(msg="This task is not assigned to you"), 403
    if c.status == "resolved":
        return jsonify(msg="Task already completed"), 400

    # Remarks (form field)
    remarks = (request.form.get("remarks") or "").strip()

    # Proof image upload
    proof_url = ""
    file = request.files.get("proof_image")
    if file and file.filename:
        if not allowed_file(file.filename):
            return jsonify(msg="Invalid image format"), 400
        safe_name = secure_filename(file.filename)
        fn = f"proof_{uuid.uuid4().hex}_{safe_name}"
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], fn)
        file.save(save_path)
        proof_url = f"/uploads/{fn}"

    old_status = c.status
    c.status = "resolved"
    c.completed_at = datetime.utcnow()
    c.proof_image_url = proof_url
    c.worker_remarks = remarks

    db.session.add(StatusLog(
        complaint_id=c.id,
        old_status=old_status,
        new_status="resolved",
        remark=remarks or "Task completed by worker",
        changed_by=worker_id,
    ))
    db.session.commit()

    return jsonify(
        msg="Task completed! Great work.",
        complaint=c.to_dict()
    ), 200


@worker_bp.get("/task/<int:cid>")
@jwt_required()
def task_detail(cid):
    """Ek specific task ka detail."""
    if not is_worker():
        return jsonify(msg="Forbidden — worker only"), 403

    worker_id = int(get_jwt_identity())
    c = Complaint.query.get(cid)

    if not c:
        return jsonify(msg="Task not found"), 404
    if c.assigned_to != worker_id:
        return jsonify(msg="Not your task"), 403

    return jsonify(c.to_dict(with_logs=True)), 200