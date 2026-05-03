import os, sqlite3, time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI



BASE_DIR = Path(__file__).resolve().parent

FILE_PROMPT = BASE_DIR / "prompt.txt"
FILE_WELCOME = BASE_DIR / "welcome.txt"
FILE_HELP = BASE_DIR / "help.txt"


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден: {path.name}")

PROMPT_TEMPLATE = load_text(FILE_PROMPT)
WELCOME = load_text(FILE_WELCOME)
HELP_TEXT = load_text(FILE_HELP)



load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")



DB = sqlite3.connect("chat_history.db")
DB.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    content TEXT NOT NULL
)
""")
DB.commit()

def save(role: str, content: str):
    DB.execute(
        "INSERT INTO messages(role, content) VALUES(?, ?)",
        (role, content)
    )
    DB.commit()

def fetch_all():
    return DB.execute(
        "SELECT role, content FROM messages ORDER BY id ASC"
    ).fetchall()

def clear_history():
    DB.execute("DELETE FROM messages")
    DB.commit()
    print("🧹 История очищена")


def build_messages(user_input: str):
    history = fetch_all()

    messages = [
        {"role": "system", "content": PROMPT_TEMPLATE}
    ]

    for role, content in history:
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_input})

    return messages

def get_answer(user_input: str):
    messages = build_messages(user_input)

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )

    answer = response.choices[0].message.content

    save("user", user_input)
    save("assistant", answer)

    return answer


def show_welcome():
    print(WELCOME)

def show_help():
    print(HELP_TEXT)


def main():
    show_welcome()

    while True:
        user_input = input("\nТы: ").strip()

        if not user_input:
            continue

        if user_input == "/exit":
            print("Пока! 👋")
            break

        if user_input == "/help":
            show_help()
            continue

        if user_input in ["/reset", "/delete"]:
            clear_history()
            continue

        print("\nИИ печатает...\n")
        time.sleep(0.5)

        answer = get_answer(user_input)
        print("ИИ:", answer)


if __name__ == "__main__":
    main()