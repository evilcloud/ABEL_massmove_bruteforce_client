import os
import requests
import asyncio
from telegram import Bot


class TelegramCommunicator:
    def __init__(self):
        # Telegram credentials
        self.bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
        self.chat_id = os.environ["TELEGRAM_CHAT_ID"]

    async def send_telegram_message(self, message):
        bot = Bot(token=self.bot_token)
        # Check if the message is a dictionary
        if isinstance(message, dict):
            # Convert the dictionary to a nicely formatted string
            message = self._pretty_print_text(message)
        try:
            await bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            print(f"Failed to send Telegram message: {str(e)}")

    def send_telegram_message_sync(self, message):
        asyncio.run(self.send_telegram_message(message))

    def _pretty_print_text(self, data):
        # Convert dictionary to a structured text format
        pretty_text = ""
        for key, value in data.items():
            pretty_text += f"{key}:\n    {value}\n"
        return pretty_text


class APICommunicator:
    def __init__(self):
        # API credentials
        self.master_pass = os.environ["API_MASTER_PASS"]
        self.url = os.environ["API_URL"]

    def post_update_to_server(self, payload):
        response = requests.post(self.url, json=payload)
        try:
            response.json()
        except ValueError:
            print(response.content)


class MultiChannelCommunicator(TelegramCommunicator, APICommunicator):
    def __init__(self):
        TelegramCommunicator.__init__(self)
        APICommunicator.__init__(self)

    def message_all(self, payload, message=None):
        message = message or payload
        if isinstance(message, dict):
            message = self._pretty_print_text(message)
        self.send_telegram_message_sync(message)
        self.post_update_to_server(payload)

    def message_telegram(self, payload):
        self.send_telegram_message_sync(payload)

    def message_api(self, payload):
        self.post_update_to_server(payload)


# Example usage
if __name__ == "__main__":
    communications = MultiChannelCommunicator()
    communications.message_all(
        {"example": "Hello from the bot!", "key2": "value2"}, {"example": "payload"}
    )
