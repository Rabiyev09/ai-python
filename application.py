import sqlite3
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = "gpt-4o-mini"

db = sqlite3.connect("chat.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    content TEXT
)
""")
db.commit()

def add(role, text):
    cur.execute(
        "INSERT INTO messages(role, content) VALUES (?, ?)",
        (role, text)
    )
    db.commit()

def get_messages(limit=20):
    rows = cur.execute(
        "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()

    rows.reverse()  

    messages = [
        {"role": "system", "content": "You are a helpful assistant"}
    ]

    for role, content in rows:
        messages.append({"role": role, "content": content})

    return messages

print("🤖 Chat started (OpenAI + SQLite). Ctrl+C to exit.\n")

while True:
    try:
        user_input = input("You: ").strip()
    except KeyboardInterrupt:
        print("\nExit.")
        break

    if not user_input:
        continue

    add("user", user_input)

    messages = get_messages()

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7
    )

    reply = response.choices[0].message.content

    add("assistant", reply)

    print("Bot:", reply, "\n")

db.close()