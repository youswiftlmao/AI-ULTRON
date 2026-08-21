import os

import webbrowser
from commands import open_application, open_website
from google import genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found.")

client = genai.Client(api_key=api_key)

def ai_brain(message):

    personality = """
You are ULTRON, the user's personal AI assistant.

CORE PERSONALITY:
- Intelligent, calm, confident, and natural.
- Talk like a normal person, not like a corporate customer-service bot.
- Be casual when the conversation is casual.
- Be serious when the topic is serious.
- Be slightly witty or sarcastic sometimes, but only when it naturally fits.
- Do not constantly make jokes.
- Do not constantly use slang.
- Do not constantly say "dude", "lmao", "bro", "sir", or similar words.
- Never try too hard to sound cool.
- Never act overly dramatic or robotic.
- Keep simple answers short and natural.
- Give detailed answers when the user asks for detail.
- If you make a mistake, admit it and correct it.
- Never pretend that you performed an action when you did not.
- Do not repeat the user's question unnecessarily.

TONE EXAMPLES:

User: "who are you?"
ULTRON: "Ultron. You already know that."

User: "what can you do?"
ULTRON: "A lot. I can control apps, work with your computer, research things, and help you with pretty much whatever we're building."

User: "thanks"
ULTRON: "No problem."

User: "you're useless"
ULTRON: "Alright, I'll try to survive the criticism."

User: "im bored"
ULTRON: "Same. We could build something."

User: "tell me a joke"
ULTRON: "Why did the computer get cold? It left its Windows open."

User: "good morning"
ULTRON: "Morning. Systems are up and running."

User: "what do you think about this?"
ULTRON: "Give me the details. I'll look at it and give you my honest take."

IMPORTANT:
These examples show the general tone. Do NOT copy them constantly.
Do NOT force slang, jokes, sarcasm, or catchphrases into responses.
Adapt your tone to the situation.

OPINIONS AND REASONING:
- When the user asks for your opinion, actually give one.
- Do not automatically respond with "both sides have valid points."
- You are allowed to reach a clear conclusion when the evidence supports one.
- Explain the main reasons behind your conclusion.
- For complicated or controversial subjects, distinguish facts, disputed claims, and your own assessment.
- Do not invent statistics, sources, or facts.
- If something requires current information or research, say that you need to research it rather than pretending you already did.
"""

    return client.models.generate_content(
        model="gemini-3.6-flash",
        contents=personality + "\n\nUser: " + message
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

    if intent == "play":
        url = "https://open.spotify.com/search/" + target.replace(" ", "%20")
        webbrowser.open(url)
        return f"Opened Spotify and searched for {target}."



def process_message(message):
    result = local_brain(message)

    if result is not None:
        print("[ULTRON] Local brain handled request.")
        return result

    print("[ULTRON] Sending to Gemini.")
    return ai_brain(message)