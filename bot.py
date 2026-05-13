import os
import json
import csv
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# =========================
# QUIZ GENERATOR
# =========================
def generate_quiz(topic, grade_level, num_questions, question_type="mix", language="en"):

    system_prompt = """
You are a strict quiz generator.
Return ONLY valid JSON.
No extra text.
"""

    user_prompt = f"""
Create a quiz.

Topic: {topic}
Grade: {grade_level}
Questions: {num_questions}
Type: {question_type}
Language: {language}

Format:
{{
  "topic": "...",
  "grade_level": "...",
  "questions": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "A"
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


# =========================
# QUIZ GAME ENGINE (FIXED)
# =========================
def run_quiz(quiz):

    if not quiz:
        print("❌ Quiz failed to load")
        return 0, 0

    score = 0
    total = len(quiz["questions"])

    print("\n🎮 QUIZ STARTED!\n")

    for i, q in enumerate(quiz["questions"], 1):
        print(f"Q{i}: {q['question']}\n")

        for idx, option in enumerate(q["options"], 1):
            print(f"{idx}. {option}")

        user_input = input("\nYour answer (A-D or 1-4): ").strip().upper()

        mapping = {
            "A": 0, "1": 0,
            "B": 1, "2": 1,
            "C": 2, "3": 2,
            "D": 3, "4": 3
        }

        if user_input in mapping:
            chosen = q["options"][mapping[user_input]]
        else:
            print("❌ Invalid input!")
            chosen = None

        correct = q["answer"].strip().upper()

        # convert correct answer letter → value from options
        correct_value = q["options"][mapping.get(correct, 0)]

        if chosen == correct_value and chosen is not None:
            print("✅ Correct!\n")
            score += 1
        else:
            print(f"❌ Wrong! Correct answer: {correct}\n")

    print(f"🏁 Final Score: {score}/{total}")
    return score, total


# =========================
# SAVE RESULT
# =========================
def save_result(topic, score, total):
    file_exists = os.path.isfile("results.csv")

    with open("results.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["date", "topic", "score", "total"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            topic,
            score,
            total
        ])

    print("💾 Result saved to results.csv")


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    topic = input("Enter topic: ")

    if topic.strip().isdigit():
        print("❌ Please enter a real topic (e.g. Football, Math, History)")
        exit()

    quiz = generate_quiz(
        topic=topic,
        grade_level="7-9",
        num_questions=5
    )

    score, total = run_quiz(quiz)

    save_result(topic, score, total)