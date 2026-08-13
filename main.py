from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6544312652"))

PRODUCTS = {
    "sut": ("🥛 Sut", 12000, "litr"),
    "qatiq": ("🥛 Qatiq", 13000, "litr"),
    "qaymoq": ("🧈 Qaymoq", 70000, "kg"),
    "tvorog": ("🧀 Tvorog", 35000, "kg"),
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cart"] = {}

    keyboard = [
        [InlineKeyboardButton("🥛 Sut — 12 000 so'm/litr", callback_data="sut")],
        [InlineKeyboardButton("🥛 Qatiq — 13 000 so'm/litr", callback_data="qatiq")],
        [InlineKeyboardButton("🧈 Qaymoq — 70 000 so'm/kg", callback_data="qaymoq")],
        [InlineKeyboardButton("🧀 Tvorog — 35 000 so'm/kg", callback_data="tvorog")],
        [InlineKeyboardButton("🛒 Savatcha", callback_data="cart")],
    ]

    await update.message.reply_text(
        "🧺 *Ixlos Sut mahsulotlari*\n\n"
        "Mahsulotni tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cart":
        await show_cart(query, context)
        return

    if query.data in PRODUCTS:
        context.user_data["selected_product"] = query.data

        name, price, unit = PRODUCTS[query.data]

        await query.message.reply_text(
            f"{name}\n"
            f"💰 Narxi: {price:,} so'm / {unit}\n\n"
            "Necha dona/litr/kg kerakligini yozing.\n"
            "Masalan: 2"
        )
        context.user_data["waiting_quantity"] = True


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if context.user_data.get("waiting_quantity"):
        try:
            quantity = float(text.replace(",", "."))
            if quantity <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text(
                "❗ Iltimos, miqdorni raqam bilan yozing.\nMasalan: 2"
            )
            return

        product_key = context.user_data["selected_product"]
        name, price, unit = PRODUCTS[product_key]

        cart = context.user_data.setdefault("cart", {})
        cart[product_key] = cart.get(product_key, 0) + quantity

        context.user_data["waiting_quantity"] = False

        total = quantity * price

        keyboard = [
            [
                InlineKeyboardButton("🛍 Yana mahsulot", callback_data="more"),
                InlineKeyboardButton("🛒 Savatcha", callback_data="cart")
            ]
        ]

        await update.message.reply_text(
            f"✅ Qo‘shildi!\n\n"
            f"{name}\n"
            f"📦 Miqdor: {quantity:g} {unit}\n"
            f"💰 Narxi: {total:,.0f} so'm",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if context.user_data.get("waiting_address"):
        context.user_data["address"] = text
        context.user_data["waiting_address"] = False

        await send_order(update, context)
        return

    await update.message.reply_text(
        "Mahsulot tanlash uchun /start ni bosing."
    )


async def show_cart(query, context):
    cart = context.user_data.get("cart", {})

    if not cart:
        await query.message.reply_text(
            "🛒 Savatchangiz hozircha bo‘sh.\n/start ni bosib mahsulot tanlang."
        )
        return

    text = "🛒 *Savatchangiz:*\n\n"
    total = 0

    for key, quantity in cart.items():
        name, price, unit = PRODUCTS[key]
        summa = quantity * price
        total += summa

        text += f"{name}\n"
        text += f"📦 {quantity:g} {unit} × {price:,} = {summa:,.0f} so'm\n\n"

    text += f"💰 *Jami: {total:,.0f} so'm*"

    keyboard = [
        [InlineKeyboardButton("✅ Buyurtma berish", callback_data="order")],
        [InlineKeyboardButton("🛍 Yana mahsulot", callback_data="more")]
    ]

    await query.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def more_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🥛 Sut — 12 000 so'm/litr", callback_data="sut")],
        [InlineKeyboardButton("🥛 Qatiq — 13 000 so'm/litr", callback_data="qatiq")],
        [InlineKeyboardButton("🧈 Qaymoq — 70 000 so'm/kg", callback_data="qaymoq")],
        [InlineKeyboardButton("🧀 Tvorog — 35 000 so'm/kg", callback_data="tvorog")],
        [InlineKeyboardButton("🛒 Savatcha", callback_data="cart")],
    ]

    await query.message.reply_text(
        "Mahsulotni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[
        KeyboardButton("📱 Telefon raqamimni yuborish", request_contact=True)
    ]]

    await query.message.reply_text(
        "📱 Buyurtmani rasmiylashtirish uchun telefon raqamingizni yuboring.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.contact.phone_number
    context.user_data["waiting_address"] = True

    await update.message.reply_text(
        "📍 Endi yetkazib berish manzilingizni yozing."
    )


async def send_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", {})
    phone = context.user_data.get("phone", "Noma'lum")
    address = context.user_data.get("address", "Noma'lum")

    total = 0
    order_text = "🆕 *YANGI BUYURTMA!*\n\n"

    for key, quantity in cart.items():
        name, price, unit = PRODUCTS[key]
        summa = quantity * price
        total += summa

        order_text += (
            f"{name}\n"
            f"📦 {quantity:g} {unit}\n"
            f"💰 {summa:,.0f} so'm\n\n"
        )

    order_text += (
        f"💵 *JAMI: {total:,.0f} so'm*\n\n"
        f"📱 Telefon: {phone}\n"
        f"📍 Manzil: {address}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=order_text,
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "✅ Buyurtmangiz qabul qilindi!\n\n"
        f"💰 Jami: {total:,.0f} so'm\n\n"
        "Tez orada siz bilan bog‘lanamiz."
    )

    context.user_data.clear()


async def error(update: object, context: ContextTypes.DEFAULT_TYPE):
    print("Xatolik:", context.error)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern="^(sut|qatiq|qaymoq|tvorog|cart)$"))
    app.add_handler(CallbackQueryHandler(more_products, pattern="^more$"))
    app.add_handler(CallbackQueryHandler(order, pattern="^order$"))
    app.add_handler(MessageHandler(filters.CONTACT, contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

    app.add_error_handler(error)

    print("Ixlos Sut Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
