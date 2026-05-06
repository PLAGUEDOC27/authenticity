import os
import json
from collections import defaultdict

from flask import Blueprint, request, current_app, render_template, flash, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename

from extensions import db
from models.document import Document

from utils.text_extractor import extract_text_from_file
from utils.text_preprocessing import preprocess_text
from utils.plagiarism_engine import check_plagiarism
from utils.ai_detector import ai_probability_score
from utils.report_engine import generate_plagiarism_report
from utils.pdf_export import generate_pdf
from utils.scoring import compute_jd_score
from utils.file_validator import validate_file


document_bp = Blueprint("documents", __name__)

ALLOWED_EXT = {"pdf", "docx", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# =========================
# 📤 UPLOAD DOCUMENT
# =========================
@document_bp.route("/documents/upload", methods=["GET", "POST"])
def upload_document():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("upload.html")

    if "file" not in request.files:
        flash("No file detected.", "danger")
        return redirect(url_for("documents.upload_document"))

    file = request.files["file"]

    valid, result = validate_file(file)

    if not valid:
        flash(result, "danger")
        return redirect(url_for("documents.upload_document"))

    filename = result

    upload_folder = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    path = os.path.join(upload_folder, filename)
    file.save(path)

    user_id = session.get("user_id")

    doc = Document(user_id=user_id, filename=filename, file_type=filename.rsplit(".", 1)[1].lower())
    db.session.add(doc)
    db.session.commit()

    try:
        raw_text = extract_text_from_file(path)
        if not raw_text or not raw_text.strip():
            flash("No readable content found.", "warning")
            return redirect(url_for("documents.upload_document"))
    except Exception:
        flash("File processing error.", "danger")
        return redirect(url_for("documents.upload_document"))

    clean_text = preprocess_text(raw_text)

    existing_docs = Document.query.filter(
        Document.original_text.isnot(None),
        Document.id != doc.id
    ).all()

    plagiarism_score, similarity_report = check_plagiarism(clean_text, existing_docs)

    ai_prob = ai_probability_score(clean_text)

    doc.original_text = clean_text
    doc.plagiarism_score = plagiarism_score
    doc.similarity_report = json.dumps(similarity_report)
    doc.ai_generated_prob = ai_prob

    db.session.commit()

    flash("File uploaded and analyzed successfully!", "success")
    return redirect(url_for("documents.documents"))


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

    total_docs = len(documents)

    # SAFE calculations
    if total_docs > 0:
        avg_plagiarism = round(
            sum(d.plagiarism_score or 0 for d in documents) / total_docs, 2
        )
        avg_ai = round(
            sum(d.ai_generated_prob or 0 for d in documents) / total_docs, 2
        )
    else:
        avg_plagiarism = 0
        avg_ai = 0

    # CHART DATA
    labels = [d.filename for d in documents]
    values = [d.plagiarism_score or 0 for d in documents]

    # RESUMES (filtered from same table)
    resumes = Document.query.filter_by(type="resume").all()

    for r in resumes:
        r.jd_score = compute_jd_score(r.original_text)

    return render_template(
        "dashboard.html",
        total_docs=total_docs,
        avg_plagiarism=avg_plagiarism,
        avg_ai=avg_ai,
        labels=labels,
        values=values,
        resumes=resumes
    )

# =========================
# 📄 DOCUMENT DETAIL (TURNITIN VIEW FIX)
# =========================
@document_bp.route("/document/<int:doc_id>")
def document_detail(doc_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    doc = Document.query.get_or_404(doc_id)

    # Load similarity report
    report = []
    if doc.similarity_report:
        try:
            report = json.loads(doc.similarity_report)
        except:
            report = []

    # 🔥 BUILD SENTENCE STRUCTURE (THIS IS KEY)
    sentences = []
    raw_sentences = doc.original_text.split(".")

    for s in raw_sentences:
        clean = s.strip()
        if not clean:
            continue

        matched = False
        score = 0
        source = ""

        for item in report:
            if item["sentence"] in clean.lower():
                matched = True
                score = item["similarity"]
                source = item["source_document"]
                break

        sentences.append({
            "text": clean + ". ",
            "score": score,
            "source": source
        })

    ai_score = round(doc.ai_generated_prob or 0, 2)

    return render_template(
        "document_detail.html",
        document=doc,
        sentences=sentences,   # ✅ REQUIRED
        ai_score=ai_score
    )


# =========================
# 📄 PDF DOWNLOAD
# =========================
@document_bp.route("/report/<int:doc_id>/download")
def download_plagiarism_report(doc_id):

    doc = Document.query.get_or_404(doc_id)

    source_docs = Document.query.filter(
        Document.original_text.isnot(None)
    ).all()

    report = generate_plagiarism_report(doc, source_docs)

    pdf_buffer = generate_pdf(doc, report)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"plagiarism_report_{doc.id}.pdf",
        mimetype="application/pdf"
    )