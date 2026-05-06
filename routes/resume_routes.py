from flask import Blueprint, render_template, request, redirect, url_for
from models.document import Document
from extensions import db
from utils.text_extractor import extract_text_from_file as extract_text
from utils.resume_engine import compute_resume_score
from utils.resume_similarity import check_resume_similarity
from utils.ats_engine import compute_ats_score
from utils.skill_extractor import extract_skills
import os
import time
import json
from utils.file_validator import validate_file
from utils.ats_engine import generate_ats_explanation


resume_bp = Blueprint('resume', __name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================================
# UPLOAD RESUMES + JD
# ================================
@resume_bp.route('/resume/upload', methods=['GET', 'POST'])
def upload_resumes():

    if request.method == 'POST':

        jd_file = request.files.get('jd')
        resume_files = request.files.getlist('resumes')

        if not jd_file or not resume_files:
            return "Please upload JD and resumes", 400

        group_id = int(time.time())

        # ================= JD =================
        valid, result = validate_file(jd_file)
        if not valid:
            return result, 400

        jd_filename = f"{group_id}_{result}"
        jd_path = os.path.join(UPLOAD_FOLDER, jd_filename)
        jd_file.save(jd_path)

        jd_text = extract_text(jd_path)

        jd_doc = Document(
            user_id=1,
            filename=jd_filename,
            file_type=jd_file.filename.split('.')[-1],
            original_text=jd_text,
            type='jd',
            group_id=group_id
        )
        db.session.add(jd_doc)

        # ================= RESUMES =================
        for file in resume_files:

            valid, result = validate_file(file)
            if not valid:
                return result , 400
            filename = f"{group_id}_{result}"
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)

            text = extract_text(path)

            doc = Document(
                user_id=1,
                filename=filename,
                file_type=file.filename.split('.')[-1],
                original_text=text,
                type='resume',
                group_id=group_id
            )

            db.session.add(doc)

        db.session.commit()

        run_pipeline(group_id)

        return redirect(url_for('resume.results', group_id=group_id))

    return render_template('resume_upload.html')


# ================================
# PIPELINE
# ================================
def run_pipeline(group_id):

    docs = Document.query.filter_by(group_id=group_id).all()

    jd = next(d for d in docs if d.type == 'jd')
    resumes = [d for d in docs if d.type == 'resume']

    jd_skills = set(extract_skills(jd.original_text))

    for r in resumes:

        # ATS SCORE
        score, matched, missing = compute_ats_score(
            jd.original_text,
            r.original_text
        )

        r.match_score = score

        # SKILLS
        resume_skills = set(extract_skills(r.original_text))

        matched_skills = list(jd_skills & resume_skills)
        missing_skills = list(jd_skills - resume_skills)

        # STORE JSON
        explanation = generate_ats_explanation(score, matched_skills, missing_skills)

        r.similarity_report = json.dumps({
            "matched" : matched_skills,
            "missing" : missing_skills,
            "explanation" : explanation
        })

    db.session.commit()

    check_resume_similarity(resumes)


# ================================
# RESULTS
# ================================
@resume_bp.route('/resume/results/<int:group_id>')
def results(group_id):

    resumes = Document.query.filter_by(
        group_id=group_id,
        type='resume'
    ).order_by(Document.match_score.desc()).all()

    import json

    for r in resumes:
        # SAFETY: handle both DB string and missing field
        raw = getattr(r, "similarity_report", None)

        if raw:
            try:
                r.similarity_report = json.loads(raw)
            except:
                r.similarity_report = {"matched": [], "missing": []}
        else:
            r.similarity_report = {"matched": [], "missing": []}

    similarities = check_resume_similarity(resumes)

    return render_template(
        'resume_results.html',
        resumes=resumes,
        similarities=similarities
    )

@resume_bp.route('/resume/detail/<int:doc_id>')
def resume_detail(doc_id):
    doc = Document.query.get_or_404(doc_id)

    data = {}
    if doc.similarity_report:
        try:
            data = json.loads(doc.similarity_report)
        except:
            data = {}

    return render_template(
        'resume_detail.html',
        resume=doc,
        matched=data.get("matched", []),
        missing=data.get("missing", []),
        explanation=data.get("explanation",""),
        score=doc.match_score or 0
    )