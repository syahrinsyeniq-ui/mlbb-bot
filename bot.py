import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Konfigurasi
BOT_TOKEN = "8760375355:AAGKrsrtgJkxXx4p3OIFW5AyvQQ7VUeqdIQ"
ML_API_BASE = "https://mlbb-api-production-api.lolivalkyrievalorant.com"

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /start"""
    keyboard = [
        [InlineKeyboardButton("📊 Cek Info Akun ML", callback_data="check_ml")],
        [InlineKeyboardButton("ℹ️ Cara Cek ID ML", callback_data="how_to")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *Bot Cek Info MLBB*\n\n"
        "Kirim **ID ML** kamu untuk cek info akun!\n\n"
        "*Contoh:* `123456789`", 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_ml":
        await query.edit_message_text(
            "📝 *Kirim ID ML kamu*\n\n"
            "Contoh: `123456789` (9 digit)", 
            parse_mode='Markdown'
        )
    elif query.data == "how_to":
        await query.edit_message_text(
            "🔍 *Cara Cek ID ML:*\n\n"
            "1. Buka MLBB\n"
            "2. Klik profil (pojok kiri atas)\n"
            "3. ID ada di bagian atas (9 digit)\n\n"
            "*Contoh:* `123456789`",
            parse_mode='Markdown'
        )

async def check_ml_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cek info MLBB berdasarkan ID"""
    user_id = update.message.from_user.id
    ml_id = update.message.text.strip()
    
    # Validasi ID (9 digit)
    if not ml_id.isdigit() or len(ml_id) != 9:
        await update.message.reply_text("❌ ID harus 9 digit angka!\nContoh: `123456789`")
        return
    
    await update.message.reply_text("⏳ Sedang mencari info akun...")
    
    try:
        # API request ke MLBB official
        url = f"{ML_API_BASE}/v1/public/player/information"
        params = {
            "playerId": ml_id,
            "serverId": 20000  # Server Indonesia
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get('data'):
            player = data['data']
            
            # Buat embed info
            info_text = f"""
🎮 *INFO AKUN MLBB*

🆔 **ID:** `{ml_id}`
👤 **Nama:** {player.get('name', 'N/A')}
⭐ **Star:** {player.get('star', 0)}
🏆 **Rank:** {player.get('rank', 'N/A')}
⚔️ **Winrate:** {player.get('winRate', 0)}%
💎 **Elo:** {player.get('elo', 0)}
👑 **Highest Rank:** {player.get('highestRank', 'N/A')}

📊 **Matches:** {player.get('matchCount', 0)}
✅ **Wins:** {player.get('winCount', 0)}
❌ **Losses:** {player.get('loseCount', 0)}
            """
            
            await update.message.reply_text(info_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Akun tidak ditemukan atau data tidak tersedia!")
            
    except requests.exceptions.RequestException:
        await update.message.reply_text("❌ Error koneksi! Coba lagi nanti.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan! Coba lagi.")

def main():
    """Main function"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_ml_id))
    
    print("🤖 Bot MLBB Info started!")
    app.run_polling()

if __name__ == '__main__':
    main()
