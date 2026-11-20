import os
import pymupdf

def pdf_reader(file_path):
    '''
    This Function uses fitz library to read the pdf file and store the text inside the pdf as a string, return type String.
    '''
    
    doc = pymupdf.open(file_path)
    
    text = ""
    
    for i in doc:
        text+=i.get_text()
    
    doc.close()
    
    return text