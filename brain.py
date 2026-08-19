import os

from commands import open_application, open_website
from google import genai
from google.genai import types


# gemini ai set up

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found.")

client = genai.Client(api_key=api_key)


# ultrons pbrain

def process_message(message):
    message = message.strip()

    if not message:
        return ""

    # gemini

    response = client.models.generate_content(
        model="gemini-3.6-flash-lite",
        contents=message,
        config=types.GenerateContentConfig(
            tools=[
                open_application,
                open_website
            ]
        )
    )

    return response.text