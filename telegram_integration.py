import asyncio
from telegram import Bot
import os

# Your Telegram bot token
bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]


# Send a message using the bot
async def send_telegram_message(message):
    bot = Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Failed to send Telegram message: {str(e)}")


# Example usage
async def main():
    message = "Hello from the bot!"
    await send_telegram_message(message)


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
