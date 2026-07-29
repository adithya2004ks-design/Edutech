import requests
import json
import time
import os

# -----------------------------
# CONFIG
# -----------------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"   # Change to "phi3" if system slow
OUTPUT_FILE = "data/model_answers.json"

# -----------------------------
# IMPORT QUESTION BANK
# -----------------------------
try:
    from data.question_bank import question_bank
except Exception as e:
    print("❌ Failed to import question_bank:", e)
    exit()

print("✅ Script started...")
print(f"📌 Total Questions: {len(question_bank)}")

model_answers = {}

# -----------------------------
# GENERATION LOOP
# -----------------------------
for index, (q_key, data) in enumerate(question_bank.items(), start=1):

    question_text = data["question"]
    marks = data["marks"]

    print(f"\n🔄 ({index}/{len(question_bank)}) Generating answer for {q_key} ({marks} marks)...")

    prompt = f"""
You are a strict Kerala Technological University (KTU) examiner.

Generate a HIGH-QUALITY model answer suitable for {marks} marks.

Requirements:
- Accurate
- Structured
- Academic tone
- Appropriate length for {marks} marks
- Maximum scoring quality

Question:
{question_text}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=300   # Allow up to 5 minutes per answer
        )

        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
            continue

        result = response.json()
        answer_text = result.get("response", "").strip()

        model_answers[q_key] = answer_text

        print("✅ Done")

        # Save progressively after each answer
        os.makedirs("data", exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(model_answers, f, indent=4, ensure_ascii=False)

        time.sleep(1)  # small delay to avoid overload

    except requests.exceptions.Timeout:
        print("⏳ Timeout occurred. Skipping this question.")
    except Exception as e:
        print("❌ Unexpected error:", e)

print("\n🎉 Model answer generation complete!")
print(f"📂 Saved to: {OUTPUT_FILE}")