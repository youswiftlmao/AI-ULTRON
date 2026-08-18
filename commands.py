import subprocess
import webbrowser

def open_application(name):

    name = name.lower().strip()

    applications = {
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
    }