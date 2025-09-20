import io
import docx
import pdfplumber
from PyPDF2 import PdfReader

def extract_text(uploaded_file):
    """Return extracted text from a Streamlit / FastAPI upload file-like object."""
    ftype = uploaded_file.type if hasattr(uploaded_file, "type") else None
    raw = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file.getvalue()

    # Try pdfplumber for PDFs
    if ftype == "application/pdf" or (isinstance(raw, (bytes, bytearray)) and raw[:4] == b"%PDF"):
        try:
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n".join(pages)
        except Exception:
            # fallback to PyPDF2
            try:
                reader = PdfReader(io.BytesIO(raw))
                return "\n".join([(p.extract_text() or "") for p in reader.pages])
            except Exception:
                return ""

    # DOCX
    if ftype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or uploaded_file.filename.endswith(".docx"):
        try:
            doc = docx.Document(io.BytesIO(raw))
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            return ""

    # TXT
    try:
        return raw.decode("utf-8", errors="ignore")
    except Exception:
        return str(raw)
