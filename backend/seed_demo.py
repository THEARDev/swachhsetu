"""
SwachhSetu — Demo Data Seeder
15 realistic complaints add karta hai with:
- Various statuses (submitted, in_progress, resolved)
- Various priorities (high, medium, low)
- Hindi + English mix
- Worker assignments
- Feedback ratings
- Realistic timestamps
"""

import uuid
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, Complaint, StatusLog, Feedback


# ============================================
# DEMO COMPLAINTS DATA (15 total)
# ============================================
COMPLAINTS_DATA = [
    # ───────── MUMBAI (5) ─────────
    {
        "category": "overflow",
        "description": "School ke paas bin overflow ho raha hai, bachhe pareshan hain",
        "lat": 19.1197, "lng": 72.8464, "address": "Andheri East, Mumbai",
        "status": "resolved", "priority": "high", "ai_tag": "wet",
        "nlp_category": "overflow", "language": "english",
        "keywords": "school, bin, overflow, bachhe",
        "worker_email": "ramesh@demo.com",
        "days_ago": 5, "feedback_rating": 5,
        "feedback_comment": "Fast response, school saaf ho gaya!",
    },
    {
        "category": "road",
        "description": "MG Road pe kachra pheela hua hai, vehicles slip ho rahi",
        "lat": 19.0760, "lng": 72.8777, "address": "MG Road, Mumbai",
        "status": "resolved", "priority": "high", "ai_tag": "dry",
        "nlp_category": "road", "language": "english",
        "keywords": "road, kachra, pheela, vehicles",
        "worker_email": "ramesh@demo.com",
        "days_ago": 4, "feedback_rating": 4,
        "feedback_comment": "Good work",
    },
    {
        "category": "overflow",
        "description": "मेरी गली में कचरा भरा हुआ है, सफाई करवाइए",
        "lat": 19.0596, "lng": 72.8295, "address": "Bandra West, Mumbai",
        "status": "in_progress", "priority": "high", "ai_tag": "wet",
        "nlp_category": "overflow", "language": "hindi",
        "keywords": "गली, कचरा, भरा, सफाई",
        "worker_email": "ramesh@demo.com",
        "days_ago": 2,
    },
    {
        "category": "illegal",
        "description": "Construction waste illegally dumped near hospital",
        "lat": 19.0176, "lng": 72.8562, "address": "Dadar, Mumbai",
        "status": "resolved", "priority": "high", "ai_tag": "hazardous",
        "nlp_category": "illegal", "language": "english",
        "keywords": "construction, waste, illegally, hospital",
        "worker_email": "ramesh@demo.com",
        "days_ago": 6, "feedback_rating": 5,
        "feedback_comment": "Hospital area clean ho gaya, thanks!",
    },
    {
        "category": "missed",
        "description": "3 din se garbage pickup nahi hua society se",
        "lat": 19.0677, "lng": 72.8356, "address": "Khar, Mumbai",
        "status": "submitted", "priority": "medium", "ai_tag": "dry",
        "nlp_category": "missed", "language": "english",
        "keywords": "din, garbage, pickup, society",
        "worker_email": None,
        "days_ago": 1,
    },

    # ───────── DELHI (3) ─────────
    {
        "category": "road",
        "description": "Connaught Place pe garbage on road, tourists visiting",
        "lat": 28.6139, "lng": 77.2090, "address": "Connaught Place, Delhi",
        "status": "in_progress", "priority": "high", "ai_tag": "dry",
        "nlp_category": "road", "language": "english",
        "keywords": "connaught, place, garbage, road",
        "worker_email": "suresh@demo.com",
        "days_ago": 2,
    },
    {
        "category": "overflow",
        "description": "Dustbin full hai market area mein",
        "lat": 28.6519, "lng": 77.1909, "address": "Karol Bagh, Delhi",
        "status": "resolved", "priority": "medium", "ai_tag": "wet",
        "nlp_category": "overflow", "language": "english",
        "keywords": "dustbin, full, market, area",
        "worker_email": "suresh@demo.com",
        "days_ago": 5, "feedback_rating": 4,
        "feedback_comment": "Ok",
    },
    {
        "category": "missed",
        "description": "Garbage truck 5 din se nahi aaya",
        "lat": 28.5700, "lng": 77.2300, "address": "Lajpat Nagar, Delhi",
        "status": "submitted", "priority": "medium", "ai_tag": "dry",
        "nlp_category": "missed", "language": "english",
        "keywords": "garbage, truck, din, nahi",
        "worker_email": None,
        "days_ago": 1,
    },

    # ───────── BENGALURU (3) ─────────
    {
        "category": "overflow",
        "description": "College ke paas dustbin overflow, students pareshan",
        "lat": 12.9352, "lng": 77.6245, "address": "Koramangala, Bengaluru",
        "status": "resolved", "priority": "high", "ai_tag": "wet",
        "nlp_category": "overflow", "language": "english",
        "keywords": "college, dustbin, overflow, students",
        "worker_email": "suresh@demo.com",
        "days_ago": 7, "feedback_rating": 5,
        "feedback_comment": "Students ka problem solve ho gaya!",
    },
    {
        "category": "road",
        "description": "Garbage on road near metro station",
        "lat": 12.9784, "lng": 77.6408, "address": "Indiranagar, Bengaluru",
        "status": "in_progress", "priority": "medium", "ai_tag": "dry",
        "nlp_category": "road", "language": "english",
        "keywords": "garbage, road, metro, station",
        "worker_email": "suresh@demo.com",
        "days_ago": 1,
    },
    {
        "category": "illegal",
        "description": "E-waste illegally dumped near residential area",
        "lat": 12.9698, "lng": 77.7500, "address": "Whitefield, Bengaluru",
        "status": "submitted", "priority": "high", "ai_tag": "hazardous",
        "nlp_category": "illegal", "language": "english",
        "keywords": "e-waste, illegally, dumped, residential",
        "worker_email": None,
        "days_ago": 1,
    },

    # ───────── PUNE (2) ─────────
    {
        "category": "overflow",
        "description": "Society ke bahar bin bhar gaya hai",
        "lat": 18.5204, "lng": 73.8567, "address": "Kothrud, Pune",
        "status": "resolved", "priority": "medium", "ai_tag": "wet",
        "nlp_category": "overflow", "language": "english",
        "keywords": "society, bahar, bin, bhar",
        "worker_email": "ramesh@demo.com",
        "days_ago": 4, "feedback_rating": 4,
        "feedback_comment": "Nice",
    },
    {
        "category": "missed",
        "description": "Small garbage pile near park entrance",
        "lat": 18.5983, "lng": 73.6948, "address": "Hinjewadi, Pune",
        "status": "resolved", "priority": "low", "ai_tag": "dry",
        "nlp_category": "missed", "language": "english",
        "keywords": "small, garbage, pile, park",
        "worker_email": "suresh@demo.com",
        "days_ago": 3, "feedback_rating": 5,
        "feedback_comment": "Quick action",
    },

    # ───────── CHENNAI (1) ─────────
    {
        "category": "road",
        "description": "Marina Beach road pe kachra, tourists aa rahe hain",
        "lat": 13.0500, "lng": 80.2824, "address": "Marina Beach, Chennai",
        "status": "resolved", "priority": "medium", "ai_tag": "dry",
        "nlp_category": "road", "language": "english",
        "keywords": "marina, beach, road, kachra",
        "worker_email": "ramesh@demo.com",
        "days_ago": 5, "feedback_rating": 4,
        "feedback_comment": "Beach area clean",
    },

    # ───────── HYDERABAD (1) ─────────
    {
        "category": "overflow",
        "description": "मेरे मोहल्ले में डिब्बा भरा है, बदबू आ रही है",
        "lat": 17.4126, "lng": 78.4392, "address": "Banjara Hills, Hyderabad",
        "status": "submitted", "priority": "high", "ai_tag": "wet",
        "nlp_category": "overflow", "language": "hindi",
        "keywords": "मोहल्ले, डिब्बा, भरा, बदबू",
        "worker_email": None,
        "days_ago": 1,
    },
]


