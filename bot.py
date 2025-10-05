import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
import asyncio

# 🔑 Telegram bot token va OpenAI API kalitini bu yerga yoz
TELEGRAM_TOKEN = "8369521872:AAGmWTeDmuqYBwionMpNblYgn2hCUBnQSNE"
OPENAI_API_KEY = "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"

# 🔧 OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# 🧠 Har foydalanuvchi uchun xotira
user_memory = {}

# 🚀 /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men @zafarjan_17 tomonidan yaratilgan ChatGPT asosidagi sun’iy intellektman.\n"
        "Menga savol bering yoki shunchaki suhbatni boshlang 😊"
    )

import requests

# 🌐 Ob-havo va valyuta ma’lumotlarini olish
def get_web_data(user_message):
    user_message_lower = user_message.lower()

    # Ob-havo
    if "ob-havo" in user_message_lower or "havo" in user_message_lower:
        try:
            response = requests.get("https://wttr.in/Tashkent?format=%C+%t")
            if response.status_code == 200:
                return f"🌤 Hozirgi ob-havo: {response.text}"
        except:
            return "❌ Ob-havo ma’lumotini olishda xatolik yuz berdi."

    # Dollar kursi
    if "dollar" in user_message_lower or "usd" in user_message_lower:
        try:
            response = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/")
            data = response.json()
            usd = next((x for x in data if x["Ccy"] == "USD"), None)
            if usd:
                return f"💵 1 USD = {usd['Rate']} so'm"
        except:
            return "❌ Valyuta kursini olishda xatolik yuz berdi."

    # Yangiliklar
    if "yangilik" in user_message_lower:
        try:
            response = requests.get("https://kun.uz/news/rss")
            if response.status_code == 200:
                return "📰 So‘nggi yangiliklar: https://kun.uz/news"
        except:
            return "❌ Yangiliklarni olishda xatolik yuz berdi."

    return None  # hech narsa topilmasa



# 💬 Asosiy chat funksiyasi
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text
    

    # 🔍 Internetdan ma’lumot kerak bo‘lsa
    web_info = get_web_data(user_message)
    if web_info:
        await update.message.reply_text(web_info)
        return


    # Typing animatsiyasi
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(0.5)  # biroz kutish tabiiyroq qiladi

    # Foydalanuvchining kontekstini tekshiramiz
    if user_id not in user_memory:
        user_memory[user_id] = [
            {"role": "system", "content": "Sen o‘zbek tilida samimiy, kulgili, lekin foydali yordamchisan."}
        ]

    user_memory[user_id].append({"role": "user", "content": user_message})

    # ChatGPT modelidan javob olish
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=user_memory[user_id],
        stream=True
    )

    reply = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and getattr(chunk.choices[0].delta, "content", None):
            reply += chunk.choices[0].delta.content

    if not reply:
        reply = "😅 Kechirasiz, javobni hosil qila olmadim. Qayta yozing."

    # Javobni xotirada saqlaymiz
    user_memory[user_id].append({"role": "assistant", "content": reply})

    # Markdown formatda yuboramiz
    await update.message.reply_text(
        reply,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# 🔧 Botni ishga tushirish
if __name__ == "__main__":
    print("🚀 Bot ishga tushmoqda...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()
