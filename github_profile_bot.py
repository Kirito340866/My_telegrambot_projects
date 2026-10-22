from telegram import Update
from telegram.ext import Application,CommandHandler,ContextTypes
from telegram.request import HTTPXRequest
import os
import httpx
import logging
token = os.getenv('token')
logging.basicConfig(
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	level = logging.INFO
)
logger = logging.getLogger(__name__)
url = "https://api.github.com/users/"

async def start(update: Update,context: ContextTypes.DEFAULT_TYPE):
	await update.effective_message.reply_text(f"Hello, {update.effective_user.first_name}\n\nUsage:\n/github <user_name>")

async def github(update: Update,context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.effective_message.reply_text("[✘] Argument Not Found\n\nUsage:\n/github <user_name>")
		return
	if len(context.args) != 1:
		await update.effective_message.reply_text("[✘] Please Enter Only User name\n\nUsage:\n/github <user_name>")
		return
	user_name = context.args[0]
	if not user_name or len(user_name) > 39:
		await update.effective_message.reply_text("[✘] Invalid User Name")
		return
	await update.effective_message.reply_text("Finding Gighub Profile ...")
	try:
		async with httpx.AsyncClient(timeout=10) as client:
			response = await client.get(f"{url}{user_name}")
			if response.status_code == 404:
				await update.effective_message.reply_text("[✘] User Not Found")
				return
			response.raise_for_status()
			data = response.json()
			name = data['name'] or data['login']
			u_name = data['login']
			bio = data['bio'] or "Not Found"
			p_repo = data['public_repos']
			followers = data['followers']
			profile = data['html_url']
			repo_url = data['repos_url']
			result = f"""
Name: {name}
User name: {u_name}
Bio: {bio}
Public Repos: {p_repo}
Followers: {followers}

Profile: {profile}
Repos: {repo_url}
"""
			await update.effective_message.reply_text(result)

	except httpx.HTTPStatusError as e:
		logger.warning("Github API request HTTP Error: %s",e.response.status_code)
		await update.effective_message.reply_text("[✘] API Problem at github")
	except httpx.TimeoutException as t:
		await update.effective_message.reply_text("[✘] Github API Does no response in time\nTry Again!")
	except httpx.RequestError:
		logger.excception("Github API connection Failed")
		await update.effective_message.reply_text("[✘] Can't Connect to API. Check you network connection")
	except ValueError:
		logger.exception("Github API returned invalid JSON")
		await update.effective_message.reply_text("[✘] Cannot read to Api resposne")

def main():
	cus_request = HTTPXRequest(read_timeout=60,write_timeout=60)
	bot = Application.builder().token(token).request(cus_request).build()
	bot.add_handler(CommandHandler("start",start))
	bot.add_handler(CommandHandler("github",github))
	logger.info("Bot is Running ...")
	bot.run_polling()

if __name__=="__main__":
	main()
