import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = "".join(os.getenv("BOT_TOKEN", "").split())

MAIN_TEXT = """🤖 کارتن‌یار جامع

به سامانه جامع کارتن‌یار خوش آمدید.
از منوی زیر بخش موردنظر خود را انتخاب کنید:"""

def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 ثبت آگهی", callback_data="ad"),
            InlineKeyboardButton("🔎 جستجوی آگهی", callback_data="search"),
        ],
        [
            InlineKeyboardButton("🏭 بانک شرکت‌ها", callback_data="companies"),
            InlineKeyboardButton("📦 محصولات و خدمات", callback_data="products"),
        ],
        [
            InlineKeyboardButton("👥 گروه‌های کارتن‌یار", callback_data="groups"),
            InlineKeyboardButton("💬 پشتیبانی", callback_data="support"),
        ],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MAIN_TEXT, reply_markup=main_keyboard())

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(MAIN_TEXT, reply_markup=main_keyboard())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    messages = {
        "ad": "📢 ثبت آگهی\n\nدر نسخه بعدی، ثبت آگهی خرید و فروش را فعال می‌کنیم.",
        "search": "🔎 جستجوی آگهی\n\nدر نسخه بعدی، جستجوی آگهی‌ها را فعال می‌کنیم.",
        "companies": "🏭 بانک شرکت‌ها\n\nدر این بخش اطلاعات شرکت‌ها و تولیدکنندگان صنعت سلولزی قرار می‌گیرد.",
        "products": "📦 محصولات و خدمات\n\nدسته‌بندی محصولات، مواد اولیه، ماشین‌آلات و خدمات در این بخش قرار می‌گیرد.",
        "groups": "👥 گروه‌های کارتن‌یار\n\nفهرست گروه‌های تخصصی کارتن‌یار در این بخش قرار می‌گیرد.",
        "support": "💬 پشتیبانی\n\nبرای ارتباط با مدیریت کارتن‌یار، پیام خود را ارسال کنید."
    }

    text = messages.get(query.data, MAIN_TEXT)
    keyboard = main_keyboard() if query.data not in messages else InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="home")]]
    )
    await query.edit_message_text(text, reply_markup=keyboard)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Exception while handling update:", exc_info=context.error)
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

def main():
    if not TOKEN:
        raise RuntimeError ("BOT_TOKEN is not set")
        threading.Thread(target=run_health_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(error_handler)

    print("KartonYarMarketBot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
