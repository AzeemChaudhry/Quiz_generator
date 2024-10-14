pip install python-docx
import os
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
import json
import google.generativeai as genai
import streamlit as st
import file_reading as file
import generate_questions as generator


gemini_api = st.secrets["gemini"]  
genai.configure(api_key=gemini_api)
model = genai.GenerativeModel("gemini-1.5-flash")







# Streamlit UI
st.title("Question Generator")
st.subheader("Generate Questions Based on Input File")

# Upload file
uploaded_file = st.file_uploader("Choose an input file", type=["pdf", "docx", "csv", "xlsx", "xls", "py", "ipynb"])

# Question type selection
question_type = st.radio("Select the type of question you want to generate:", ["multiple choice", "short answer", "long answer"])

if st.button("Generate Questions"):
    if uploaded_file is not None:
        progress_bar = st.progress(0) 
        progress_bar.progress(20)  
        #st.wait(3)
        progress_bar.progress(50)  
        
        # Simulate progress during question generation
        questions = generator.generate_questions(uploaded_file, question_type)  # Generate once
        
        progress_bar.progress(90)  # 90% - Finalizing output
        
        st.success('Questions generated successfully!')
        progress_bar.progress(100)  # Complete progress
        
        st.subheader("Generated Questions")
        st.text_area("Questions:", value=questions, height=300)
        
        progress_bar.empty()  # Clear the progress bar
    else:
        st.warning("Please upload a file before generating questions.")
