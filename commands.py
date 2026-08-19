import subprocess
import webbrowser
import os

def open_application(name: str) -> str:

    name = name.lower().strip()

    if not name:
        return "I do not know how to open that."

    try:
        
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"""
                $app = Get-StartApps | Where-Object {{
                    $_.Name -like "*{name}*"
                }} | Select-Object -First 1

                if ($app) {{
                    Start-Process "shell:AppsFolder\\$($app.AppID)"
                    exit 0
                }}

                exit 1
                """
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return f"Opened {name}."

    except Exception:
        pass

    return f"I do not know how to open {name}."



def open_website(url: str) -> str:

    webbrowser.open(url)

    return f"Opened {url}."


def execute_command(command: str) -> str:
    return "Command execution is not implemented yet."