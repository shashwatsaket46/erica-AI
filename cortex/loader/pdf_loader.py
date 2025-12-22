import pdfplumber
import io


# =========================================================
# PDF LOADER
# This function extracts readable text from raw PDF bytes.
# =========================================================
def load_pdf(pdf_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if page_text:
                text += page_text + "\n\n"
    return text
