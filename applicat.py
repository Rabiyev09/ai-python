import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# =========================
# LOAD .ENV
# =========================
load_dotenv(dotenv_path=Path(".env"))

# =========================
# CREATE OPENAI CLIENT
# =========================
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================
# CREATE OUTPUT FOLDER
# =========================
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# =========================
# USER PROMPT
# =========================
prompt = input("Enter image prompt: ").strip()

# default prompt
if not prompt:
    prompt = "A futuristic cyberpunk city at night with neon lights"

# =========================
# GENERATE IMAGE
# =========================
try:

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    # get base64 image
    image_base64 = result.data[0].b64_json

    # decode image
    image_bytes = base64.b64decode(image_base64)

    # output path
    file_path = output_dir / "generated_image.png"

    # save image
    with open(file_path, "wb") as file:
        file.write(image_bytes)

    # success message
    print("\n✅ IMAGE GENERATED SUCCESSFULLY!")
    print(f"📝 Prompt used: {prompt}")
    print(f"💾 Saved file: {file_path}")

except Exception as e:
    print("\n❌ ERROR:")
    print(e)