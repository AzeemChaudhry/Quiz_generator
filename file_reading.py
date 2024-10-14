

import os
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
import json
import google.generativeai as genai
import streamlit as st

def convert_file_to_text(input_file):
    _, file_extension = os.path.splitext(input_file.name)

    if file_extension == '.py':
        content = input_file.read().decode('utf-8')

    elif file_extension == '.ipynb':
        notebook = json.load(input_file)
        code_cells = [
            "\n".join(line.strip() for line in cell['source'])
            for cell in notebook.get('cells', []) if cell['cell_type'] == 'code'
        ]
        content = "\n\n".join(code_cells)

    elif file_extension == '.pdf':
        content = ""
        reader = PdfReader(input_file)
        for page in reader.pages:
            content += page.extract_text() + "\n"
        return content

    elif file_extension == '.docx':
        doc = Document(input_file)
        content = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return content

    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(input_file)
        content = df.to_string(index=False)
        return content

    elif file_extension == '.csv':
        df = pd.read_csv(input_file)
        content = df.to_string(index=False)
        return content

    else:
        raise ValueError("Unsupported file format: {}".format(file_extension))