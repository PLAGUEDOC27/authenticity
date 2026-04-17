from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash

from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from extensions import db, jwt
from models.user import User
from models.document import Document

from utils.text_extractor import extract_text_from_file
from utils.ai_detector import ai_probability_score
from utils.text_preprocessing import preprocess_text

import io
import base64
import matplotlib.pyplot as plt
import numpy as np

from utils.plagiarism_engine import check_plagiarism
from models.document import Document
import json

from utils.analytics import generate_plagiarism_chart
from functools import wraps
from flask import session, redirect, url_for, abort




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
    
    from routes.document_routes import document_bp
    app.register_blueprint(document_bp)

    from routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    from routes.resume_routes import resume_bp
    app.register_blueprint(resume_bp)

    from routes.auth_routes import auth_bp   # ✅ ADD THIS
    app.register_blueprint(auth_bp)

    # ---------------- ROUTES ----------------
    @app.route("/")
    def index():
        return redirect(url_for("login"))

    def admin_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:
                return redirect(url_for("login"))

            user = User.query.get(session["user_id"])

            if not user or user.role != "admin":
                return abort(403)

            return f(*args, **kwargs)

        return wrapper



    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user = User.query.filter_by(username=username).first()
            if not user or not check_password_hash(user.password_hash, password):
                return render_template("auth.html", error="Invalid credentials")

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role   # ✅ ADD THIS

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("documents.dashboard"))

        return render_template("auth.html")



    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))


    
    @app.route("/admin")
    @admin_required
    def admin_dashboard():

        users = User.query.all()   # ✅ FIX

        total_users = User.query.count()
        total_docs = Document.query.count()
        docs = Document.query.all()

        avg_plagiarism = round(
            sum(d.plagiarism_score for d in docs) / total_docs, 2
        ) if total_docs > 0 else 0

        avg_ai = round(
            sum(d.ai_generated_prob for d in docs) / total_docs, 2
        ) if total_docs > 0 else 0

        max_plagiarism = max(
            (d.plagiarism_score for d in docs),
            default=0
        )

        return render_template(
            "admin_dashboard.html",
            users=users,   # ✅ now valid
            total_users=total_users,
            total_docs=total_docs,
            avg_plagiarism=avg_plagiarism,
            avg_ai=avg_ai,
            max_plagiarism=max_plagiarism,
            documents=docs
        )
    
    @app.route("/similarity-graph")
    def similarity_graph():

        docs = Document.query.filter(Document.original_text.isnot(None)).all()

        if len(docs) < 2:
            return "Not enough documents to compare"

        texts = [d.original_text for d in docs]
        labels = [d.filename for d in docs]

        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        tfidf = TfidfVectorizer()
        matrix = cosine_similarity(tfidf.fit_transform(texts)).tolist()

        return render_template(
            "similarity_graph.html",
            labels=labels,
            matrix=matrix
        )

    @app.route("/compare")
    def compare_docs():

        a = request.args.get("a")
        b = request.args.get("b")

        # 🟡 If no documents selected → show selection UI
        if not a or not b:
            docs = Document.query.all()
            return render_template("compare_select.html", documents=docs)

        # 🟢 If selected → load docs
        doc1 = Document.query.get_or_404(a)
        doc2 = Document.query.get_or_404(b)

        return render_template("compare.html", doc1=doc1, doc2=doc2)
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
