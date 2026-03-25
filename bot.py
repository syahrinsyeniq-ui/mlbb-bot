import os
import logging
from dotenv import load_dotenv
import requests
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

load_dotenv()
BOT_TOKEN = os.getenv("8760375355:AAE3Bzw1Byf0J25EpzaJ1BdGPeEONi8M014")
assert BOT_TOKEN, "8760375355:AAE3Bzw1Byf0J25EpzaJ1BdGPeEONi8M014"

# Server List
SERVERS = {
    "id": 20000, "ina": 20000, "indonesia": 20000,
    "my": 20100, "malaysia": 20100,
    "ph": 20200, "philippines": 20200,
    "sg": 20300, "singapore": 20300,
    "tw": 20400, "taiwan": 20400,
    "vn": 20500, "vietnam": 20500,
    "mm": 20600, "myanmar": 20600,
    "global": 22000
}

ML_APIS = [
    "https://ml-api.lolivalkyrie.com",
    "https://api-mlbb.bahrul.id", 
    "https://mlbb-data.herokuapp.com"
]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Cek Akun ML", callback_data="cek")],
        [InlineKeyboardButton("🌍 List Server", callback_data="server")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *MLBB Info Bot v2.1*\n\n"
        "📝 *Cara pakai:*\n"
        "• Kirim ID ML\n"
        "• `/info 123456789 20000`\n\n"
        "*Contoh:* `123456789`", 
        parse_mode='Markdown', reply_markup=reply_markup
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info [id] [server]"""
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "ℹ️ *Perintah /info*\n\n"
            "**Format:** `/info [ID] [SERVER]`\n\n"
            "*Contoh:*\n"
            "`/info 123456789 20000` → Indonesia\n"
            "`/info 123456789 20100` → Malaysia\n\n"
            "**Server Populer:**\n"
            "• `20000` = Indonesia\n"
            "• `20100` = Malaysia\n"
            "• `20200` = Philippines\n"
            "• `20300` = Singapore", 
            parse_mode='Markdown'
        )
        return
    
    # Parse args: ID + SERVER
    ml_id = args[0] if args[0].isdigit() else None
    server_id = 20000  # Default Indonesia
    
    if len(args) > 1 and args[1].isdigit():
        server_id = int(args[1])
    elif len(args) > 1:
        # Parse server name
        server_name = args[1].lower()
        server_id = SERVERS.get(server_name, 20000)
    
    if not ml_id or len(ml_id) != 9:
        await update.message.reply_text("❌ ID harus 9 digit angka!")
        return
    
    await check_account(update, ml_id, server_id, f"Server: {server_id}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "cek":
        await query.edit_message_text("📝 Kirim ID ML (9 digit)")
    elif query.data == "server":
        server_text = "**🌍 Server MLBB:**\n\n"
        for name, sid in SERVERS.items():
            server_text += f"• `{sid}` = {name.title()}\n"
        server_text += "\n*Gunakan:* `/info ID SERVER`"
        await query.edit_message_text(server_text, parse_mode='Markdown')

async def check_ml_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text message (ID only)"""
    ml_id = update.message.text.strip()
    await check_account(update, ml_id, 20000, "Server Indonesia")

async def check_account(update: Update, ml_id: str, server_id: int, status_msg: str):
    """Core check function"""
    if not (ml_id.isdigit() and len(ml_id) == 9):
        await update.message.reply_text("❌ ID harus **9 digit angka**!", parse_mode='Markdown')
        return
    
    await update.message.reply_text(f"⏳ *{status_msg}*", parse_mode='Markdown')
    
    # Try APIs
    player_data = None
    for api_url in ML_APIS:
        try:
            if "lolivalkyrie" in api_url:
                url = f"{api_url}/v1/public/player/information"
                params = {"playerId": ml_id, "serverId": server_id}
            else:
                url = f"{api_url}/player/{ml_id}?server={server_id}"
                params = {}
            
            resp = requests.get(url, params=params, timeout=8)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data') or data.get('userInfo') or data.get('player'):
                    player_data = data
                    break
                    
        except:
            continue
    
    if not player_data:
        await update.message.reply_text(f"❌ Akun `{ml_id}` tidak ditemukan di server `{server_id}`!", parse_mode='Markdown')
        return
    
    # Parse & Send
    try:
        player = player_data.get('data') or player_data.get('userInfo') or player_data
        server_name = next((name for name, sid in SERVERS.items() if sid == server_id), "Unknown")
        
        info = f"""
🎮 *MLBB PLAYER INFO*

🆔 **ID:** `{ml_id}`
🌍 **Server:** `{server_id}` ({server_name.title()})
👤 **Nama:** {player.get('name', player.get('nickname', 'N/A'))}
⭐ **Bintang:** {player.get('star', 0)}
🏆 **Rank:** {player.get('rank', player.get('rankName', 'N/A'))}
⚔️ **Winrate:** {player.get('winRate', 0)}%
💎 **Elo/Score:** {player.get('elo', player.get('score', 0))}

📊 **Total Match:** {player.get('matchCount', 0)}
✅ **Wins:** {player.get('winCount', 0)}
❌ **Losses:** {player.get('loseCount', 0)}
        """
        
        await update.message.reply_text(info.strip(), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Parse error: {e}")
        await update.message.reply_text("❌ Error parsing data!")

def main():
    print("🤖 MLBB Bot v2.1 Starting...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_ml_id))
    
    print("🚀 Bot LIVE!")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