def generate_ticket_id():
    return "WM" + uuid.uuid4().hex[:8].upper()


def seed_demo_data():
    app = create_app()

    with app.app_context():
        # Get users
        citizen = User.query.filter_by(email="citizen@demo.com").first()
        admin = User.query.filter_by(email="admin@demo.com").first()
        ramesh = User.query.filter_by(email="ramesh@demo.com").first()
        suresh = User.query.filter_by(email="suresh@demo.com").first()

        if not citizen:
            print("❌ Citizen not found. Run backend first to seed users.")
            return

        if not ramesh or not suresh:
            print("❌ Workers not found. Restart backend to seed workers.")
            return

        # Worker map
        worker_map = {
            "ramesh@demo.com": ramesh,
            "suresh@demo.com": suresh,
        }

        print("\n🌱 Seeding 15 demo complaints...\n")

        count = 0
        for data in COMPLAINTS_DATA:
            # Create complaint
            created_at = datetime.utcnow() - timedelta(days=data.get("days_ago", 1))

            worker = worker_map.get(data.get("worker_email"))
            assigned_to = worker.id if worker else None

            # Set timestamps based on status
            assigned_at = None
            started_at = None
            completed_at = None

            if data["status"] in ("acknowledged", "in_progress", "resolved"):
                assigned_at = created_at + timedelta(minutes=30)

            if data["status"] in ("in_progress", "resolved"):
                started_at = created_at + timedelta(hours=2)

            if data["status"] == "resolved":
                completed_at = created_at + timedelta(hours=4)

            complaint = Complaint(
                ticket_id=generate_ticket_id(),
                user_id=citizen.id,
                category=data["category"],
                description=data["description"],
                image_url="",  # No image in seed
                ai_tag=data.get("ai_tag", ""),
                priority=data["priority"],
                nlp_category=data.get("nlp_category", ""),
                keywords=data.get("keywords", ""),
                language=data.get("language", "english"),
                lat=data["lat"],
                lng=data["lng"],
                address=data["address"],
                status=data["status"],
                assigned_to=assigned_to,
                assigned_at=assigned_at,
                started_at=started_at,
                completed_at=completed_at,
                worker_remarks="Task completed by worker" if data["status"] == "resolved" else "",
                created_at=created_at,
                updated_at=completed_at or started_at or assigned_at or created_at,
            )

            db.session.add(complaint)
            db.session.flush()

            # ---- STATUS LOGS ----
            logs = []

            # 1. Submitted log
            logs.append(StatusLog(
                complaint_id=complaint.id,
                old_status="",
                new_status="submitted",
                remark="Complaint received",
                changed_by=citizen.id,
                timestamp=created_at,
            ))

            # 2. Assigned log
            if assigned_at and worker:
                logs.append(StatusLog(
                    complaint_id=complaint.id,
                    old_status="submitted",
                    new_status="acknowledged",
                    remark=f"Assigned to worker: {worker.name}",
                    changed_by=admin.id if admin else citizen.id,
                    timestamp=assigned_at,
                ))

            # 3. Started log
            if started_at and worker:
                logs.append(StatusLog(
                    complaint_id=complaint.id,
                    old_status="acknowledged",
                    new_status="in_progress",
                    remark="Worker started task",
                    changed_by=worker.id,
                    timestamp=started_at,
                ))

            # 4. Resolved log
            if completed_at and worker:
                logs.append(StatusLog(
                    complaint_id=complaint.id,
                    old_status="in_progress",
                    new_status="resolved",
                    remark="Task completed by worker",
                    changed_by=worker.id,
                    timestamp=completed_at,
                ))

            for log in logs:
                db.session.add(log)

            # ---- FEEDBACK ----
            if data.get("feedback_rating") and data["status"] == "resolved":
                fb_time = (completed_at or created_at) + timedelta(hours=1)
                feedback = Feedback(
                    complaint_id=complaint.id,
                    user_id=citizen.id,
                    rating=data["feedback_rating"],
                    comment=data.get("feedback_comment", ""),
                    created_at=fb_time,
                )
                db.session.add(feedback)

            count += 1
            print(f"  ✅ [{count}/15] {complaint.ticket_id} · {data['category']} · {data['priority']} · {data['status']}")

        db.session.commit()

        # ---- SUMMARY ----
        print("\n" + "=" * 55)
        print("  🎉 15 demo complaints added successfully!")
        print("=" * 55)

        total = Complaint.query.count()
        submitted = Complaint.query.filter_by(status="submitted").count()
        in_progress = Complaint.query.filter_by(status="in_progress").count()
        resolved = Complaint.query.filter_by(status="resolved").count()

        high = Complaint.query.filter_by(priority="high").count()
        medium = Complaint.query.filter_by(priority="medium").count()
        low = Complaint.query.filter_by(priority="low").count()

        hindi = Complaint.query.filter_by(language="hindi").count()
        english = Complaint.query.filter_by(language="english").count()

        ramesh_tasks = Complaint.query.filter_by(assigned_to=ramesh.id).count()
        suresh_tasks = Complaint.query.filter_by(assigned_to=suresh.id).count()
        unassigned = Complaint.query.filter_by(assigned_to=None).count()

        feedback_count = Feedback.query.count()
        if feedback_count > 0:
            ratings = [f.rating for f in Feedback.query.all()]
            avg_rating = round(sum(ratings) / len(ratings), 1)
        else:
            avg_rating = 0

        print(f"\n  📊 Summary:")
        print(f"     Total:          {total}")
        print(f"\n     By Status:")
        print(f"       Submitted:    {submitted}")
        print(f"       In Progress:  {in_progress}")
        print(f"       Resolved:     {resolved}")
        print(f"\n     By Priority:")
        print(f"       🔴 High:      {high}")
        print(f"       🟡 Medium:    {medium}")
        print(f"       🟢 Low:       {low}")
        print(f"\n     By Language:")
        print(f"       🇬🇧 English:   {english}")
        print(f"       🇮🇳 Hindi:     {hindi}")
        print(f"\n     Workers:")
        print(f"       Ramesh Kumar: {ramesh_tasks}")
        print(f"       Suresh Patel: {suresh_tasks}")
        print(f"       Unassigned:   {unassigned}")
        print(f"\n     Feedback:       {feedback_count} ratings · Avg {avg_rating} ⭐")
        print("\n" + "=" * 55)
        print("  ✅ Demo ready! Refresh admin dashboard.\n")


if __name__ == "__main__":
    seed_demo_data()