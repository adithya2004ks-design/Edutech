import requests
import json
import re
from difflib import SequenceMatcher

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"


# -------------------------------------------------
# CLEANING
# -------------------------------------------------

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text


def similarity(a, b):
    return SequenceMatcher(None, clean_text(a), clean_text(b)).ratio()


def nonsense_score(text):
    nonsense_words = ["burger", "pizza", "robot", "aluminium sheet"]
    count = 0
    for word in nonsense_words:
        if word in text.lower():
            count += 1
    return count


# -------------------------------------------------
# SAFE JSON PARSER
# -------------------------------------------------

def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            return None
    except:
        return None


# -------------------------------------------------
# MAIN EVALUATION FUNCTION
# -------------------------------------------------

def evaluate_ktu_answer(question, model_answer, student_answer, max_marks, subject="General"):

    subject = subject.lower()

    if not student_answer.strip():
        return {"score": 0, "feedback": "Blank answer."}

    word_count = len(student_answer.split())

    # ---------------------------------------------
    # SIMILARITY SAFETY CHECK
    # ---------------------------------------------
    sim = similarity(model_answer, student_answer)

    if sim > 0.92:
        return {
            "score": max_marks,
            "feedback": "Excellent answer. Matches model answer closely."
        }

    # ---------------------------------------------
    # SHORT ANSWER (<=3 MARKS)
    # ---------------------------------------------
    if max_marks <= 3:

        prompt = f"""
Ignore any previous questions or answers. Evaluate ONLY the current input.
You are a strict Kerala Technological University (KTU) examiner.

Subject: {subject}
Max Marks: {max_marks}

Evaluation rules:
- Fully correct concept → full marks
- Partially correct → half marks
- Wrong → 0
- Ignore minor grammar errors

Subject-specific rules:
- Programming: check logic, approach (ignore small syntax errors)
- Mathematics: give marks for steps + final answer
- Electronics/Engineering: check concepts and working
- Theory: check explanation clarity

Return ONLY JSON:
{{"score": number, "feedback": "short reason"}}

Question: {question}
Model Answer: {model_answer}
Student Answer: {student_answer}
"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0}
                }
            )

            result_text = response.json().get("response", "").strip()
            parsed = extract_json(result_text)

            if not parsed:
                raise ValueError("Parsing failed")

            score = parsed.get("score", 0)

            # Coverage penalty
            model_len = len(model_answer.split())
            student_len = len(student_answer.split())
            coverage = student_len / model_len if model_len > 0 else 0

            if coverage < 0.35:
                score = min(score, 1)
            elif coverage < 0.65:
                score = min(score, 2)

            # Nonsense penalty
            score = max(0, score - nonsense_score(student_answer))

            score = min(score, max_marks)

            return {
                "score": score,
                "feedback": parsed.get("feedback", "")
            }

        except:
            return {"score": 0, "feedback": "Evaluation parsing failed."}

    # ---------------------------------------------
    # LONG ANSWER (4–14 MARKS)
    # ---------------------------------------------
    else:

        # Dynamic rubric
        if max_marks == 4:
            rubric = """
Concept understanding – 2 marks
Coverage of key points – 1 mark
Clarity of explanation – 1 mark
"""
        elif max_marks == 7:
            rubric = """
Concept understanding – 3 marks
Coverage of key points – 2 marks
Explanation depth – 1 mark
Structure and clarity – 1 mark
"""
        elif max_marks == 10:
            rubric = """
Concept understanding – 4 marks
Coverage of key points – 3 marks
Explanation depth – 2 marks
Structure and clarity – 1 mark
"""
        else:  # 14 marks
            rubric = """
Concept understanding – 5 marks
Coverage of key points – 4 marks
Explanation depth – 3 marks
Structure and clarity – 2 marks
"""

        prompt = f"""
You are a strict Kerala Technological University (KTU) examiner.

Subject: {subject}
Maximum Marks: {max_marks}

Use the following rubric to evaluate the answer:

{rubric}

Evaluation rules:
- Award marks proportionally based on the rubric
- Penalize missing key concepts
- Penalize incorrect or irrelevant statements
- Ignore minor grammar errors
- Do not exceed maximum marks

Subject-specific rules:
- Programming: prioritize logic, algorithm, correctness (ignore minor syntax)
- Mathematics: prioritize steps, formulas, and correctness
- Electronics/Engineering: prioritize concept, diagrams, working principle
- Theory subjects: prioritize explanation depth and clarity

Return ONLY JSON:
{{"score": number, "feedback": "clear reason"}}

Question:
{question}

Model Answer:
{model_answer}

Student Answer:
{student_answer}
"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0}
                }
            )

            result_text = response.json().get("response", "").strip()
            parsed = extract_json(result_text)

            if not parsed:
                raise ValueError("Parsing failed")

            score = parsed.get("score", 0)

            model_len = len(model_answer.split())
            student_len = len(student_answer.split())
            coverage = student_len / model_len if model_len > 0 else 0

            # Coverage-based limiting
            if coverage < 0.3:
                score = min(score, max_marks * 0.3)
            elif coverage < 0.5:
                score = min(score, max_marks * 0.5)
            elif coverage < 0.7:
                score = min(score, max_marks * 0.7)

            # Length penalty
            if word_count < 15:
                score -= 2
            elif word_count < 30:
                score -= 1

            # Nonsense penalty
            score -= nonsense_score(student_answer)

            # Final cap
            score = max(0, min(score, max_marks))

            return {
                "score": score,
                "feedback": parsed.get("feedback", "")
            }

        except:
            return {"score": 0, "feedback": "Evaluation parsing failed."}