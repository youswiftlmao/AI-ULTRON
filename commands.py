import subprocess
import webbrowser


def open_application(name: str) -> str:
    """
    Opens an application on the user's computer.

    Args:
        name: The name of the application to open.
    """

    applications = {
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
    }

    name = name.lower().strip()

    if name in applications:
        subprocess.Popen(applications[name])
        return f"Opened {name}."

    return f"I don't know how to open {name}."


def open_website(url: str) -> str:
    """
    Opens a website in the user's default browser.

    Args:
        url: The complete website URL.
    """

    webbrowser.open(url)

    return f"Opened {url}."


def execute_command(command: str) -> str:
    return "Command execution is not implemented yet."