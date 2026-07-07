import sqlite3
import os

TOKEN = os.getenv("BOT_TOKEN")
import logging
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

# ==========================
# BOT TOKEN
# ==========================
TOKEN = os.getenv("BOT_TOKEN")

# ==========================
# DATABASE
# ==========================
conn = sqlite3.connect("payments.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS totals (
    chat_id INTEGER PRIMARY KEY,
    total INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    user_name TEXT,
    amount INTEGER
)
""")

conn.commit()

logging.basicConfig(level=logging.INFO)
# ==========================
# FUNCTIONS
# ==========================

def get_total(chat_id):
    cursor.execute(
        "SELECT total FROM totals WHERE chat_id=?",
        (chat_id,)
    )
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        "INSERT INTO totals(chat_id,total) VALUES(?,?)",
        (chat_id, 0)
    )
    conn.commit()
    return 0


def update_total(chat_id, amount, user):
    total = get_total(chat_id)
    total += amount

    cursor.execute(
        "UPDATE totals SET total=? WHERE chat_id=?",
        (total, chat_id)
    )

    cursor.execute(
        "INSERT INTO history(chat_id,user_name,amount) VALUES(?,?,?)",
        (chat_id, user, amount)
    )

    conn.commit()
    return total


async def total_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = get_total(update.effective_chat.id)

    await update.message.reply_text(
        f"💰 Total Payment = {total}"
    )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id,
    )

    if member.status not in ["creator"]:
        await update.message.reply_text(
            "❌ Sirf Owner Reset Kar Sakta Hai."
        )
        return

    cursor.execute(
        "UPDATE totals SET total=0 WHERE chat_id=?",
        (update.effective_chat.id,)
    )
    conn.commit()

    await update.message.reply_text(
        "✅ Total Reset Ho Gaya."
    )
    # ==========================
# MESSAGE HANDLER
# ==========================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    text = update.message.text.strip()

    match = re.match(r"^([+-])(\d+)$", text)

    if not match:
        return

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        return

    sign = match.group(1)
    amount = int(match.group(2))

    if sign == "-":
        amount = -amount

    total = update_total(
        update.effective_chat.id,
        amount,
        update.effective_user.first_name
    )

    await update.message.reply_text(
        f"✅ Total Payment: {total}"
    )# ==========================
# MAIN
# ==========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("total", total_command))
app.add_handler(CommandHandler("reset", reset_command))
app.add_handler(
    MessageHandler(
        filters.TEXT & (~filters.COMMAND),
        message_handler
    )
)

print("Bot Started...")

app.run_polling()
