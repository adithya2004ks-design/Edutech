# 🎓 Edutech - AI Powered KTU Answer Sheet Evaluation System

Edutech is an AI-powered web application that automates the evaluation of Kerala Technological University (KTU) descriptive answers. The system compares student answers with model answers using Large Language Models (LLMs) and generates marks along with feedback based on KTU evaluation standards.

## ✨ Features

- AI-based descriptive answer evaluation
- KTU-style marking scheme
- Automatic score generation
- Detailed feedback for each answer
- Student answer upload
- Admin dashboard
- Question and model answer management
- SQLite database integration
- Responsive web interface

## 🛠️ Technologies Used

### Backend
- Python
- Flask

### Frontend
- HTML
- CSS
- JavaScript

### Database
- SQLite

### AI
- OpenAI API

### Version Control
- Git
- GitHub

## 📂 Project Structure

```
Edutech/
│
├── app.py
├── ktu_llm_evaluator.py
├── ktu_result_logic.py
├── requirements.txt
├── edutech.db
├── data/
├── templates/
├── static/
├── uploads/
└── README.md
```

## 🚀 Installation

### Clone the repository

```bash
git clone https://github.com/adithya2004ks-design/Edutech.git
```

### Move into the project

```bash
cd Edutech
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file in the project root.

Example:

```text
OPENAI_API_KEY=your_openai_api_key
```

> **Do not upload your `.env` file to GitHub.**

## ▶️ Run the application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

## 📖 Workflow

1. Upload student answers.
2. Compare answers with model answers.
3. AI evaluates semantic similarity and correctness.
4. Marks are assigned based on the KTU scheme.
5. Feedback is generated automatically.
6. Results are stored in the database.

## 📸 Screenshots

You can add screenshots here later.

Example:

```
screenshots/home.png
screenshots/admin_dashboard.png
screenshots/results.png
```

## Future Improvements

- OCR support for handwritten answer sheets
- Multiple university support
- PDF report generation
- User authentication
- Analytics dashboard
- Cloud database integration
- Docker deployment

## Author

**Adithya KS**

GitHub:
https://github.com/AdithyaKS69

## License

This project is intended for educational and research purposes.
