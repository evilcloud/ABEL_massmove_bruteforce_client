import time
import pyautogui
from tqdm import tqdm
import subprocess
import pyperclip

PAUSE_TIME = 0.2
PENDING_SYMBOLS = ["⏳", "⌛", "Unlocking account"]
SUBMITTED_SYMBOL = "✅"
FAILED_SYMBOL = "❌"
FAILED_REASONS = {
    "Insufficient balance": "Insufficient balance",
    "Failed getting the latest balance": "Wallet not connected",
    "Wrong password.": "Wrong password",
}


def is_pending(screen_content):
    return any(symbol in screen_content for symbol in PENDING_SYMBOLS)


def is_submitted(screen_content):
    return SUBMITTED_SYMBOL in screen_content


def has_failed(screen_content):
    return FAILED_SYMBOL in screen_content


def get_failed_reason(screen_content):
    for reason, message in FAILED_REASONS.items():
        if reason in screen_content:
            return message


# scalars

def pause(wait: float):
    wait = wait if wait else PAUSE_TIME
    time.sleep(wait)


def tab(times: int = 1):
    for _ in range(times):
        pyautogui.press("tab")


def enter(text=None):
    if text:
        pyautogui.typewrite(str(text))
    else:
        pyautogui.press("enter")


def enter_value(text: str):
    pyautogui.typewrite(text)


def get_clipboard():
    pyperclip.copy('')
    pyautogui.hotkey("command", "a")
    pyautogui.hotkey("command", "c")
    return pyperclip.paste()


# complexities


def status_bar_pause(wait=0, description="Pause"):
    wait = wait if wait else PAUSE_TIME
    for _ in tqdm(range(wait), leave=False, desc=description):
        pause(1)


def app_in_focus(target_app):
    while True:
        try:
            front_app_name = subprocess.check_output(
                [
                    "osascript",
                    "-e",
                    'tell application "System Events" to get the name of every process whose frontmost is true',
                ],
                text=True,
            ).strip()
            if target_app in front_app_name:
                return
        except Exception as e:
            print(f"An error occurred: {e}")
        status_bar_pause(wait=5, desc="APP WINDOW NOT IN FOCUS")
