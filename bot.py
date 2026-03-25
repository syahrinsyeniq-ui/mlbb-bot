import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Get token from Railway ENV
BOT_TOKEN = os.getenv("8760375355:AAE3Bzw1Byf0J25EpzaJ1BdGPeEONi8M014")

print("🤖 MLBB Bot Starting...")

# NO ASSERT - Always continue
if not BOT_TOKEN:
    print("⚠️  BOT_TOKEN kosong - cek Railway Variables")
else:
    print(f"✅ Token detected")

# Config
SERVERS = {
    "id": 20000, "ina": 20000,
    "my": 20100, "ph": 20200, 
    "sg": 20300, "vn": 20500,
    "global": 22000
}

ML_APIS = ["https://ml-api.lolivalkyrie.com"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not BOT_TOKEN:
        await update.message.reply_text("❌ Bot error - cek Railway Variables")
        return
        
    keyboard = [[InlineKeyboardButton("📊 Cek ML", callback_data="cek")]]
    await update.message.reply_text(
        "🤖 *MLBB Bot*\n\n`/info ID SERVER`\n*Contoh:* `/info 123456789 20000`", 
        parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not BOT_TOKEN:
        await update.message.reply_text("❌ Error - cek /start")
        return
    
    ml_id = args[0]
    server_id = 20000
    if len(args) > 1 and args[1].isdigit():
        server_id = int(args[1])
    
    if len(ml_id) != 9 or not ml_id.isdigit():
        await update.message.reply_text("❌ ID 9 digit!")
        return
    
    await check_account(update, ml_id, server_id)

async def check_account(update: Update, ml_id: str, server_id: int):
    await update.message.reply_text(f"⏳ `{ml_id}` - Server `{server_id}`")
    
    try:
        url = f"https://ml-api.lolivalkyrie.com/v1/public/player/information"
        params = {"playerId": ml_id, "serverId": server_id}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if resp.status_code == 200 and data.get('data'):
            player = data['data']
            info = f"""🎮 *ML INFO*

🆔 `{ml_id}`
🌍 `{server_id}`
👤 {player.get('name', 'N/A')}
⭐ {player.get('star', 0)}
🏆 {player.get('rank', 'N/A')}
💎 {player.get('elo', 0)}

📊 Match: {player.get('matchCount', 0)}
✅ Win: {player.get('winCount', 0)}"""
            await update.message.reply_text(info, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Akun `{ml_id}` server `{server_id}` tidak ditemukan")
    except:
        await update.message.reply_text("❌ API error - coba lagi")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("📝 `/info ID 20000`")

async def check_ml_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ml_id = update.message.text.strip()
    if len(ml_id) == 9 and ml_id.isdigit():
        await check_account(update, ml_id, 20000)

def main():
    if not BOT_TOKEN:
        print("❌ Cannot start - no BOT_TOKEN")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_ml_id))
    
    print("🚀 Bot started!")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
