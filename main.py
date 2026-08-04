from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id] = {}

    await update.message.reply_text(
        "🥛 Assalomu alaykum!\n\nIxlos Sut Botga xush kelibsiz.\n\nIsmingizni yozing."
    )

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    text = update.message.text

    if "name" not in users[user]:
        users[user]["name"] = text

        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

        await update.message.reply_text(
            "Telefon raqamingizni yuboring.",
            reply_markup=keyboard,
        )
        return

    if "phone" in users[user] and "address" not in users[user]:
        users[user]["address"] = text

        data = users[user]

        msg = f"""
🛒 Yangi buyurtma

👤 Ism: {data['name']}
📞 Telefon: {data['phone']}
📍 Manzil: {data['address']}

🥛 Mahsulot:
1 litr sut — 12 000 so'm
"""

        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

        await update.message.reply_text(
            "✅ Buyurtmangiz qabul qilindi.\nTez orada siz bilan bog'lanamiz."
        )

        users.pop(user)

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id

    users[user]["phone"] = update.message.contact.phone_number

    await update.message.reply_text(
        "📍 Endi manzilingizni yozing."
    )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
