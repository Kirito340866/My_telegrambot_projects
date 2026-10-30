import aiohttp
import logging
import asyncio
from telegram import Update,constants
from telegram.ext import Application,CommandHandler,ContextTypes,ConversationHandler,CallbackQueryHandler,MessageHandler,filters
from telegram.request import HTTPXRequest
import os

token = os.getenv('token')

url = 'https://api.ipgeolocation.io/v3/ipgeo?apiKey=#your api key from (https://ipgeolocation.io)'
logging.basicConfig(
	format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	level = logging.INFO
)
logger = logging.getLogger(__name__)


# ===========[ getting ip information ]============
async def get_info_of_ip(ip):
	async with aiohttp.ClientSession() as client:
		async with client.get(f"{url}&ip={ip}") as response:
			response = await response.json()
			if 'message' in response and response['message'] == f"Provided name, service or IP address '{ip}' is not valid.":
				return f"Provided name, service or IP address '{ip}' is not valid."
			if 'message' in response and response['message'] == f"'{ip}' is a bogon IP address.":
				return f"'{ip}' is a bogon IP address."
			location = response['location']
			currency = response['currency']
			country_metadata = response['country_metadata']
			time_zone = response['time_zone']
			#informations
			#location
			continent = location['continent_name']
			continent_code = location['continent_code']
			country = f"{location['country_name']} {location['country_emoji']}"
			country_codes = f"{location['country_code2']}, {location['country_code3']}"
			city = location['city']
			zipcode = location['zipcode']
			latitude = location['latitude']
			longitude = location['longitude']
			google_map_url = f"https://maps.google.com/maps?ll={latitude},{longitude}"

			#country_metadata
			calling_code = country_metadata['calling_code']
			tld = country_metadata['tld']
			languages = ""
			for language in country_metadata['languages']:
				if country_metadata['languages'].index(language) == len(country_metadata['languages']) - 1:
					languages += f"{language}"
				else:
					languages += f"{language},"

			#currency
			money_code = currency['code']
			money_name = currency['name']
			money_symbol = currency['symbol']

			#time_zone
			t_zone = time_zone['name']
			c_time = time_zone['current_time']

			result = f"""
Location:

Continent: <code>{continent}</code>
Continent Code: <code>{continent_code}</code>
Country: <code>{country}</code>
Country Codes: <code>{country_codes}</code>
City: <code>{city}</code>
Zip Code: <code>{zipcode}</code>

Latitude: <code>{latitude}</code>
Longitude: <code>{longitude}</code>
Google Map: {google_map_url}

================================

Counry Metadata:

Calling Code: <code>{calling_code}</code>
Top-Level Domain: <code>{tld}</code>
Languages: <code>{languages}</code>

=================================

Currency:

Code: <code>{money_code}</code>
Name: <code>{money_name}</code>
Symbol: <code>{money_symbol}</code>

=================================
Time Zone:

Time Zone: <code>{t_zone}</code>
Current Time: <code>{c_time}</code>

"""
			return result


#start_command
async def start(update: Update,context: ContextTypes.DEFAULT_TYPE):
		await update.message.reply_text(f"""
=========================
             DOH Ip Tracker
=========================

Usage:

1. Just send me The Ip You Want To track


""")


#=============[ Start Ip Tracking ]==============
async def get_ip(update: Update,context: ContextTypes.DEFAULT_TYPE):
		ip = update.message.text
		await update.message.reply_text("Searching Ip Information ...")
		result = await get_info_of_ip(ip)
		await update.message.reply_text(result,parse_mode=constants.ParseMode.HTML)
		return ConversationHandler.END


def main():
	request = HTTPXRequest(read_timeout=60,write_timeout=60)
	bot = Application.builder().token(token).request(request).build()
	bot.add_handler(CommandHandler('start',start))
	bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,get_ip))
	logger.info("Bot is Running ...")
	bot.run_polling()
if __name__=="__main__":
	main()
