import sqlite3
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
TOKEN = "YAHAN_APNA_NAYA_BOT_TOKEN_DALNA"

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
