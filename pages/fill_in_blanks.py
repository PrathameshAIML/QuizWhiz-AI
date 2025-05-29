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

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize session state
if "questions_json" not in st.session_state:
    st.session_state.questions_json = []

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# Extract text from PDF files
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

# Split text into chunks
def get_text_chunks(text):
    """Split text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=500)
    return text_splitter.split_text(text)

# Generate high-quality fill-in-the-blank questions
def generate_fill_in_blank_questions(text_chunks, num_questions):
    """Generate structured, high-standard fill-in-the-blank questions strictly from the text."""
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7)  # Reduce randomness for precision

    prompt_template = f"""
    Generate exactly {num_questions} high-quality fill-in-the-blank questions based **only** on the provided text.

    **Strict Instructions:**
    - question generated should be such that each question should strictly have a blank
    - Use direct references from the text.
    - Maintain high academic quality.
    - Format the output as follows:
    
    **Example Output:**
    Q1. The concept of _____ was introduced by [author/scientist] in [year]. | [correct answer]  
    Q2. In physics, Newton's Second Law states that Force = Mass × _____. | [Acceleration]  
    Q3. The capital of France is _____. | [Paris]  
    
    **Do NOT generate unrelated questions. Only use the given text.**
    
    **Text for Reference:**  
    {{context}}

    **Generate the Questions Below (Follow the Format Strictly):**
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
    
    # Use more text chunks to improve question quality
    context = " ".join(text_chunks[:5])  
    formatted_prompt = prompt.format(context=context)

    input_message = HumanMessage(content=formatted_prompt)
    response = model.invoke([input_message])

    return response.content if hasattr(response, "content") else response

# Parse structured questions into JSON format
def parse_questions(questions_text):
    """Parse structured fill-in-the-blank questions into a list."""
    questions_list = []

    for line in questions_text.strip().split("\n"):
        parts = line.split("|")
        if len(parts) == 2:
            question = parts[0].strip()
            answer = parts[1].strip()
            questions_list.append({"question": question, "answer": answer})
        else:
            st.warning(f"Skipping invalid question format: {line}")

    return questions_list

# Generate PDF with questions & answers
def generate_pdf(questions_list):
    """Create a PDF quiz with questions and answer key."""
    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y_position = height - 50  

    # Quiz Header
    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(50, y_position, "Fill-in-the-Blank Quiz")
    pdf_canvas.setFont("Helvetica", 10)
    y_position -= 30

    # Write Questions
    for i, question in enumerate(questions_list):
        if y_position < 50:
            pdf_canvas.showPage()
            y_position = height - 50

        pdf_canvas.drawString(50, y_position, f"Q{i + 1}: {question['question']}")
        y_position -= 30

    # Answer Key
    pdf_canvas.showPage()
    y_position = height - 50
    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(50, y_position, "Answer Key")
    pdf_canvas.setFont("Helvetica", 10)
    y_position -= 30

    for i, question in enumerate(questions_list):
        pdf_canvas.drawString(50, y_position, f"Q{i + 1}: {question['answer']}")
        y_position -= 20

    pdf_canvas.save()
    buffer.seek(0)
    return buffer

# Conduct the quiz
def conduct_fill_in_blank_quiz():
    """Display the quiz and collect user responses."""
    user_answers = {}
    for i, q in enumerate(st.session_state.questions_json):
        st.subheader(f"Question {i+1}")
        st.write(q["question"])
        user_answers[i] = st.text_input("Your answer:", key=f"q{i}")

    if st.button("Submit Quiz"):
        st.session_state.user_answers = user_answers
        st.session_state.quiz_submitted = True
        st.rerun()

# Calculate and display quiz score
def calculate_fill_in_blank_score():
    """Calculate the score based on user answers."""
    if not st.session_state.user_answers:
        st.warning("No answers submitted yet.")
        return

    score = 0
    total = len(st.session_state.questions_json)

    for i, q in enumerate(st.session_state.questions_json):
        correct_answer = q["answer"].strip().lower()
        user_answer = st.session_state.user_answers.get(i, "").strip().lower()

        if user_answer == correct_answer:
            score += 1

    st.success(f"You scored {score}/{total}!")

    st.write("### Correct Answers:")
    for i, q in enumerate(st.session_state.questions_json):
        st.write(f"- **{q['question']}**: {q['answer']}")

# Main Streamlit App
def main():
    st.title("📘 AI Fill-in-the-Blank Quiz Generator")
    st.sidebar.title("📌 Menu")
    option = st.sidebar.radio("Choose an option", ["Generate Questions", "Take Quiz"])

    # Generate Questions
    if option == "Generate Questions":
        pdf_docs = st.sidebar.file_uploader("Upload PDF Files", accept_multiple_files=True)
        num_questions = st.sidebar.number_input("Number of questions:", min_value=1, max_value=50, value=5, step=1)
        
        
        start_page = st.sidebar.number_input("Start Page:", min_value=1, value=1)
        end_page = st.sidebar.number_input("End Page:", min_value=1, value=10)

        if st.sidebar.button("Submit & Process"):
            if pdf_docs:
                with st.spinner("Processing..."):
                    # raw_text = get_pdf_text(pdf_docs)
                    raw_text = get_pdf_text(pdf_docs, start_page, end_page)
                    text_chunks = get_text_chunks(raw_text)
                    questions_text = generate_fill_in_blank_questions(text_chunks, num_questions)
                    print(questions_text)
                    if questions_text:
                        st.session_state.questions_json = parse_questions(questions_text)
                        st.success("✅ Questions Generated Successfully!")

                        # Provide downloadable PDF
                        pdf_buffer = generate_pdf(st.session_state.questions_json)
                        st.download_button(
                            label="📥 Download Quiz as PDF",
                            data=pdf_buffer,
                            file_name="fill_in_the_blank_quiz.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("⚠️ No valid questions generated. Please try again.")
            else:
                st.error("⚠️ Please upload at least one PDF file.")

    # Take Quiz
    if option == "Take Quiz":
        if st.session_state.questions_json:
            st.write("### 📝 Quiz")
            conduct_fill_in_blank_quiz()
            if "quiz_submitted" in st.session_state and st.session_state.quiz_submitted:
                calculate_fill_in_blank_score()
        else:
            st.warning("⚠️ No questions available. Please generate them first.")

if __name__ == "__main__":
    main()
