import aiohttp
import logging
import os
import telegram
import datetime
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup,constants
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes,CallbackQueryHandler,ConversationHandler
from telegram.request import HTTPXRequest
import sqlite3
import asyncio
import pytz
mm_tz = pytz.timezone('Asia/Yangon')
async def start_db():
        conn = sqlite3.connect('coinmap.db')
        cursor = conn.cursor()
        return conn,cursor
conn = sqlite3.connect('coinmap.db')
cursor = conn.cursor()
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id varchar(100) not null,
        base_code VARCHAR(100),
        compare_code VARCHAR(100),
        auto_send VARCHAR(100)
);
""")
conn.commit()
conn.close()

logging.basicConfig(
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level = logging.INFO
)
logger = logging.getLogger(__name__)
token = os.getenv('token')

async def currency():
        currency_data = {
                "CNY": {"country": "China 🇨🇳", "symbol": "¥"},
                "JPY": {"country": "Japan 🇯🇵", "symbol": "¥"},
                "KRW": {"country": "South Korea 🇰🇷", "symbol": "₩"},
                "HKD": {"country": "Hong Kong 🇭🇰", "symbol": "HK$"},
                "MOP": {"country": "Macau 🇲🇴", "symbol": "Pica"},
                "TWD": {"country": "Taiwan 🇹🇼", "symbol": "NT$"},
                "MNT": {"country": "Mongolia 🇲🇳", "symbol": "₮"},
                "KPW": {"country": "North Korea 🇰🇵", "symbol": "₩"},
                "MMK": {"country": "Myanmar 🇲🇲", "symbol": "Ks"},
                "SGD": {"country": "Singapore 🇸🇬", "symbol": "S$"},
                "IDR": {"country": "Indonesia 🇮🇩", "symbol": "Rp"},
                "THB": {"country": "Thailand 🇹🇭", "symbol": "฿"},
                "MYR": {"country": "Malaysia 🇲🇾", "symbol": "RM"},
                "PHP": {"country": "Philippines 🇵🇭", "symbol": "₱"},
                "VND": {"country": "Vietnam 🇻🇳", "symbol": "₫"},
                "KHR": {"country": "Cambodia 🇰🇭", "symbol": "៛"},
                "LAK": {"country": "Laos 🇱🇦", "symbol": "₭"},
                "BND": {"country": "Brunei 🇧🇳", "symbol": "B$"},
                "USD_TL": {"country": "Timor-Leste 🇹🇱", "symbol": "$"},
                "INR": {"country": "India 🇮🇳", "symbol": "₹"},
                "PKR": {"country": "Pakistan 🇵🇰", "symbol": "₨"},
                "BDT": {"country": "Bangladesh 🇧🇩", "symbol": "৳"},
                "LKR": {"country": "Sri Lanka 🇱🇰", "symbol": "Rs"},
                "NPR": {"country": "Nepal 🇳🇵", "symbol": "₨"},
                "AFN": {"country": "Afghanistan 🇦🇫", "symbol": "؋"},
                "MVR": {"country": "Maldives 🇲🇻", "symbol": ".ރ"},
                "BTN": {"country": "Bhutan 🇧🇹", "symbol": "Nu."},
                "SAR": {"country": "Saudi Arabia 🇸🇦", "symbol": "SR"},
                "AED": {"country": "United Arab Emirates 🇦🇪", "symbol": "د.إ"},
                "ILS": {"country": "Israel 🇮🇱", "symbol": "₪"},
                "TRY": {"country": "Turkey 🇹🇷", "symbol": "₺"},
                "QAR": {"country": "Qatar 🇶🇦", "symbol": "QR"},
                "KWD": {"country": "Kuwait 🇰🇼", "symbol": "KD"},
                "OMR": {"country": "Oman 🇴🇲", "symbol": "RO"},
                "BHD": {"country": "Bahrain 🇧🇭", "symbol": "BD"},
                "JOD": {"country": "Jordan 🇯🇴", "symbol": "JD"},
                "LBP": {"country": "Lebanon 🇱🇧", "symbol": "ل.ل"},
                "ILS_PS": {"country": "Palestine 🇵🇸", "symbol": "₪"},
                "SYP": {"country": "Syria 🇸🇾", "symbol": "LS"},
                "YER": {"country": "Yemen 🇾🇪", "symbol": "﷼"},
                "IQD": {"country": "Iraq 🇮🇶", "symbol": "ع.د"},
                "IRR": {"country": "Iran 🇮🇷", "symbol": "﷼"},
                "EUR_CY": {"country": "Cyprus 🇨🇾", "symbol": "€"},
                "GEL": {"country": "Georgia 🇬🇪", "symbol": "₾"},
                "AMD": {"country": "Armenia 🇦🇲", "symbol": "֏"},
                "AZN": {"country": "Azerbaijan 🇦🇿", "symbol": "₼"},
                "KZT": {"country": "Kazakhstan 🇰🇿", "symbol": "₸"},
                "UZS": {"country": "Uzbekistan 🇺🇿", "symbol": "soʻm"},
                "TMT": {"country": "Turkmenistan 🇹🇲", "symbol": "m"},
                "KGS": {"country": "Kyrgyzstan 🇰🇬", "symbol": "ل.ص"},
                "TJS": {"country": "Tajikistan 🇹🇯", "symbol": "SM"},
                "RUB": {"country": "Russia 🇷🇺", "symbol": "₽"},
                "USD": {"country": "United States 🇺🇸", "symbol": "$"},
                "EUR": {"country": "Eurozone 🇪🇺", "symbol": "€"},
                "AUD": {"country": "Australia 🇦🇺", "symbol": "A$"},
                "GBP": {"country": "United Kingdom 🇬🇧", "symbol": "£"},
        }


        return currency_data

#Start Command
async def start(update: Update,context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(r"""
🌍 Welcome to Coin Map!

