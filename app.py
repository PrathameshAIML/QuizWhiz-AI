import streamlit as st

# Function to create an animated gradient background
def get_gradient_style():
    gradient = "linear-gradient(45deg, #ff9a9e, #fad0c4, #ffdde1, #fccb90, #fbc2eb, #a6c1ee, #d4fc79, #96e6a1)"
    return f"""
    <style>
        /* Apply gradient background to the whole app */
        .stApp {{
            background: {gradient}; 
            background-size: 400% 400%;
            animation: gradientBG 10s ease infinite;
            color: black; /* Ensuring text remains black */
        }}

        @keyframes gradientBG {{
            0% {{background-position: 0% 50%;}}
            50% {{background-position: 100% 50%;}}
            100% {{background-position: 0% 50%;}}
        }}

        /* Centered main container */
        .main-container {{
            text-align: center;
            padding: 50px;
            color: black; /* Black text */
        }}

        /* Customizing buttons */
        .stButton>button {{
            background-color: rgba(255, 255, 255, 0.6);
            color: black;
            padding: 15px 25px;
            font-size: 18px;
            border-radius: 10px;
            border: 2px solid black;
            cursor: pointer;
            transition: 0.3s;
        }}
        
        .stButton>button:hover {{
            background-color: rgba(255, 255, 255, 0.8);
            transform: scale(1.05);
        }}
    </style>
    """

# Apply the gradient background
st.markdown(get_gradient_style(), unsafe_allow_html=True)

# Page Title
st.markdown("<div class='main-container'>", unsafe_allow_html=True)
st.title("🔥 QuizWhiz AI 🚀")
st.write("### AI-Powered Quiz Generator for Smarter Learning")

# Description (100 words)
st.write("""
**Welcome to QuizWhiz AI!** 🚀  
This platform is your ultimate AI-powered quiz generator. Whether you're a student, teacher, or just someone who loves learning, QuizWhiz AI makes studying fun and interactive. Generate quizzes instantly, customize difficulty levels, and challenge yourself with engaging MCQs and fill-in-the-blank exercises.  
Learning has never been this easy and exciting! Get started now and become an absolute wizard! 🔥
""")

# Buttons for navigation
col1, col2 = st.columns(2)

with col1:
    if st.button("✨ Fill in the Blanks"):
        st.switch_page("fill_in_blanks")  

with col2:
    if st.button("📝 Multiple Choice Questions"):
        st.switch_page("mcq")  

st.markdown("</div>", unsafe_allow_html=True)
