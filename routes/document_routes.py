import os
from flask import Blueprint, request, jsonify, current_app, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from extensions import db
from models.document import Document

from utils.text_extractor import extract_text
from utils.text_preprocessing import preprocess_text
from utils.plagiarism import calculate_plagiarism

document_bp = Blueprint("documents", __name__)

ALLOWED_EXT = {"pdf", "docx", "txt"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@document_bp.route("/documents/upload", methods=["POST"])
@jwt_required()
def upload_document():

    # ---- file validation (unchanged) ----
    if "file" not in request.files:
        return jsonify({"msg": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"msg": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"msg": "Unsupported file type"}), 400

    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    path = os.path.join(upload_folder, filename)
    file.save(path)

    ext = filename.rsplit(".", 1)[1].lower()
    user_id = get_jwt_identity()

    # ---- create DB row first ----
    doc = Document(
        user_id=user_id,
        filename=filename,
        file_type=ext
    )
    db.session.add(doc)
    db.session.commit()

    # ==================================================
    # ✅ PLACE THE CODE *HERE* (THIS IS THE CORRECT SPOT)
    # ==================================================

    raw_text = extract_text(path, ext)
    print("RAW TEXT LENGTH:", len(raw_text))

    # Optional but STRONGLY recommended
    if not raw_text or not raw_text.strip():
        return jsonify({"msg": "No readable text found in document"}), 400

    clean_text = preprocess_text(raw_text)

    existing_docs = Document.query.filter(
        Document.original_text.isnot(None),
        Document.id != doc.id
    ).all()

    existing_texts = [d.original_text for d in existing_docs]
    plagiarism_score = calculate_plagiarism(clean_text, existing_texts)

    doc.original_text = clean_text
    doc.plagiarism_score = plagiarism_score
    db.session.commit()

    return jsonify({
        "msg": "File uploaded and analyzed",
        "document_id": doc.id,
        "plagiarism_score": plagiarism_score
    }), 201


@document_bp.route("/dashboard", methods=["GET"])
def dashboard():
    documents = Document.query.all()

    docs_for_display = []
    for d in documents:
        docs_for_display.append({
            "id": d.id,
            "filename": d.filename,
            "user_id": d.user_id,
            "text_length": len(d.original_text) if d.original_text else 0,
            "plagiarism_score": d.plagiarism_score or 0.0
        })

    return render_template("dashboard.html", documents=docs_for_display)