💱 Your Smart Currency Exchange Assistant

With Coin Map, you can easily check exchange rates between different currencies from around the world.

✨ How to Use:

🔹 Check Exchange Rate – Find the latest exchange rate between two currencies.

🔹 Base Currency – Choose the currency you want to exchange from.

🔹 Target Currency – Select the currency you want to exchange into.

⚠️ Warning!

If the buttons are not work use /restart


🚀 Let's get started!

Select a base currency below to begin.

""",reply_markup = await base_keyboard(),parse_mode=constants.ParseMode.HTML)
        return 0


#=========[ Keyboards ]==========

async def base_keyboard():
        base_keys = [
                [
                InlineKeyboardButton('USD 🇺🇸', callback_data="usd"),
                InlineKeyboardButton('EUR 🇪🇺', callback_data="eur"),
                ],
                [
                InlineKeyboardButton('AUD 🇦🇺', callback_data="aud"),
                InlineKeyboardButton('GBP 🇬🇧', callback_data="gbp"),
                ],
                [
                InlineKeyboardButton('CNY 🇨🇳', callback_data="cny"),
                InlineKeyboardButton('JPY 🇯🇵', callback_data="jpy"),
                ],
                [
                InlineKeyboardButton('KRW 🇰🇷', callback_data="krw"),
                InlineKeyboardButton('HKD 🇭🇰', callback_data="hkd"),
                ],
                [
                InlineKeyboardButton('MOP 🇲🇴', callback_data="mop"),
                InlineKeyboardButton('TWD 🇹🇼', callback_data="twd"),
                ],
                [
                InlineKeyboardButton('MNT 🇲🇳', callback_data="mnt"),
                InlineKeyboardButton('KPW 🇰🇵', callback_data="kpw"),
                ],
                [
                InlineKeyboardButton('MMK 🇲🇲', callback_data="mmk"),
                InlineKeyboardButton('SGD 🇸🇬', callback_data="sgd"),
                ],
                [
                InlineKeyboardButton('IDR 🇮🇩', callback_data="idr"),
                InlineKeyboardButton('THB 🇹🇭', callback_data="thb"),
                ],
                [
                InlineKeyboardButton('MYR 🇲🇾', callback_data="myr"),
                InlineKeyboardButton('PHP 🇵🇭', callback_data="php"),
                ],
                [
                InlineKeyboardButton('VND 🇻🇳', callback_data="vnd"),
                InlineKeyboardButton('KHR 🇰🇭', callback_data="khr"),
                ],
                [
                InlineKeyboardButton('LAK 🇱🇦', callback_data="lak"),
                InlineKeyboardButton('BND 🇧🇳', callback_data="bnd"),
                ],
                [
                InlineKeyboardButton('USD (Timor) 🇹🇱', callback_data="usd_tl"),
                InlineKeyboardButton('IRR 🇮🇷', callback_data="irr"),
                ],
                [
                InlineKeyboardButton('INR 🇮🇳', callback_data="inr"),
                InlineKeyboardButton('PKR 🇵🇰', callback_data="pkr"),
                ],
                [
                InlineKeyboardButton('BDT 🇧🇩', callback_data="bdt"),
                InlineKeyboardButton('LKR 🇱🇰', callback_data="lkr"),
                ],
                [
                InlineKeyboardButton('NPR 🇳🇵', callback_data="npr"),
                InlineKeyboardButton('AFN 🇦🇫', callback_data="afn"),
                ],
                [
                InlineKeyboardButton('MVR 🇲🇻', callback_data="mvr"),
                InlineKeyboardButton('BTN 🇧🇹', callback_data="btn"),
                ],

                [
                InlineKeyboardButton('SAR 🇸🇦', callback_data="sar"),
                InlineKeyboardButton('AED 🇦🇪', callback_data="aed"),
                ],
                [
                InlineKeyboardButton('ILS 🇮🇱', callback_data="ils"),
                InlineKeyboardButton('TRY 🇹🇷', callback_data="try"),
                ],
                [
                InlineKeyboardButton('QAR 🇶🇦', callback_data="qar"),
                InlineKeyboardButton('KWD 🇰🇼', callback_data="kwd"),
                ],
                [
                InlineKeyboardButton('OMR 🇴🇲', callback_data="omr"),
                InlineKeyboardButton('BHD 🇧🇭', callback_data="bhd"),
                ],
                [
                InlineKeyboardButton('JOD 🇯🇴', callback_data="jod"),
                InlineKeyboardButton('LBP 🇱🇧', callback_data="lbp"),
                ],
                [
                InlineKeyboardButton('ILS (Palestine) 🇵🇸', callback_data="ils_ps"),
                InlineKeyboardButton('SYP 🇸🇾', callback_data="syp"),
                ],
                [
                InlineKeyboardButton('YER 🇾🇪', callback_data="yer"),
                InlineKeyboardButton('IQD 🇮🇶', callback_data="iqd"),
                ],
                [
                InlineKeyboardButton('EUR (Cyprus) 🇨🇾', callback_data="eur_cy"),
                InlineKeyboardButton('GEL 🇬🇪', callback_data="gel"),
                ],
                [
                InlineKeyboardButton('AMD 🇦🇲', callback_data="amd"),
                InlineKeyboardButton('AZN 🇦🇿', callback_data="azn"),
                ],

                [
                InlineKeyboardButton('KZT 🇰🇿', callback_data="kzt"),
                InlineKeyboardButton('UZS 🇺🇿', callback_data="uzs"),
                ],
                [
                InlineKeyboardButton('TMT 🇹🇲', callback_data="tmt"),
                InlineKeyboardButton('KGS 🇰🇬', callback_data="kgs"),
                ],
                [
                InlineKeyboardButton('TJS 🇹🇯', callback_data="tjs"),
                InlineKeyboardButton('RUB 🇷🇺', callback_data="rub")
                ],
                ]

        return InlineKeyboardMarkup(base_keys)

async def menu_keyboard():
        menu_keys = [
                [
                        InlineKeyboardButton("Check Exchange Rates",callback_data="check_exchange")
                ],
                [
                        InlineKeyboardButton("Select Base Currency",callback_data="base_currency"),
                        InlineKeyboardButton("Select Target Currency",callback_data="target_currency")
                ],
                [
                        InlineKeyboardButton("Auto Send Per Day",callback_data="auto_send")
                ]
        ]
        return InlineKeyboardMarkup(menu_keys)
#Data Handeling
async def insert_data(user_id,base_code,target_code):
        conn,cursor = await start_db()
        cursor.execute("insert into users(user_id,base_code,compare_code) values(?,?,?)",(user_id,base_code,target_code,))
        conn.commit()
        conn.close()
async def get_data(user_id):
        conn,cursor = await start_db()
        cursor.execute("select base_code,compare_code,user_id,auto_send from users where user_id = ?",(user_id,))
        datas = cursor.fetchone()
        conn.commit()
        conn.close()
        return datas
async def update_base(user_id,base_code):
        conn,cursor = await start_db()
        cursor.execute("update users set base_code = ? where user_id = ?",(base_code,user_id,))
        conn.commit()
        conn.close()
async def update_target(user_id,target_code):
        conn,cursor = await start_db()
        cursor.execute("update users set compare_code = ? where user_id = ?",(target_code,user_id,))
        conn.commit()
        conn.close()

#Conversation Start
async def base_buttons_handler(update: Update,context: ContextTypes.DEFAULT_TYPE):
        currency_data = await currency()
        query = update.callback_query
        await query.answer()
        if query.data.upper() in currency_data:
                context.user_data['base_code'] = query.data.upper()
                await query.edit_message_text(

"           🪙 Select Target Currency \n",reply_markup = await base_keyboard())
        return 1

async def compare_button_handler(update: Update,context: ContextTypes.DEFAULT_TYPE):
        currency_data = await currency()
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        if query.data.upper() in currency_data:
                context.user_data['compare_code'] = query.data.upper()
                datas = await get_data(user_id)
                if datas is None:
                        await insert_data(user_id,context.user_data['base_code'],context.user_data['compare_code'])
                else:
                        await update_base(user_id,context.user_data['base_code'])
                        await update_target(user_id,context.user_data['compare_code'])
                await query.edit_message_text(f"Base Currency:   {context.user_data['base_code']} ({currency_data[context.user_data['base_code']]['symbol']})\nTarget Currency: {query.data.upper()} ({currency_data[query.data.upper()]['symbol']})",reply_markup = await menu_keyboard())
        return ConversationHandler.END


#Menu Conversation
async def base_currency_handler(update: Update,context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if query.data == "base_currency":
                await query.edit_message_text(
"           🪙 Select Base Currency\n",reply_markup = await base_keyboard())
                return 0
async def base_currency(update: Update,context: ContextTypes.DEFAULT_TYPE):
        currency_data = await currency()
        query = update.callback_query
        await query.answer()
        if query.data.upper() in currency_data:
                context.user_data['base_code'] = query.data.upper()
                await update_base(query.from_user.id,context.user_data['base_code'])
                datas = await get_data(query.from_user.id)
                await query.edit_message_text(f"🔔 Base Currency Changed!\n\nBase Currency:   {datas[0]} ({currency_data[datas[0]]['symbol']})\nTarget Currency: {datas[1]} ({currency_data[datas[1]]['symbol']})",reply_markup=await menu_keyboard())
        return ConversationHandler.END

async def target_currency_handler(update: Update,context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if query.data == "target_currency":
                await query.edit_message_text("           🪙 Select Target Currency\n",reply_markup=await base_keyboard())
                return 0
async def target_currency(update: Update,context: ContextTypes.DEFAULT_TYPE):
        currency_data = await currency()
        query = update.callback_query
        await query.answer()
        if query.data.upper() in currency_data:
                context.user_data['compare_code'] = query.data.upper()
                await update_target(query.from_user.id,query.data.upper())
                datas = await get_data(query.from_user.id)
                await query.edit_message_text(f"🔔 Target Currency Changed!\n\nBase Currency:   {datas[0]} ({currency_data[datas[0]]['symbol']})\nTarget Currency: {datas[1]} ({currency_data[datas[1]]['symbol']})",reply_markup=await menu_keyboard())

        return ConversationHandler.END

#Canceler
async def cancel(update: Update,context: ContextTypes.DEFAULT_TYPE):
        context.user_data.pop('compare_code',None)
        context.user_data.pop('base_code',None)
        await update.message.reply_text("Process is Canceled")
        return ConversationHandler.END

#Start Getting Information
async def check_exchange(base_currency,target_currency):
        currency_data = await currency()
        #m_url = 'https://v6.exchangerate-api.com/v6/072e7034e261aab764cccb8e/latest/'
        m_url = 'https://open.er-api.com/v6/latest/'
        date_time = datetime.datetime.now().strftime("%Y-%m-%d")
        async with aiohttp.ClientSession() as client:
                async with client.get(f"{m_url}{base_currency}") as response:
                        response = await response.json()
                        datas = response['rates']
                        result = f"""
