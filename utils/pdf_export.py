from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(doc, report, filename):

    pdf = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph(f"Plagiarism Report: {doc.filename}", styles["Title"]))
    content.append(Spacer(1, 12))

    for item in report:

        text = f"""
        <b>Sentence:</b> {item['sentence']} <br/>
        <b>Similarity:</b> {item['similarity']}% <br/>
        <b>Source:</b> {item['source_document']} <br/>
        <br/>
        """

        content.append(Paragraph(text, styles["BodyText"]))
        content.append(Spacer(1, 10))

    pdf.build(content)
    return filename