from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
Application,
CommandHandler,
MessageHandler,
ContextTypes,
filters,
)
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

MENU = """
🥛 Ixlos Sut Bot

Mahsulotlar:

🥛 1 litr sut — 12 000 so'm

Buyurtma berish uchun ismingizni yozing.
"""

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(MENU)

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user.id
text = update.message.text

if user not in users:  
    users[user] = {"name": text}  
    kb = ReplyKeyboardMarkup(  
        [[{"text": "📞 Telefon raqamni yuborish", "request_contact": True}]],  
        resize_keyboard=True,  
        one_time_keyboard=True,  
    )  
    await update.message.reply_text(  
        "Telefon raqamingizni yuboring.",  
        reply_markup=kb,  
    )  
    return  

users[user]["address"] = text  

data = users[user]  

msg = f"""

🛒 Yangi buyurtma

👤 Ism: {data['name']}
📍 Manzil: {data['address']}
"""

await context.bot.send_message(ADMIN_ID, msg)  

await update.message.reply_text(  
    "✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog'lanamiz."  
)

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

app.run_polling()

if name == "main":
main()
