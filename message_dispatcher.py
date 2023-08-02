import os
import requests
import asyncio
from telegram import Bot
from enum import Enum


class Channel(Enum):
    TELEGRAM = 'telegram'
    STDOUT = 'stdout'
    API = 'api'


class TelegramCommunicator:
    def __init__(self):
        self.bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
        self.chat_id = os.environ["TELEGRAM_CHAT_ID"]

    async def send_telegram_message(self, message):
        bot = Bot(token=self.bot_token)
        try:
            await bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            print(f"Failed to send Telegram message: {str(e)}")

    def send_telegram_message_sync(self, message):
        asyncio.run(self.send_telegram_message(message))


class APICommunicator:
    def __init__(self):
        self.master_pass = os.environ["API_MASTER_PASS"]
        self.url = os.environ["API_URL"]

    def post_update_to_server(self, payload):
        response = requests.post(self.url, json=payload)
        try:
            response.json()
        except ValueError:
            print(response.content)


class StdoutCommunicator:
    def print_to_stdout(self, message):
        if isinstance(message, dict):
            pretty_message = "\n".join([f"{k}: {v}" for k, v in message.items()])
        else:
            pretty_message = message
        print(pretty_message)


class MultiChannelCommunicator(TelegramCommunicator, APICommunicator, StdoutCommunicator):
    def __init__(self):
        TelegramCommunicator.__init__(self)
        APICommunicator.__init__(self)

    def message_all(self, payload, message=None):
        message = message or payload
        if isinstance(message, dict):
            message = self._pretty_print_text(message)
        self.send_telegram_message_sync(message)
        self.post_update_to_server(payload)
        self.print_to_stdout(message)

    def send_message(self, payload, channels: list):
        message = payload
        if isinstance(message, dict):
            message = self._pretty_print_text(message)

        if Channel.TELEGRAM in channels:
            self.send_telegram_message_sync(message)

        if Channel.API in channels:
            self.post_update_to_server(payload)

        if Channel.STDOUT in channels:
            self.print_to_stdout(message)

    def _pretty_print_text(self, data):
        pretty_text = ""
        for key, value in data.items():
            pretty_text += f"{key}:\n    {value}\n"
        return pretty_text
