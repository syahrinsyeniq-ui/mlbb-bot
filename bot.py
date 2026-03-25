import os, logging, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8760375355:AAE3Bzw1Byf0J25EpzaJ1BdGPeEONi8M014")
print("🤖 MLBB Bot")

if not BOT_TOKEN:
    print("❌ No token - set railway variables")
else:
    print("✅ Token OK")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 MLBB\n/info ID 20000")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    ml_id = args[0] if args else "0"
    server = int(args[1]) if len(args) > 1 else 20000
    
    await update.message.reply_text(f"⏳ {ml_id}")
    
    url = "https://ml-api.lolivalkyrie.com/v1/public/player/information"
    r = requests.get(url, params={"playerId": ml_id, "serverId": server})
    data = r.json()
    
    if r.status_code == 200 and data.get('data'):
        p = data['data']
        await update.message.reply_text(f"""🎮 ML
ID: {ml_id}
Name: {p.get('name')}
Rank: {p.get('rank')}
Elo: {p.get('elo')}""")
    else:
        await update.message.reply_text("❌ Not found")

def main():
    if not BOT_TOKEN:
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.run_polling()

if __name__ == '__main__':
    main()
