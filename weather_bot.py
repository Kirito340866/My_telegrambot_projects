from telegram import Update
from telegram.ext import Application,CommandHandler,ContextTypes
import os
import logging
import httpx
token = os.getenv('token')
logging.basicConfig(
	format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	level = logging.INFO
)
logger = logging.getLogger(__name__)
location_url = "https://geocoding-api.open-meteo.com/v1/search"
weather_url = "https://api.open-meteo.com/v1/forecast"
async def start(update: Update,context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(f"Hello, {update.message.chat.first_name}\nWelcome from My Weather bot!\n\nUsage:\n/weather <city_name>")

async def weather(update: Update,context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("[✘] Argument Not Found\n\nUsage:\n/weather <city_name>")
		return
	city = " ".join(context.args[0:])
	if city.isdigit():
		await update.message.reply_text("[✘] City Must be String")
		return
	try:
		datas = await get_weather(city)
	except httpx.HTTPStatusError as e:
		logger.error(f"Http Error: {e}")
		await update.message.reply_text("[✘] API Error!\nPlease Try again later")
		return
	except httpx.RequestError as e:
		logger.error(f"Network or Request Error: {e}")
		await update.message.reply_text("[✘] API Error!\nPlease Try again later")
		return
	except ValueError as e:
		logger.error(f"[-] ValueError: {e}")
		await update.message.reply_text("[✘] Value Error!\nPlease Try again")
		return
		
	if datas is None:
		await update.message.reply_text(f"{city} Is Not Found")
		return

	result = f"""
City: {datas['city']}
Country: {datas['country']}
Temperature: {datas['temperature']} °C
Actual Feel Temperature: {datas['feel_like_tem']} °C
Humidity: {datas['humidity']} %
Wind Speed: {datas['wind_speed']} km/h

Weather Condition: {datas['condition']}
Time: {datas['time']}

"""
	await update.message.reply_text(result)

async def get_weather(city: str):
	location_params = {
		'name': city,
		'count': 1,
		'language':'en',
		'format': 'json'
	}
	async with httpx.AsyncClient(timeout=10) as client:
		response = await client.get(location_url,params = location_params)
		response.raise_for_status()
		response_data = response.json()
		location_data = response_data.get('results',[])
		if not location_data:
			return None
		location = location_data[0]
		latitude = location['latitude']
		longitude = location['longitude']
		city_name = location['name']
		country = location['country']
		weather_params = {
			'latitude':latitude,
			'longitude':longitude,
			'current': (
				'temperature_2m,'
				'relative_humidity_2m,'
				'apparent_temperature,'
				'weather_code,'
				'wind_speed_10m'),
			'timezone':'auto'}
		weather_response = await client.get(weather_url,params = weather_params)
		weather_response.raise_for_status()
		weather_response = weather_response.json()
		current = weather_response['current']
		data = {
			'city': city_name,
			'country': country,
			'temperature': current['temperature_2m'],
			'feel_like_tem': current['apparent_temperature'],
			'humidity': current['relative_humidity_2m'],
			'wind_speed': current['wind_speed_10m'],
			'condition': weather_condition(current['weather_code']),
			'time': current['time']}

		return data

def weather_condition(code):
	conditions = {
	"0": "Clear sky",
	"1": "Mainly clear",
	"2": "Partly cloudy",
	"3": "Overcast",
	"45": "Fog",
	"48": "Depositing rime fog",
	"51": "Light drizzle",
	"53": "Moderate drizzle",
	"55": "Dense drizzle",
	"56": "Light freezing drizzle",
	"57": "Dense freezing drizzle",
	"61": "Slight rain",
	"63": "Moderate rain",
	"65": "Heavy rain",
	"66": "Light freezing rain",
	"67": "Heavy freezing rain",
	"71": "Slight snowfall",
	"73": "Moderate snowfall",
	"75": "Heavy snowfall",
	"77": "Snow grains",
	"80": "Slight rain showers",
	"81": "Moderate rain showers",
	"82": "Violent rain showers",
	"85": "Slight snow showers",
	"86": "Heavy snow showers",
	"95": "Thunderstorm",
	"96": "Thunderstorm with slight hail",
	"97": "Heavy thunderstorm",
	"99": "Thunderstorm with heavy hail"
}
	code = str(code)
	if not code in conditions.keys():
		return "[✘] Unknown Weather Condition"
	return conditions[code]

def main():
	if not token:
		print("[-] Token Not Found")
		return
	app = Application.builder().token(token).concurrent_updates(10).build()
	app.add_handler(CommandHandler('start',start))
	app.add_handler(CommandHandler('weather',weather))
	logger.info("Bot is Running ... ")
	app.run_polling()

if __name__=="__main__":
	main()
