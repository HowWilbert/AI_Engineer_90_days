import os
from docx import Document

def read_document(file_path):
    doc = Document(file_path)
    
    text = ""
    
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    # skills and education are often placed inside tables
    for table in doc.tables:
        for row in table.rows:
            text += " | ".join(cell.text for cell in row.cells) + "\n"

    return text
