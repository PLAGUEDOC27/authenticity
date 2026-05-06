import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_FILE_SIZE_MB = 10


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file(file):
    if not file or file.filename == "":
        return False, "No file selected"

    if not allowed_file(file.filename):
        return False, "Invalid file type. Only PDF, DOCX, and TXT are allowed."

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size == 0:
        return False, "File is empty"

    if size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB."

    safe_name = secure_filename(file.filename)

    return True, safe_name

def generate_ats_explanation(score, matched, missing):

    explanation = []

    if score >= 75:
        explanation.append("Strong match for the job description.")
    elif score >= 50:
        explanation.append("Moderate match. Some improvements needed.")
    else:
        explanation.append("Weak match. Significant gaps detected.")

    if matched:
        explanation.append(
            f"Matches {len(matched)} key skills such as {', '.join(matched[:3])}."
        )

    if missing:
        explanation.append(
            f"Missing important skills like {', '.join(missing[:3])}."
        )

    if score < 40:
        explanation.append("Consider adding more relevant experience and technologies.")

    return " ".join(explanation)