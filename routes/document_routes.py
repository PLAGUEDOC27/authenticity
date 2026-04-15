import os
from flask import Blueprint, request, current_app, render_template, flash, redirect, url_for, session
from werkzeug.utils import secure_filename

from extensions import db
from models.document import Document

from utils.text_extractor import extract_text_from_file
from utils.text_preprocessing import preprocess_text
from utils.plagiarism_engine import check_plagiarism
from utils.ai_detector import ai_probability_score
import json

document_bp = Blueprint("documents", __name__)

ALLOWED_EXT = {"pdf", "docx", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# =========================
# 📤 UPLOAD DOCUMENT
# =========================
@document_bp.route("/documents/upload", methods=["GET", "POST"])
def upload_document():

    # 🔐 SESSION CHECK (REPLACES JWT)
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("upload.html")

    # -------- FILE VALIDATION --------
    if "file" not in request.files:
        flash("No file detected. Please select a file to upload.", "danger")
        return redirect(url_for("documents.upload_document"))

    file = request.files["file"]

    if file.filename == "":
        flash("No file selected. Please choose a file.", "warning")
        return redirect(url_for("documents.upload_document"))

    if not allowed_file(file.filename):
        flash("Unsupported file type. Allowed formats: PDF, DOCX, TXT.", "danger")
        return redirect(url_for("documents.upload_document"))

    # -------- SAVE FILE --------
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    path = os.path.join(upload_folder, filename)
    file.save(path)

    ext = filename.rsplit(".", 1)[1].lower()

    # 🔐 GET USER FROM SESSION
    user_id = session.get("user_id")

    # -------- CREATE DB ENTRY --------
    doc = Document(
        user_id=user_id,
        filename=filename,
        file_type=ext
    )
    db.session.add(doc)
    db.session.commit()

    # -------- TEXT EXTRACTION --------
    try:
        raw_text = extract_text_from_file(path)

        if not raw_text or not raw_text.strip():
            flash("We couldn't extract readable content from your file.", "warning")
            return redirect(url_for("documents.upload_document"))

    except Exception:
        flash("Error processing file. The file may be corrupted.", "danger")
        return redirect(url_for("documents.upload_document"))

    # -------- PREPROCESS --------
    clean_text = preprocess_text(raw_text)

    # -------- PLAGIARISM --------
    existing_docs = Document.query.filter(
        Document.original_text.isnot(None),
        Document.id != doc.id
    ).all()

    plagiarism_score, similarity_report = check_plagiarism(clean_text, existing_docs)


    # -------- AI DETECTION --------
    ai_prob = ai_probability_score(clean_text)

    # -------- SAVE RESULTS --------
    doc.original_text = clean_text
    doc.plagiarism_score = plagiarism_score
    doc.similarity_report = json.dumps(similarity_report)
    doc.ai_generated_prob = ai_prob

    db.session.commit()

    flash("File uploaded and analyzed successfully!", "success")

    return redirect(url_for("documents.dashboard"))


# =========================
# 📄 DOCUMENT LIST
# =========================
@document_bp.route("/documents")
def documents():

    if "user_id" not in session:
        return redirect(url_for("login"))

    docs = Document.query.order_by(Document.id.desc()).all()
    return render_template("documents.html", documents=docs)


# =========================
# 📊 DASHBOARD
# =========================
@document_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    documents = Document.query.all()

    docs_for_display = []
    for d in documents:
        docs_for_display.append({
            "id": d.id,
            "filename": d.filename,
            "user_id": d.user_id,
            "text_length": len(d.original_text) if d.original_text else 0,
            "plagiarism_score": d.plagiarism_score or 0.0,
            "ai_generated_prob": round((d.ai_generated_prob or 0.0) * 100, 2)
        })

    return render_template("dashboard.html", documents=docs_for_display)