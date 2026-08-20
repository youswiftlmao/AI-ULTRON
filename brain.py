import os
import webbrowser
from commands import open_application, open_website
from google import genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found.")

client = genai.Client(api_key=api_key)


def ai_brain(message):
    return client.models.generate_content(
        model="gemini-3.6-flash",
        contents=message
    ).text


def understand(message):
    text = message.strip()
    lower = text.lower()

    for word in [
        "open ",
        "launch ",
        "start ",
        "start up ",
        "bring up "
        ]:


        if lower.startswith(word):
            return "open", text[len(word):].strip()

    for word in [
        "write ",
        "type ",
        "enter "
        ]:

        
        if lower.startswith(word):
            return "write", text[len(word):].strip()

    if lower.startswith("play "):
        return "play", text[5:].strip()

    return None


def local_brain(message):
    parsed = understand(message)
    if not parsed:
        return None

    intent, target = parsed

    if intent == "open":
        if target.startswith(("http://", "https://")):
            return open_website(target)

        result = open_application(target)
        if not result.startswith("I do not know"):
            return result

        webbrowser.open("https://" + target + ".com")
        return f"opened {target} on the web."

    if intent == "write":
        return f"I understand i need to write: {target}"

    if intent == "play":
        return f"I understand you want me to play: {target}"


def process_message(message):
    result = local_brain(message)
    return result if result is not None else ai_brain(message)


def process_message(message):
    result = local_brain(message)

    if result is not None:
        print("[ULTRON] Local brain handled request.")
        return result

    print("[ULTRON] Sending to Gemini.")
    return ai_brain(message)