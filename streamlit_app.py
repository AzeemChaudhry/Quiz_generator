import os
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
import json
import google.generativeai as genai
import streamlit as st


gemini_api = st.secrets["gemini"]  
genai.configure(api_key=gemini_api)
model = genai.GenerativeModel("gemini-1.5-flash")

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


def generate_questions(file, question_type): 
    if question_type == "multiple choice":
        examples = [
            {
                "context": "Artificial Intelligence is revolutionizing the tech industry by automating repetitive tasks, enhancing data analysis, and enabling predictive insights. Companies are investing heavily in AI technologies to stay competitive and increase efficiency.",
                "questions": [
                    {
                        "question": "What is one way AI is revolutionizing the tech industry?",
                        "options": [
                            "Automating repetitive tasks",
                            "Reducing employee salaries",
                            "Decreasing internet speed",
                            "Increasing hardware costs"
                        ],
                        "correct_answer": "Automating repetitive tasks"
                    }
                ]
            }
        ]
    elif question_type == "short answer":
        examples = [
            {
                "context": "Artificial Intelligence is enabling new capabilities in technology, such as natural language processing, computer vision, and autonomous systems. It helps companies analyze data more effectively, allowing them to make informed decisions.",
                "questions": [
                    {
                        "question": "What are some capabilities enabled by AI?",
                        "expected_answer": "Natural Language Processing, Computer Vision, Autonomous Systems"
                    }
                ]
            }
        ]
    elif question_type == "long answer":
        examples = [
            {
                "context": "Artificial Intelligence has become a critical driver of innovation across various sectors. In healthcare, AI-powered diagnostic tools are aiding in early disease detection. In finance, AI algorithms are optimizing trading strategies. The article explores how AI adoption is shaping these industries and highlights future trends, such as the integration of AI with IoT to create smart ecosystems.",
                "questions": [
                    {
                        "question": "Discuss how AI is transforming different industries and predict future trends based on current developments.",
                        "expected_answer": "AI is transforming healthcare with diagnostic tools for early disease detection, and finance with algorithmic trading. Future trends include integrating AI with IoT to create smart ecosystems."
                    }
                ]
            }
        ]

    # Generate questions
    context = convert_file_to_text(file)

    prompt = f"""
    Act like an experienced question generation expert specializing in multiple domains, including coding, dry run scenarios, and general knowledge assessments. Your expertise spans creating structured, diverse, and non-repetitive questions tailored for various use cases.

    Objective: Your task is to generate a set of high-quality {question_type} questions based on the provided context. Each question should test a unique aspect of understanding and should not overlap with others.

    Requirements:
    1. Generate **at least 30 unique questions** that are clear and non-redundant.
    2. Each question should follow the style and format of the provided examples.
    3. For coding-related questions, include dry run scenarios, code writing, or debugging tasks.

    - **Examples**:
    {examples}

    - **Context to Generate Questions From**:
    {context}

    ### Step-by-Step Instructions
    1. **Understand the Input**: Carefully read the provided context and examples to grasp the style and complexity expected for the {question_type} questions.
    2. **Generate the Questions**: Create a minimum of 30 questions based on the context, ensuring they are varied and cover different aspects or subtopics within the given context.
        - For coding questions, consider including the following types:
          - Code writing tasks
          - Debugging scenarios
          - Algorithm or function design challenges
    3. **Review for Redundancy**: Make sure no two questions are identical or too similar in wording or intent.
    4. **Format the Output**: Each question should be presented in a numbered list, with clear language and correct syntax. If the questions involve code, ensure the code snippets are enclosed in triple backticks (```) for proper formatting.
    """

    response = model.generate_content(prompt)
    generated_questions = response.text
    return generated_questions


# Streamlit UI
st.title("Question Generator")
st.subheader("Generate Questions Based on Input File")

# Upload file
uploaded_file = st.file_uploader("Choose an input file", type=["pdf", "docx", "csv", "xlsx", "xls", "py", "ipynb"])

# Question type selection
question_type = st.radio("Select the type of question you want to generate:", ["multiple choice", "short answer", "long answer"])

if st.button("Generate Questions"):
    if uploaded_file is not None:
        with st.spinner('Generating questions...'):
            questions = generate_questions(uploaded_file, question_type)
            st.success('Questions generated successfully!')
        
        st.subheader("Generated Questions")
        st.text_area("Questions:", value=questions, height=300)
    else:
        st.warning("Please upload a file before generating questions.")