🔔 Daily Exchange Rate Information
📅 Today: {date_time}
💵 {datas[base_currency]} {currency_data[base_currency]['symbol']} = {datas[target_currency]} {currency_data[target_currency]['symbol']} (Official Bank Rate)
"""
                        return result
async def get_information(update: Update,context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if query.data == "check_exchange":
                await query.edit_message_text("Checking Exchange Rate ...",reply_markup=await menu_keyboard())
                datas = await get_data(update.effective_user.id)
                result = await check_exchange(datas[0],datas[1])
                try:
                        await query.edit_message_text(result,reply_markup=await menu_keyboard())
                except telegram.error.BadRequest as e:
                        logger.error(f"Telegram Error BadRequest: {e}")
                        await query.edit_message_text("Checking Exchange Rate ...",reply_markup=await menu_keyboard())
                        datas = await get_data(update.effective_user.id)
                        result = await check_exchange(datas[0],datas[1])
                        await query.edit_message_text(result,reply_markup=await menu_keyboard())

async def auto_sending(context: ContextTypes.DEFAULT_TYPE):
        user_id = context.job.data
        datas = await get_data(user_id)
        result = await check_exchange(datas[0],datas[1])
        await context.bot.send_message(chat_id=user_id,text=result,reply_markup = await menu_keyboard())

async def auto_send_true(user_id):
        conn,cursor = await start_db()
        cursor.execute("update users set auto_send = 'True' where user_id = ?",(user_id,))
        conn.commit()
        conn.close()
async def start_auto_send(update: Update,context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        if query.data == "auto_send":
                await auto_send_true(user_id)
                job_name = f"daily_job_{user_id}"
                target_time = datetime.time(hour=0,minute=0,second=0,tzinfo=mm_tz)
                current_job = context.job_queue.get_jobs_by_name(job_name)
                if current_job:
                        await query.message.reply_text("🔔 The automated messageing system hase been started\n\n[ Don't need to start again! ]")
                        return
                await query.message.reply_text("🔔 The automated messageing system hase been started")
                context.job_queue.run_daily(auto_sending,time=target_time,data=user_id,name=job_name)

#admin section

async def get_all_datas():
        conn,cursor = await start_db()
        cursor.execute("select user_id,auto_send from users")
        datas = cursor.fetchall()
        conn.commit()
        conn.close()
        return datas

async def auto_send(update: Update,context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.id == 5779950798:
                if len(context.args) == 0:
                        datas = await get_all_datas()
                        target_time = datetime.time(hour=0,minute=0,second=0,tzinfo=mm_tz)
                        result = ""
                        no_start_users = []
                        for data in datas:
                                job_name = f"daily_job_{data[0]}"
                                current_job = context.job_queue.get_jobs_by_name(job_name)
                                if current_job:
                                        result += f"-  [<code>{data[0]}</code>] is already started\n"
                                        no_start_users.append(data[0])
                                if data[1] is None:
                                        result += f"-  [<code>{data[0]}</code>] do not click Auto Send Button Yet\n"
                                        no_start_users.append(data[0])
                                if not data[0] in no_start_users and data[1] == "True":
                                        result += f"-  [<code>{data[0]}</code>] is started\n"
                                        context.job_queue.run_daily(auto_sending,time=target_time,data=data[0],name=job_name)
                        await update.message.reply_text(f"My Lord!\nAuto Sending is started for Every Users.\n\nLogs:\n\n{result}",parse_mode=constants.ParseMode.HTML)
                elif len(context.args) == 1:
                        user_id = context.args[0]
                        target_time = datetime.time(hour=0,minute=0,second=0,tzinfo=mm_tz)
                        job_name = f"daily_job_{user_id}"
                        current_job = context.job_queue.get_jobs_by_name(job_name)
                        if current_job:
                                await update.message.reply_text(f"My Lord!\nAuto Sending is Already Started for [<code>{user_id}</code>]",parse_mode = constants.ParseMode.HTML)
                                return
                        context.job_queue.run_daily(auto_sending,time=target_time,data=user_id,name=job_name)
                        await update.message.reply_text(f"My Lord!\nAuto Sending is Started For [<code>{user_id}</code>]",parse_mode = constants.ParseMode.HTML)
                else:
                        await update.message.reply_text(f"[✘] Wrong Command!")
        else:
                await update.message.reply_text("You are Not My Lord! You Can't Use This command")
                return

async def admin(update: Update,context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.id == 5779950798:
                await update.message.reply_text("Here is Your Commands my Lord!\n\n/autosend <user_id or not>  - to start auto send message for users \n/users  - To See Users ID")
        else:
                await update.message.reply_text("You are Not My Lord! You can't use this command")

async def users(update: Update,context:ContextTypes.DEFAULT_TYPE):
        if update.message.chat.id == 5779950798:
                datas = await get_all_datas()
                result = "Users:\n\n"
                for i,data in enumerate(datas,1):
                        result += f"{i}. <code>{data[0]}</code>\n"
                await update.message.reply_text(result,parse_mode = constants.ParseMode.HTML)
        else:
                await update.message.reply_text("You are Not My Lord! You can't use this command")

def main():
        request = HTTPXRequest(read_timeout=60,write_timeout=60)
        bot = Application.builder().token(token).request(request).build()
        start_conversation = ConversationHandler(
                entry_points =[CommandHandler('start',start),CommandHandler('restart',start)],
                states = {
                        0: [CallbackQueryHandler(base_buttons_handler,pattern=r'^(usd|eur|aud|gbp|cny|jpy|krw|hkd|mop|twd|mnt|kpw|mmk|sgd|idr|thb|myr|php|vnd|khr|lak|bnd|usd_tl|irr|inr|pkr|bdt|lkr|npr|afn|mvr|btn|sar|aed|ils|try|qar|kwd|omr|bhd|jod|lbp|ils_ps|syp|yer|iqd|eur_cy|gel|amd|azn|kzt|uzs|tmt|kgs|tjs|rub)$')],
                        1: [CallbackQueryHandler(compare_button_handler,pattern=r'^(usd|eur|aud|gbp|cny|jpy|krw|hkd|mop|twd|mnt|kpw|mmk|sgd|idr|thb|myr|php|vnd|khr|lak|bnd|usd_tl|irr|inr|pkr|bdt|lkr|npr|afn|mvr|btn|sar|aed|ils|try|qar|kwd|omr|bhd|jod|lbp|ils_ps|syp|yer|iqd|eur_cy|gel|amd|azn|kzt|uzs|tmt|kgs|tjs|rub)$')]
                },
                fallbacks = [CommandHandler('cancel',cancel)]
        )
        base_conversation = ConversationHandler(
                entry_points = [CallbackQueryHandler(base_currency_handler,pattern='^base_currency$')],
                states = {
                        0: [CallbackQueryHandler(base_currency)]
                },
                fallbacks = [CommandHandler('cancel',cancel)],
        )
        target_conversation = ConversationHandler(
                entry_points = [CallbackQueryHandler(target_currency_handler,pattern='^target_currency$')],
                states = {
                        0: [CallbackQueryHandler(target_currency)]
                },
                fallbacks = [CommandHandler('cancel',cancel)]
        )
        bot.add_handler(start_conversation)
        bot.add_handler(base_conversation)
        bot.add_handler(target_conversation)
        bot.add_handler(CallbackQueryHandler(get_information,pattern='^check_exchange$'))
        bot.add_handler(CallbackQueryHandler(start_auto_send,pattern="^auto_send$"))
        bot.add_handler(CommandHandler('auto_send',auto_send))
        bot.add_handler(CommandHandler('users',users))
        logger.info("Bot is Running ...")
        bot.run_polling()

if __name__=="__main__":
        main()
