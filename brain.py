import os
import re
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
        model="gemini-3.6-flash",
        contents=message,
        config=types.GenerateContentConfig(
            tools=[
                open_application,
                open_website
            ]
        )
    )

    return response.text









def local_brain(message):

        # small brain
        #Returns:
        #str  -> if ULTRON can handle the request locally
        #None -> if the request should go to Gemini

    text = message.strip()


    if not text:
        return ""

    lower = text.lower()

    #open somthign

    if lower.startswith("open "):

        target = text[5:].strip()

        if not target:
            return None



        #if it looks like website

        if (
             target.startswith("http://")
            or target.startswith("https://")
            or "." in target
        ):
            url = target

            if not url.startswith(("http://", "https://")):

                url = "https://" + url

            return open_website(url)

        return open_application(target)

    return None


#ultrons new processor wooooo

_old_process_message = process_message

def process_message(message):

    #local brain

    local_response = local_brain(message)

    if local_response  is not None:
        print ("[ULTRON] Local brain handled request.")
        return local_response


    #if cant use ai 
    print ("[ULTRON] sending request to gemni.")
    return _old_process_message(message)
