from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy import func
from datetime import datetime
from extensions import db
from models import Complaint, StatusLog, User, Feedback

admin_bp = Blueprint("admin", __name__)


def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"


@admin_bp.get("/complaints")
@jwt_required()
def all_complaints():
    if not is_admin():
        return jsonify(msg="Forbidden — admin only"), 403

    status_filter = request.args.get("status")
    q = Complaint.query
    if status_filter:
        q = q.filter_by(status=status_filter)

    items = q.order_by(Complaint.id.desc()).all()
    return jsonify([c.to_dict() for c in items]), 200


@admin_bp.patch("/complaints/<int:cid>")
@jwt_required()
def update_status(cid):
    if not is_admin():
        return jsonify(msg="Forbidden — admin only"), 403

    d = request.get_json() or {}
    new_status = d.get("status")
    remark = d.get("remark", "")

    valid_statuses = {"submitted", "acknowledged", "in_progress", "resolved", "closed"}
    if new_status not in valid_statuses:
        return jsonify(msg="Invalid status"), 400

    c = Complaint.query.get(cid)
    if not c:
        return jsonify(msg="Complaint not found"), 404

    old_status = c.status
    c.status = new_status

    db.session.add(StatusLog(
        complaint_id=c.id,
        old_status=old_status,
        new_status=new_status,
        remark=remark or f"Status changed to {new_status}",
        changed_by=int(get_jwt_identity()),
    ))
    db.session.commit()

    return jsonify(msg="Status updated", complaint=c.to_dict()), 200


@admin_bp.post("/complaints/<int:cid>/assign")
@jwt_required()
def assign_worker(cid):
    """Admin complaint ko worker ko assign karta hai."""
    if not is_admin():
        return jsonify(msg="Forbidden — admin only"), 403

    d = request.get_json() or {}
    worker_id = d.get("worker_id")

    if not worker_id:
        return jsonify(msg="Worker ID required"), 400

    worker = User.query.filter_by(id=worker_id, role="worker").first()
    if not worker:
        return jsonify(msg="Worker not found"), 404

    c = Complaint.query.get(cid)
    if not c:
        return jsonify(msg="Complaint not found"), 404
    if c.status == "resolved":
        return jsonify(msg="Complaint already resolved"), 400

    old_status = c.status
    c.assigned_to = worker_id
    c.assigned_at = datetime.utcnow()
    c.status = "acknowledged"

    db.session.add(StatusLog(
        complaint_id=c.id,
        old_status=old_status,
        new_status="acknowledged",
        remark=f"Assigned to worker: {worker.name}",
        changed_by=int(get_jwt_identity()),
    ))
    db.session.commit()

    return jsonify(
        msg=f"Assigned to {worker.name}",
        complaint=c.to_dict()
    ), 200


@admin_bp.get("/workers")
@jwt_required()
def all_workers():
    """Saare workers ki list."""
    if not is_admin():
        return jsonify(msg="Forbidden — admin only"), 403

    workers = User.query.filter_by(role="worker").all()

    result = []
    for w in workers:
        total = Complaint.query.filter_by(assigned_to=w.id).count()
        completed = Complaint.query.filter_by(
            assigned_to=w.id, status="resolved"
        ).count()
        in_progress = Complaint.query.filter_by(
            assigned_to=w.id, status="in_progress"
        ).count()

        result.append({
            **w.to_dict(),
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "active": in_progress,
        })

    return jsonify(result), 200


@admin_bp.get("/stats")
@jwt_required()
def stats():
    if not is_admin():
        return jsonify(msg="Forbidden — admin only"), 403

    total = Complaint.query.count()
    resolved = Complaint.query.filter_by(status="resolved").count()
    in_progress = Complaint.query.filter_by(status="in_progress").count()
    submitted = Complaint.query.filter_by(status="submitted").count()
    acknowledged = Complaint.query.filter_by(status="acknowledged").count()
    users = User.query.count()
    workers = User.query.filter_by(role="worker").count()

    avg_rating = db.session.query(func.avg(Feedback.rating)).scalar()
    avg_rating = round(float(avg_rating), 1) if avg_rating else 0

    return jsonify(
        total=total,
        resolved=resolved,
        in_progress=in_progress,
        submitted=submitted,
        acknowledged=acknowledged,
        pending=total - resolved,
        users=users,
        workers=workers,
        resolution_rate=round((resolved / total * 100) if total else 0, 1),
        avg_rating=avg_rating,
    ), 200


@admin_bp.get("/users")
@jwt_required()
def all_users():
    if not is_admin():
        return jsonify(msg="Forbidden — admin only"), 403
    users = User.query.order_by(User.id.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_bp.get("/hotspots")
@jwt_required()
def hotspots():
    if not is_admin():
        return jsonify(msg="Forbidden — admin only"), 403

    complaints = Complaint.query.all()
    used = set()
    hotspots_list = []

    for i, c in enumerate(complaints):
        if i in used or not c.lat or not c.lng:
            continue

        cluster = [c]
        used.add(i)

        for j, other in enumerate(complaints):
            if j in used or not other.lat or not other.lng:
                continue
            if abs(c.lat - other.lat) < 0.001 and abs(c.lng - other.lng) < 0.001:
                cluster.append(other)
                used.add(j)

        if len(cluster) >= 3:
            avg_lat = sum(x.lat for x in cluster) / len(cluster)
            avg_lng = sum(x.lng for x in cluster) / len(cluster)
            hotspots_list.append({
                "lat": avg_lat,
                "lng": avg_lng,
                "count": len(cluster),
                "intensity": min(len(cluster) / 10.0, 1.0),
            })

    return jsonify(hotspots_list), 200