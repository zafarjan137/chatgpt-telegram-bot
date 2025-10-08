import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import google.generativeai as genai

# Logging
logging.basicConfig(level=logging.INFO)

# 🔑 Muhit o'zgaruvchilari (Railway yoki local)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN topilmadi! Railway Variables-ga qo‘shing.")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY topilmadi! https://aistudio.google.com/app/apikey dan oling.")

# Telegram bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Gemini sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("👋 Salom! Men Gemini (Google AI) asosida ishlayman. Savolingizni yozing!")

@dp.message_handler()
async def chat(message: types.Message):
    try:
        prompt = message.text
        response = model.generate_content(prompt)
        await message.reply(response.text)
    except Exception as e:
        await message.reply(f"⚠️ Xato: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)








