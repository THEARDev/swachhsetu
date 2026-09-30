import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory, jsonify, request as req
from flask_cors import CORS
from werkzeug.security import generate_password_hash

from config import Config
from extensions import db, jwt


def create_app():
    frontend_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "frontend"
    )

    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path="",
    )
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    jwt.init_app(app)

    # Blueprints
    from routes.auth import auth_bp
    from routes.complaints import complaints_bp
    from routes.admin import admin_bp
    from routes.awareness import awareness_bp
    from routes.worker import worker_bp
    from routes.chatbot import chatbot_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(complaints_bp, url_prefix="/api/complaints")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(awareness_bp, url_prefix="/api/awareness")
    app.register_blueprint(worker_bp, url_prefix="/api/worker")
    app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.route("/api/health")
    def health():
        return jsonify(status="ok", service="SwachhSetu API"), 200

    @app.route("/")
    def home():
        return app.send_static_file("index.html")

    @app.errorhandler(404)
    def not_found(e):
        if req.path.startswith("/api/"):
            return jsonify(msg="Endpoint not found"), 404
        return app.send_static_file("index.html")

    @app.errorhandler(413)
    def too_large(e):
        return jsonify(msg="File too large (max 5MB)"), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(msg="Internal server error"), 500

    with app.app_context():
        from models import User, Complaint, StatusLog, Feedback  # noqa: F401

        db.create_all()

        if not User.query.filter_by(email="admin@demo.com").first():
            db.session.add(User(
                name="Demo Admin",
                email="admin@demo.com",
                phone="9999999999",
                password_hash=generate_password_hash("admin123"),
                role="admin",
            ))
            print("[SEED] Admin created: admin@demo.com / admin123")

        if not User.query.filter_by(email="citizen@demo.com").first():
            db.session.add(User(
                name="Demo Citizen",
                email="citizen@demo.com",
                phone="8888888888",
                password_hash=generate_password_hash("citizen123"),
                role="citizen",
            ))
            print("[SEED] Citizen created: citizen@demo.com / citizen123")

        if not User.query.filter_by(email="ramesh@demo.com").first():
            db.session.add(User(
                name="Ramesh Kumar",
                email="ramesh@demo.com",
                phone="7777777777",
                password_hash=generate_password_hash("worker123"),
                role="worker",
                zone="Mumbai Zone 3",
            ))
            print("[SEED] Worker 1 created: ramesh@demo.com / worker123")

        if not User.query.filter_by(email="suresh@demo.com").first():
            db.session.add(User(
                name="Suresh Patel",
                email="suresh@demo.com",
                phone="6666666666",
                password_hash=generate_password_hash("worker123"),
                role="worker",
                zone="Mumbai Zone 5",
            ))
            print("[SEED] Worker 2 created: suresh@demo.com / worker123")

        db.session.commit()

    return app


if __name__ == "__main__":
    import webbrowser
    from threading import Timer

    app = create_app()

    print("\n" + "=" * 55)
    print("  🌿 SwachhSetu Backend running")
    print("  → http://localhost:5000")
    print("  → Admin:   admin@demo.com / admin123")
    print("  → Citizen: citizen@demo.com / citizen123")
    print("  → Worker:  ramesh@demo.com / worker123")
    print("=" * 55 + "\n")

    def open_browser():
        webbrowser.open("http://localhost:5000")

    Timer(1.5, open_browser).start()

    app.run(debug=True, port=5000, use_reloader=False)