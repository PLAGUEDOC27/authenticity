from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from extensions import db, jwt
from models.user import User
from models.document import Document

from utlis.text_extractor import extract_text_from_file
from utlis.plagiarism import calculate_plagiarism,clean_text
from utlis.ai_detector import ai_probability_score




def create_app():
    app = Flask(__name__)
    CORS(app)

    # ---------------- PATHS ----------------
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

    os.makedirs(INSTANCE_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # ---------------- CONFIG ----------------
    app.config["SECRET_KEY"] = "super-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(INSTANCE_DIR, 'site.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

    # ---------------- INIT ----------------
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    # ---------------- ROUTES ----------------
    @app.route("/")
    def index():
        return redirect(url_for("login"))


    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user = User.query.filter_by(username=username).first()
            if not user or not check_password_hash(user.password, password):
                return render_template("auth.html", error="Invalid credentials")

            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("dashboard"))

        return render_template("auth.html")



    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/create_user", methods=["GET", "POST"])
    def create_user():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]

            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()

        if existing_user:
            return render_template("create_user.html", error="Username or Email already exists")

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))


    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("login"))

        docs = Document.query.all()
        return render_template("dashboard.html", documents=docs)

    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if "user_id" not in session:
            return redirect(url_for("login"))

        if request.method == "POST":
            file = request.files.get("file")
            if not file or file.filename == "":
                return "No file selected", 400

            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            # 1️⃣ Extract text
            text = extract_text_from_file(path)

            if not text or not text.strip():
                return "No readable text found", 400

            # 2️⃣ Clean text
            processed_text = clean_text(text)

            # 3️⃣ Get existing documents
            existing_texts = [
                d.original_text
                for d in Document.query.all()
                if d.original_text
            ]

            # 4️⃣ Calculate plagiarism
            plagiarism_score, similarity_report = calculate_plagiarism(
                processed_text,
                existing_texts
            )

            # 5️⃣ Calculate AI probability
            ai_prob = ai_probability_score(text)

            # 6️⃣ Save to DB
            doc = Document(
                user_id=session["user_id"],
                filename=filename,
                file_type=filename.rsplit(".", 1)[-1],
                original_text=processed_text,
                plagiarism_score=plagiarism_score,
                ai_generated_prob=ai_prob
            )

            db.session.add(doc)
            db.session.commit()

            return jsonify({
                "msg": "File uploaded and analyzed",
                "document_id": doc.id,
                "plagiarism_score": plagiarism_score,
                "similarity_report": similarity_report,
                "ai_probability": ai_prob
            }), 201
            return render_template("dashboard.html")
    

        return render_template("upload.html")



    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
