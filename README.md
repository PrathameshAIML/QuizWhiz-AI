#  QuizWhiz AI 

Welcome to **QuizWhiz AI** – an interactive and beautifully designed AI-powered quiz generator that makes learning fun, fast, and effective.

---

## 👥 Team Members
- Prathamesh
- Ibrahim Bagwan

---

## 🌟 Features

- 🎨 **Animated Gradient Background** – Modern and eye-catching UI with smooth transitions.
- ✍️ **Quiz Types** – Choose between:
  - Fill in the Blanks
  - Multiple Choice Questions (MCQs)
- 🤖 **AI Integration (Future Scope)** – Easily extendable to generate questions from user-uploaded content using NLP models.
- 🎯 **User-Friendly Layout** – Clean interface using Streamlit’s easy-to-use components.
- ⚡ **Fast Navigation** – Page switch functionality for seamless user interaction.

---

## 📂 Project Structure

```
QuizWhiz-AI/
│
├── app.py                 # Main homepage with UI and navigation
├── pages/
│   ├── fill_in_blanks.py   # Page for Fill in the Blanks quiz
│   └── mcq.py              # Page for Multiple Choice Questions quiz
│
└── README.md               # Project documentation
```

---

## 🚀 How to Run the Project

### 🔧 Prerequisites
- Python 3.7 or later
- Streamlit installed

### 📦 Installation

```bash
pip install streamlit
```

### ▶️ Run the App

```bash
streamlit run app.py
```

> **Note:** Ensure the `pages/` folder contains `fill_in_blanks.py` and `mcq.py` files.

---

## 🎨 UI Preview

The app uses a modern animated gradient background with custom-styled buttons, creating a fun and engaging experience for learners.

---

## 🛠️ Customization Tips

- Easily add your own question-generating logic using OpenAI's GPT or any NLP model.
- To modify UI themes, edit the `get_gradient_style()` function in `main.py`.

---

## 📌 Future Scope

- ✨ Integrate NLP to generate quizzes from user-uploaded text or PDFs.
- 📊 Add scoring and performance tracking.
- 💾 Save user progress using databases.
- 📱 Develop a mobile-friendly UI or Android app.

---

## 🙌 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📃 License

This project is open source and available under the MIT License.

---

## 💡 Inspiration

Built with ❤️ using Streamlit to make studying smarter, faster, and more fun!