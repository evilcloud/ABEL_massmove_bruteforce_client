import pyautogui
import subprocess
import time
from tqdm import tqdm
import logging
import re

logging.basicConfig(level=logging.INFO)
# logging.disable(logging.CRITICAL)


class Navigation:
    def __init__(self):
        self.attempts_close_popup = 10
        self.attempts_find_popup = 10
        self.pause_time = 0.2
        self.attempts_with_no_sign = 10
        self.target_app_name = "abelian-wallet-desktop"
        self.screen = Screen()
        self.symbol = Symbols()

    def pause(self, wait=None):
        self.app_in_focus()
        waiting_time = wait or self.pause_time
        time.sleep(waiting_time)
        self.app_in_focus()

    def status_bar_pause(
        self, wait=3, position=1, desc="Pause", bar_format="{desc}: {bar}| {elapsed}"
    ):
        for _ in tqdm(
            range(wait),
            position=position,
            leave=False,
            desc=desc,
            bar_format=bar_format,
        ):
            time.sleep(1)
        self.app_in_focus()

    def tab(self):
        self.pause()
        pyautogui.press("tab")

    def enter(self):
        self.pause()
        pyautogui.press("enter")

    def type(self, text):
        self.pause()
        pyautogui.typewrite(text)

    def extract_clipboard(self):
        self.pause()
        pyautogui.hotkey("command", "a")
        pyautogui.hotkey("command", "c")
        return subprocess.run(["pbpaste"], capture_output=True, text=True).stdout

    def in_popup(self):
        # The difference between this and is_popup is that this one
        # runs multiple attempts to find the popup with an increasing
        # amount of wait time between each attempt
        for _ in range(self.attempts_find_popup):
            if self.screen.is_popup():  # Check if the screen is a popup
                return True
            self.pause()
        return False

    def close_popup(self):
        # Check if we are in a popup at all first...
        # The amount of errors while we are in fact elsewhere is ridiculous
        if not self.in_popup():
            return True
        # Now that we've established that we are indeed in a popup, let's try
        # to close it, but adding a short pause and a tab in between, in case we've got lost
        for i in range(self.attempts_close_popup):
            self.pause(i)
            self.tab()
            self.enter()
            if not self.screen.is_popup():
                return True
        return False

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


class Screen:
    def __init__(self):
        self.target_app_name = "abelian-wallet-desktop"
        self.pause_time = 0.2

        self.right_screen = "Select an address to send ABEL from account"
        self.popup_id_str = "Sending ABEL"

        self.transaction_submitted = "✅ Transaction submitted."
        self.transaction_failed = "❌"
        self.transaction_failed_reasons = {
            "Insufficient balance": "Insufficient balance",
            "Failed getting balance": "Wallet not connected",
            "Wrong password.": "Wrong password",
        }
        self.transaction_waiting = ["⏳", "⌛", "Unlocking account"]

        self.screen_content = None


    def pause(self, wait=None):
        self.app_in_focus()
        waiting_time = wait or self.pause_time
        time.sleep(waiting_time)
        self.app_in_focus()

    def status_bar_pause(
        self, wait=3, position=1, desc="Pause", bar_format="{desc}: {bar}| {elapsed}"
    ):
        for _ in tqdm(
            range(wait),
            position=position,
            leave=False,
            desc=desc,
            bar_format=bar_format,
        ):
            time.sleep(1)
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

    def extract_clipboard(self):
        self.pause()
        pyautogui.hotkey("command", "a")
        pyautogui.hotkey("command", "c")
        return subprocess.run(["pbpaste"], capture_output=True, text=True).stdout

    def capture_data(self):
        self.pause()
        pyautogui.hotkey("command", "a")
        pyautogui.hotkey("command", "c")
        screen_content = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout
        self.screen_content = screen_content


    def is_popup(self):
        self.pause()
        return self.popup_id_str in self.extract_clipboard()

    def transaction_submitted(self, clipboard_content):
        return self.transaction_submitted in clipboard_content

    def is_transaction_failed(self, clipboard_content):
        return self.transaction_failed in clipboard_content

    def transaction_failure_reason(self, clipboard_content):
        return next(
            (
                v
                for k, v in self.transaction_failed_reasons.items()
                if k in clipboard_content
            ),
            "Transaction failed",
        )

    def transaction_processing(self, screen_content):
        return any(i in screen_content for i in self.transaction_waiting)


class Symbols:
    def __init__(self):
        self.right_screen = "Select an address to send ABEL from account"
        self.popup_id_str = "Sending ABEL"

        self.transaction_submitted = "✅ Transaction submitted."
        self.transaction_failed = "❌"
        self.transaction_failed_reasons = {
            "Insufficient balance": "Insufficient balance",
            "Failed getting balance": "Wallet not connected",
            "Wrong password.": "Wrong password",
        }
        self.transaction_waiting = ["⏳", "⌛", "Unlocking account"]

    def pending(self, screen_content):
        return any(i in screen_content for i in self.transaction_waiting)

    def submitted(self, screen_content):
        return self.transaction_submitted in screen_content

    def failed(self, screen_content):
        return self.transaction_failed in screen_content

    def failed_reason(self, screen_content):
        if self.failed(screen_content):
            return self.transaction_failed_reasons.get(screen_content, "Transaction failed")
        return None

