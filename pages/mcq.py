import streamlit as st
from langchain.schema import HumanMessage
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import hashlib
import random

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Step 1: PDF Processing Functions

# def get_pdf_text(pdf_docs):
#     """Extract text from uploaded PDF files."""
#     text = ""
#     for pdf in pdf_docs:
#         pdf_reader = PdfReader(pdf)
#         for page in pdf_reader.pages:
#             text += page.extract_text() or ""
#     return text.strip()


def get_pdf_text(pdf_docs, start_page, end_page):
    """Extract text from selected page range of uploaded PDF files."""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        num_pages = len(pdf_reader.pages)

        # Ensure the page range is within bounds
        start_page = max(1, min(start_page, num_pages))
        end_page = max(1, min(end_page, num_pages))

        for i in range(start_page - 1, end_page):  # Convert 1-based index to 0-based
            text += pdf_reader.pages[i].extract_text() or ""
    return text.strip()

def get_text_chunks(text):
    """Split text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=500)
    return text_splitter.split_text(text)

# Step 2: Generate MCQs Only

def generate_mcq_questions(text_chunks, num_questions):
    """Generate Multiple-Choice Questions (MCQs) only."""
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.5)

    prompt_template = f"""
    Based on the following text, generate {num_questions} high-quality multiple-choice questions (MCQs).
    Ensure each question has exactly **four options** and a **single correct answer**.
    
    **Format (strictly follow this format):**
    
    question: <question_text>
    option: <option1>
    option: <option2>
    option: <option3>
    option: <option4>
    answer: <correct_option>
    
    **Context:**  
    {{context}}
    
    **Questions:**  
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
    context = " ".join(text_chunks[:3])  # Limiting context size
    formatted_prompt = prompt.format(context=context)

    input_message = HumanMessage(content=formatted_prompt)
    response = model([input_message])
    return response.content if hasattr(response, "content") else response

# Step 3: Parse Questions into JSON

def parse_mcq_questions(questions_text):
    """Extract MCQs in structured format."""
    questions_json = []
    question_blocks = questions_text.strip().split("\n\n")

    for block in question_blocks:
        question_text = None
        options = []
        correct_answer = None

        lines = block.strip().split("\n")
        for line in lines:
            if line.startswith("question:") and question_text is None:
                question_text = line.replace("question:", "").strip()
            elif line.startswith("option:"):
                option_text = line.replace("option:", "").strip()
                if option_text not in options:
                    options.append(option_text)
            elif line.startswith("answer:") and correct_answer is None:
                correct_answer = line.replace("answer:", "").strip()

        # Validate and append to JSON
        if question_text and correct_answer and len(options) == 4:
            random.shuffle(options)  # Shuffle answer order
            questions_json.append({
                "type": "mcq",
                "question": question_text,
                "options": options,
                "answer": correct_answer
            })
        else:
            st.warning(f"Skipping invalid question block:\n{block}")

    return questions_json

# Step 4: Generate Downloadable PDF

def generate_pdf(questions_json):
    """Generate a PDF containing the quiz questions and the answer key."""
    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y_position = height - 50  

    # Write Quiz Questions
    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(50, y_position, "Quiz Questions")
    pdf_canvas.setFont("Helvetica", 10)
    y_position -= 30

    for i, question in enumerate(questions_json):
        if y_position < 50:
            pdf_canvas.showPage()
            y_position = height - 50

        pdf_canvas.drawString(50, y_position, f"Q{i + 1}: {question['question']}")
        y_position -= 15
        for option in question['options']:
            pdf_canvas.drawString(70, y_position, f"- {option}")
            y_position -= 15
        y_position -= 10

    # Add Answer Key
    if y_position < 100:
        pdf_canvas.showPage()
        y_position = height - 50

    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(50, y_position, "Answer Key")
    pdf_canvas.setFont("Helvetica", 10)
    y_position -= 30

    for i, question in enumerate(questions_json):
        if y_position < 50:
            pdf_canvas.showPage()
            y_position = height - 50

        pdf_canvas.drawString(50, y_position, f"Q{i + 1}: {question['answer']}")
        y_position -= 15

    pdf_canvas.save()
    buffer.seek(0)
    return buffer

# Step 5: Conduct MCQ Quiz

def conduct_quiz(questions):
    """Display MCQ quiz and collect user answers."""
    user_answers = {}
    for i, q in enumerate(questions):
        st.subheader(f"Question {i+1}")
        st.write(q["question"])
        user_answers[i] = st.radio("Choose an answer:", q["options"], key=f"q{i}")
    return user_answers

def calculate_score(questions, user_answers):
    """Calculate quiz score."""
    score = 0
    correct_answers = []

    for i, q in enumerate(questions):
        correct_answer = q["answer"]
        if user_answers.get(i) and user_answers[i].strip().lower() == correct_answer.strip().lower():
            score += 1
        correct_answers.append((q["question"], correct_answer))

    return score, correct_answers

# Step 6: Main Streamlit App

def main():
    st.title("MCQ Quiz Generator")
    st.sidebar.title("Menu")
    option = st.sidebar.radio("Choose an option", ["Generate MCQs", "Take Quiz"])

    # Generate MCQs
    if option == "Generate MCQs":
        pdf_docs = st.sidebar.file_uploader(
            "Upload your PDF Files and Click on the Submit & Process Button",
            accept_multiple_files=True
        )
        num_questions = st.sidebar.number_input("Number of questions:", min_value=1, max_value=50, value=5, step=1)
        
        start_page = st.sidebar.number_input("Start Page:", min_value=1, value=1)
        end_page = st.sidebar.number_input("End Page:", min_value=1, value=10)

        if st.sidebar.button("Submit & Process"):
            if pdf_docs:
                with st.spinner("Processing..."):
                    # raw_text = get_pdf_text(pdf_docs)
                    raw_text = get_pdf_text(pdf_docs, start_page, end_page)
                    text_chunks = get_text_chunks(raw_text)
                    questions_text = generate_mcq_questions(text_chunks, num_questions)

                    if questions_text:
                        questions_json = parse_mcq_questions(questions_text)
                        st.session_state.questions_json = questions_json
                        st.success("MCQs Generated Successfully!")

                        # Generate PDF
                        pdf_buffer = generate_pdf(questions_json)
                        st.download_button(
                            label="Download Questions and Answer Key as PDF",
                            data=pdf_buffer,
                            file_name="mcq_quiz_with_answers.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("No valid MCQs generated. Please try again.")
            else:
                st.error("Please upload at least one PDF file.")

    # Take Quiz
    if option == "Take Quiz":
        if "questions_json" in st.session_state:
            st.write("### Quiz")
            user_answers = conduct_quiz(st.session_state.questions_json)

            if st.button("Submit Quiz"):
                score, correct_answers = calculate_score(st.session_state.questions_json, user_answers)
                st.success(f"You scored {score}/{len(st.session_state.questions_json)}!")
                st.write("### Correct Answers:")
                for q, correct in correct_answers:
                    st.write(f"- **{q}**: {correct}")
        else:
            st.info("Generate MCQs first to take the quiz.")

if __name__ == "__main__":
    main()
