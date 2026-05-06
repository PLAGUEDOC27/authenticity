from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def generate_pdf(doc, report):

    buffer = BytesIO()

    pdf = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = []

    # TITLE
    content.append(Paragraph(f"Plagiarism Report: {doc.filename}", styles["Title"]))
    content.append(Spacer(1, 12))

    # OVERALL SCORE
    content.append(Paragraph(
        f"<b>Overall Similarity:</b> {report['overall_score']}%",
        styles["BodyText"]
    ))
    content.append(Paragraph(f"<b> AI Probability:</b> {doc.ai_generated_prob}%", styles["BodyText"]))
    content.append(Spacer(1, 16))

    # MATCHES
    matches = report.get("matches", [])

    if not matches:
        content.append(Paragraph("No significant matches found.", styles["BodyText"]))
    else:
        for item in matches:

            text = f"""
            <b>Similarity:</b> {item['score']}% <br/>
            <b>Source:</b> {item['source_document']} <br/>
            <b>Matched Sentence:</b> {item['sentence']} <br/>
            <b>Source Sentence:</b> {item['source_sentence']} <br/>
            <br/>
            """

            content.append(Paragraph(text, styles["BodyText"]))
            content.append(Spacer(1, 10))

    pdf.build(content)

    buffer.seek(0)
    return buffer