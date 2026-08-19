import subprocess
import webbrowser
import os

def open_application(name: str) -> str:

    name = name.lower().strip()


def open_website(url: str) -> str:

    webbrowser.open(url)

    return f"Opened {url}."


def execute_command(command: str) -> str:
    return "Command execution is not implemented yet."