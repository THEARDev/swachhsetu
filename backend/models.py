from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15), default="")
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="citizen")  # citizen | admin | worker
    zone = db.Column(db.String(50), default="")  # worker ka assigned zone
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaints = db.relationship(
        "Complaint",
        backref="user",
        lazy=True,
        foreign_keys="Complaint.user_id"
    )

    assigned_tasks = db.relationship(
        "Complaint",
        backref="worker",
        lazy=True,
        foreign_keys="Complaint.assigned_to"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "zone": self.zone or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Complaint(db.Model):
    __tablename__ = "complaint"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, default="")
    image_url = db.Column(db.String(255), default="")
    ai_tag = db.Column(db.String(30), default="")

    # NLP fields
    priority = db.Column(db.String(10), default="medium")
    nlp_category = db.Column(db.String(50), default="")
    keywords = db.Column(db.String(255), default="")
    language = db.Column(db.String(10), default="english")

    lat = db.Column(db.Float, default=0)
    lng = db.Column(db.Float, default=0)
    address = db.Column(db.String(255), default="")

    status = db.Column(db.String(20), default="submitted")

    # Worker assignment fields
    assigned_to = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    assigned_at = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    proof_image_url = db.Column(db.String(255), default="")
    worker_remarks = db.Column(db.Text, default="")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    logs = db.relationship(
        "StatusLog",
        backref="complaint",
        lazy=True,
        cascade="all, delete-orphan"
    )

    feedback = db.relationship(
        "Feedback",
        backref="complaint",
        uselist=False,
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self, with_logs=False):
        data = {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "user_id": self.user_id,
            "category": self.category,
            "description": self.description,
            "image_url": self.image_url,
            "ai_tag": self.ai_tag or "",
            "priority": self.priority or "medium",
            "nlp_category": self.nlp_category or "",
            "keywords": self.keywords or "",
            "language": self.language or "english",
            "lat": self.lat,
            "lng": self.lng,
            "address": self.address,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "proof_image_url": self.proof_image_url or "",
            "worker_remarks": self.worker_remarks or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "feedback": self.feedback.to_dict() if self.feedback else None,
        }
        if with_logs:
            data["timeline"] = [log.to_dict() for log in self.logs]
        return data


class StatusLog(db.Model):
    __tablename__ = "status_log"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey("complaint.id"),
        nullable=False
    )
    old_status = db.Column(db.String(20), default="")
    new_status = db.Column(db.String(20), nullable=False)
    remark = db.Column(db.String(255), default="")
    changed_by = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "remark": self.remark,
            "changed_by": self.changed_by,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey("complaint.id"),
        unique=True,
        nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }