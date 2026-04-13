import fitz

def parse_resume(pdf_path:str):
    """Extracts raw text from a PDF file"""
    try:
        doc = fitz.open(pdf_path)
        return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"Error Parsing PDF: {e}")
        return None