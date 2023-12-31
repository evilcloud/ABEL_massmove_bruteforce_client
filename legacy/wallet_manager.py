import pyautogui
import subprocess
from tqdm import tqdm
import time
import pyperclip


class Control:
    def __init__(self, target_app_name):
        self.target_app_name = target_app_name
        self.pause_time = 0.2
        self.attempts_with_no_sign = 10

    def pause(self, wait=None):
        waiting_time = wait or self.pause_time
        time.sleep(waiting_time)

    def status_bar_pause(
            self, wait=0, position=1, desc="Pause",
            bar_format="{desc}: {bar}| {elapsed}"
    ):
        wait is wait if wait else self.pause_time
        for _ in tqdm(
                range(wait),
                position=position,
                leave=False,
                desc=desc,
                bar_format=bar_format,
        ):
            self.pause(1)
        self.app_in_focus()

    def app_in_focus(self):
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
                if self.target_app_name in front_app_name:
                    return
            except Exception as e:
                print(f"An error occurred: {e}")
            self.status_bar_pause(wait=5, desc="APP WINDOW NOT IN FOCUS")

    # def extract_clipboard(self):
    #     self.pause()
    #     pyautogui.hotkey("command", "a")
    #     pyautogui.hotkey("command", "c")
    #     return subprocess.run(["pbpaste"], capture_output=True, text=True).stdout

    def extract_clipboard(self):
        self.pause()
        pyperclip.copy('')
        pyautogui.hotkey("command", "a")
        pyautogui.hotkey("command", "c")
        return pyperclip.paste()

    def confirmation_popup(self):
        self.tab()
        self.tab()
        self.enter()
        return False

    def close_popup(self):
        if not self.in_popup():
            return True
        for _ in range(10):
            self.tab()
            self.enter()
            if "Sending ABEL" not in self.extract_clipboard():
                return True
            self.pause(1)
        return False

    def in_popup(self):
        for _ in range(10):
            if "Sending ABEL" in self.extract_clipboard():
                return True
            self.pause()
        return False

    def tab(self, nr=1):
        for _ in range(nr):
            pyautogui.press("tab")

    def enter(self):
        pyautogui.press("enter")

    def type(self, text):
        pyautogui.typewrite(text)


class Symbols:
    def __init__(self):
        self.pending_symbols = ["⏳", "⌛", "Unlocking account"]
        self.submitted_symbol = "✅"
        self.failed_symbol = "❌"
        self.failed_reasons = {
            "Insufficient balance": "Insufficient balance",
            "Failed getting the latest balance": "Wallet not connected",
            "Wrong password.": "Wrong password",
        }

    def pending(self, screen_content):
        return any(i in screen_content for i in self.pending_symbols)

    def submitted(self, screen_content):
        return self.submitted_symbol in screen_content

    def failed(self, screen_content):
        return self.failed_symbol in screen_content

    def failed_reason(self, screen_content):
        for reason, message in self.failed_reasons.items():
            if reason in screen_content:
                return message


class WalletManager:
    def __init__(self, target_app_name):
        self.control = Control(target_app_name)
        self.symbols = Symbols()
