import pyautogui
import subprocess
import time
from tqdm import tqdm
import logging
import re

# logging.basicConfig(level=logging.INFO)
logging.disable(logging.CRITICAL)


class Navigation:
    def __init__(self):
        self.attempts_close_popup = 10
        self.attempts_find_popup = 10
        self.pause_time = 0.2
        self.attempts_with_no_sign = 10
        self.target_app_name = "abelian-wallet-desktop"

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

    def _is_popup(self):
        self.pause()
        return "Sending ABEL" in self.extract_clipboard()

    def in_popup(self):
        logging.info("Looking for popup")
        for _ in range(self.attempts_find_popup):
            return bool(self._is_popup())

    def close_popup(self):
        logging.info("Closing popup")
        for _ in range(self.attempts_close_popup):
            self.pause(1)
            self.tab()
            self.enter()
            return not bool(self._is_popup())

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
