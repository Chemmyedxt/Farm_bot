import os, json, logging, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Logging
logging.basicConfig(level=logging.INFO)

# 👇 YOUR BOT TOKEN (you can hide later via env)
BOT_TOKEN = "7903534242:AAHOGE3qF3xpevpMgcD4P-dYsmTnhFvz6JA"
DATA_FILE = "farmers.json"

# Sample airdrop links
farming_links = [
    {"name": "drip.haus (NFTs)", "url": "https://drip.haus"},
    {"name": "Jito Airdrop", "url": "https://jito.network/airdrop"},
    {"name": "Zealy", "url": "https://zealy.io"},
    {"name": "Galxe", "url": "https://galxe.com"},
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to FARMY Bot!\nUse /links, /mine, /balance, /leaderboard")

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(link["name"], url=link["url"])] for link in farming_links]
    await update.message.reply_text("🪂 Today's real quests:", reply_markup=InlineKeyboardMarkup(buttons))

async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    user = data.get(user_id, {"farm": 0, "last": 0})
    now = time.time()

    if now - user["last"] < 3600:
        mins = int((3600 - (now - user["last"])) // 60)
        return await update.message.reply_text(f"⛏️ Cooldown: wait {mins} minutes.")

    user["farm"] += 1
    user["last"] = now
    data[user_id] = user
    save_data(data)

    await update.message.reply_text(f"✅ You mined 1 $FARM!\n💰 Balance: {user['farm']} $FARM")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    user = data.get(user_id, {"farm": 0})
    await update.message.reply_text(f"💼 Your balance: {user['farm']} $FARM")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        return await update.message.reply_text("🏆 No miners yet.")

    sorted_users = sorted(data.items(), key=lambda x: x[1].get("farm", 0), reverse=True)[:10]
    message = "🏆 Top Miners:\n"
    for i, (uid, u) in enumerate(sorted_users, 1):
        message += f"{i}. User {uid[-4:]} — {u['farm']} $FARM\n"
    await update.message.reply_text(message)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — Welcome\n"
        "/links — Daily airdrops\n"
        "/mine — Mine $FARM hourly\n"
        "/balance — Check your balance\n"
        "/leaderboard — Top users\n"
        "/help — Show this menu"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("links", links))
    app.add_handler(CommandHandler("mine", mine))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("help", help_cmd))
    print("Bot running...")
    app.run_polling()
