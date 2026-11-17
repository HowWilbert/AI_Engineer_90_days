from pathlib import Path
from utils.docx_reader import read_document
from utils.pdf_reader import pdf_reader

def read_res(file_path):
    file_path = Path(file_path)

    if file_path.suffix.lower() == '.pdf':
        text = pdf_reader(file_path=file_path)
    elif file_path.suffix.lower() == '.docx':
        text = read_document(file_path=file_path)
    elif file_path.suffix.lower() == '.txt':
        text = file_path.read_text(encoding='utf-8')
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    # a scanned pdf has no text layer, so it comes back empty
    if not text.strip():
        raise ValueError(f"No text found in {file_path.name}, it may be a scanned file")

    return text
