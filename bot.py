from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
from openai import OpenAI

# OpenAI va Telegram sozlamalari
openai_api_key = ("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")
bot_token = ("8369521872:AAEmiiYUx1BwHyB3Wmm1sK2iUJ4vtYXWHoY")

client = OpenAI(api_key=openai_api_key)
ADMIN_ID = 6079100324  # 👈 faqat sen

# Foydalanuvchi xotirasi
user_memory = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 Yordam", callback_data="help")],
        [InlineKeyboardButton("🔁 Qayta boshlash", callback_data="restart")],
        [InlineKeyboardButton("👤 Haqimda", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Salom! Men ChatGPT asosidagi AI botman.\n\nSavolingizni yozing, men javob beraman!",
        reply_markup=reply_markup
    )

# Tugmalar funksiyasi
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await query.edit_message_text("ℹ️ Faqat yozing – men sizga javob qaytaraman.\nOvoz, matn va so‘rovlarni tushunaman.")
    elif query.data == "restart":
        user_memory.clear()
        await query.edit_message_text("🔁 Xotira tozalandi! Yangi suhbatni boshlang.")
    elif query.data == "about":
        await query.edit_message_text("🤖 GPT asosidagi AI bot (versiya 2.5)\nYaratuvchi: Admin 👨‍💻")

# Chat funksiyasi (matn)
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Faqat admin uchun maxsus buyruqlar
    if user_id == ADMIN_ID and text.startswith("/"):
        if text == "/status":
            await update.message.reply_text("🟢 Bot ishlayapti!")
            return
        elif text == "/users":
            await update.message.reply_text(f"👥 Xotirada {len(user_memory)} ta foydalanuvchi bor.")
            return
        elif text == "/clear":
            user_memory.clear()
            await update.message.reply_text("🧹 Xotira tozalandi.")
            return

    # Oddiy foydalanuvchilar uchun
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({"role": "user", "content": text})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=user_memory[user_id]
        )
        reply = response.choices[0].message.content
        user_memory[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(f"💡 {reply}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Xato yuz berdi: {str(e)}")

# Botni ishga tushurish
if __name__ == "__main__":
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.add_handler(MessageHandler(filters.COMMAND, chat))
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()






