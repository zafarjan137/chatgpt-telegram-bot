import os

print("DEBUG ENVIRONMENT:")
for k, v in os.environ.items():
    if "BOT" in k or "TOKEN" in k:
        print(k, "=", v)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

# --- TOKENLARNI ENVIRONMENTS'DAN O‘QISH ---
bot_token = os.getenv("BOT_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

print("BOT_TOKEN:", bot_token)
print("OPENAI_API_KEY:", openai_api_key)

# --- TEKSHIRISH ---
if not bot_token:
    raise ValueError("❌ BOT_TOKEN environment variable topilmadi!")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY environment variable topilmadi!")

# --- OPENAI CLIENT ---
client = OpenAI(api_key=openai_api_key)

ADMIN_ID = 6079100324
user_memory = {}

# --- START komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 Yordam", callback_data="help")],
        [InlineKeyboardButton("🔁 Qayta boshlash", callback_data="restart")],
        [InlineKeyboardButton("👤 Haqimda", callback_data="about")]
    ]
    await update.message.reply_text(
        "👋 Salom! Men ChatGPT asosidagi AI botman.\nSavolingizni yozing!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- CALLBACK BUTTON ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "help":
        await query.edit_message_text("ℹ️ Men sizga yordam bera olaman!")
    elif query.data == "restart":
        user_memory.clear()
        await query.edit_message_text("🔁 Yangi suhbat boshlandi!")
    elif query.data == "about":
        await query.edit_message_text("🤖 GPT asosidagi AI bot.")

# --- CHAT ---
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
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
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Xato: {e}")

# --- BOTNI ISHGA TUSHURISH ---
if __name__ == "__main__":
    print("🤖 Bot ishga tushmoqda...")
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()







