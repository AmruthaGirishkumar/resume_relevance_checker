import io
import docx
from PyPDF2 import PdfReader

def extract_text(uploaded_file):
    """
    Extract text from uploaded_file (txt, pdf, or docx).
    uploaded_file is a Streamlit UploadedFile object.
    """
    if uploaded_file.type == "text/plain":
        return uploaded_file.getvalue().decode("utf-8")
    
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
        return "\n".join([para.text for para in doc.paragraphs])
    
    elif uploaded_file.type == "application/pdf":
        reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    else:
        return ""
