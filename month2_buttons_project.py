from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,CommandHandler,ContextTypes,CallbackQueryHandler
from telegram.request import HTTPXRequest
import sqlite3
import re
import random
from concurrent.futures import ThreadPoolExecutor
conn = sqlite3.connect("test.db")
cursor = conn.cursor()
cursor.execute("""
create table if not exists Users(
id integer primary key autoincrement,
user_name varchar(100),
name varchar(100) not null,
password integer not null);
""")
conn.commit()
tools = InlineKeyboardButton(text="Tools",callback_data="tools")
profile = InlineKeyboardButton(text="Profile",callback_data="profile")
calculator = InlineKeyboardButton(text="Calculator",callback_data="calculator")
random_n = InlineKeyboardButton(text="Random",callback_data="random")
help = InlineKeyboardButton(text="Help",callback_data="help")
user_back = InlineKeyboardButton(text="Back to Menu",callback_data="user_back")
user_back_key = [[user_back]]
back_to_user = InlineKeyboardMarkup(user_back_key)
menu = [[profile,tools],[help]]
tool_keyboard = [[calculator,random_n],[user_back]]
tool_menu = InlineKeyboardMarkup(tool_keyboard)
menu_markup = InlineKeyboardMarkup(menu)
calculation = {}
import os
token = os.getenv('token')
def start_db():
	conn = sqlite3.connect('test.db')
	cursor = conn.cursor()
	return conn,cursor
async def start(update: Update,context: ContextTypes.DEFAULT_TYPE):
	calculation[update.message.chat.username] = ""
	login = InlineKeyboardButton(text="Login",callback_data="login")
	register = InlineKeyboardButton(text="Register",callback_data="register")
	keyboard = [[login,register],[help]]
	verify_user = InlineKeyboardMarkup(keyboard)
	await update.message.reply_text(f"Hello, {update.message.chat.first_name}\n",reply_markup=verify_user)
async def button_manager(update: Update,context: ContextTyptes.DEFAULT_TYPE):
	login = InlineKeyboardButton(text="Login",callback_data="login")
	register = InlineKeyboardButton(text="Register",callback_data="register")
	user_info_keyboard = [[login,register]]
	verify_user = InlineKeyboardMarkup(user_info_keyboard)
	back = InlineKeyboardButton(text="Back to Menu",callback_data="back")
	user_back = InlineKeyboardButton(text="Back to Menu",callback_data="user_back")
	user_back_key = [[user_back]]
	back_to_user = InlineKeyboardMarkup(user_back_key)
	back_keyboard = [[back]]
	back_to = InlineKeyboardMarkup(back_keyboard)
	query = update.callback_query
	#for calculator
	n1 = InlineKeyboardButton(text="1",callback_data="1")
	n2 = InlineKeyboardButton(text="2",callback_data="2")
	n3 = InlineKeyboardButton(text="3",callback_data="3")
	n4 = InlineKeyboardButton(text="4",callback_data="4")
	n5 = InlineKeyboardButton(text="5",callback_data="5")
	n6 = InlineKeyboardButton(text="6",callback_data="6")
	n7 = InlineKeyboardButton(text="7",callback_data="7")
	n8 = InlineKeyboardButton(text="8",callback_data="8")
	n9 = InlineKeyboardButton(text="9",callback_data="9")
	n0 = InlineKeyboardButton(text="0",callback_data="0")
	op_p = InlineKeyboardButton(text="+",callback_data="+")
	op_m = InlineKeyboardButton(text="-",callback_data="-")
	op_mul = InlineKeyboardButton(text="x",callback_data="*")
	op_d = InlineKeyboardButton(text="/",callback_data="/")
	op_re = InlineKeyboardButton(text="=",callback_data="=")
	cal_keyboard = [[n1,n2,n3,op_d],[n4,n5,n6,op_p],[n7,n8,n9,op_m],[op_p,n0,op_mul,op_re],[user_back]]
	calculation_keyboard = InlineKeyboardMarkup(cal_keyboard)
	await query.answer()
	if query.data == "login":
		await query.edit_message_text("Use:\n/login <name> <password> To Login",reply_markup=back_to)
	elif query.data == "register":
		await query.edit_message_text("Use:\n/register <name> <password> For Register\n",reply_markup=back_to)
	elif query.data == "back":
		login = InlineKeyboardButton(text="Login",callback_data="login")
		register = InlineKeyboardButton(text="Register",callback_data="register")
		keyboard = [[login,register]]
		verify_user = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"Hello, {query.message.chat.first_name}",reply_markup=verify_user)
	elif query.data == "user_back":
		await query.edit_message_text(f"Hello, {query.message.chat.first_name}\n",reply_markup=menu_markup)
	elif query.data == "profile":
		conn,cursor = start_db()
		cursor.execute("select * from users where user_name=?",(query.message.chat.username,))
		user = cursor.fetchone()
		if user is None:
			conn.close()
			await query.edit_message_text("[✘] You Need to (Login) or (Sign Up) Firstly!",reply_markup=verify_user)
			return
		await query.edit_message_text(f"[+] Profile:\n\nID: {user[0]}\nUser name: {user[2]}\nTelegram User Name: {user[1]}\n",reply_markup=back_to_user)
		conn.close()
	elif query.data == "calculator":
		await query.edit_message_text("My Calculator:\n\n",reply_markup=calculation_keyboard)
	user_name = query.message.chat.username
	if query.data == "1":
		calculation[user_name] += "1"
	if query.data == "2":
		calculation[user_name] += "2"
	if query.data == "3":
		calculation[user_name] += "3"
	if query.data == "4":
		calculation[user_name] += "4"
	if query.data == "5":
		calculation[user_name] += "5"
	if query.data == "6":
		calculation[user_name] += "6"
	if query.data == "7":
		calculation[user_name] += "7"
	if query.data == "8":
		calculation[user_name] += "8"
	if query.data == "9":
		calculation[user_name] += "9"
	if query.data == "0":
		calculation[user_name] += "0"
	if query.data == "+":
		calculation[user_name] += "+"
	if query.data == "-":
		calculation[user_name] += "-"
	if query.data == "*":
		calculation[user_name] += "*"
	if query.data == "/":
		calculation[user_name] += "/"
	if query.data == "=":
		if "+" in calculation[user_name]:
			calculate = calculation[user_name].split("+")
			try:
				first = int(calculate[0])
				second = int(calculate[1])
			except ValueError:
				await query.message.reply_text("[✘] There Shouldn't Be letters!")
				return
			await query.message.reply_text(f"{first} + {second} = {first+second}")
			calculation[user_name]=""
		elif "-" in calculation[user_name]:
			calculate = calculation[user_name].split("-")
			try:
				first = int(calculate[0])
				second = int(calculate[1])
			except ValueError:
				await query.message.reply_text("[✘] There Shouldn't Be letters!")
				return
			await query.message.reply_text(f"{first} - {second} = {first - second}")
			calculation[user_name] = ""
		elif "*" in calculation[user_name]:
			calculate = calculation[user_name].split("*")
			try:
				first = int(calculate[0])
				second = int(calculate[1])
			except ValueError:
				await query.message.reply_text("[✘] There Shouldn't Be letters!")
				return
			await query.message.reply_text(f"{first} x {second} = {first * second}")
			calculation[user_name] = ""
		elif "/" in calculation[user_name]:
			calculate = calculation[user_name].split("/")
			try:
				first = int(calculate[0])
				second = int(calculate[1])
			except ValueError:
				await query.message.reply_text("[✘] There Shouldn't Be letters!")
				return
			if second == 0:
				await query.message.reply_text("[✘] Zero Division Error!")
				return
			await query.message.reply_text(f"{first} / {second} = {first / second}")
			calculation[user_name] = ""
	if query.data == "random":
		random_number = random.randint(1,100)
		await query.message.reply_text(f"Random Number: {random_number}")
	elif query.data == "help":
		await query.edit_message_text(f"Help Menu:\n\n/login <name> <password>\n/register <name> <password>\n",reply_markup=back_to_user)
	elif query.data == "tools":
		calculation[user_name] = ""
		await query.edit_message_text(f"====[ Tools ]====\n",reply_markup=tool_menu)

async def register(update: Update,context: ContextTypes.DEFAULT_TYPE):
		if not context.args or len(context.args) < 2:
			await update.message.reply_text("[✘] Argument Not Found!\nThere must be 2 arguments\n")
			return
		if len(context.args) > 2:
			await update.message.reply_text("[✘] Too Many Arguments!\nThere must be 2 arguments\n")
			return
		name = context.args[0]
		passwords = context.args[1]
		letter_contain = False
		integer_contain = False
		if not re.match(r"\b[a-zA-Z]",name) or not name[-1].isdigit():
			await update.message.reply_text("[✘] Invalid User name\nUser name must start with letter and end with digit\n")
			return
		for password in passwords:
			try:
				inte = int(password)
				integer_contain = True
			except ValueError:
				letter_contain = True
		if len(passwords) < 8 or not letter_contain or not integer_contain:
			await update.message.reply_text("[✘] Invalid Password\n\n- Password length must be at least 8\n- Password must contain letter\n- Password must contain number\n")
			return
		conn,cursor = start_db()
		cursor.execute("select * from users where name=?",(name,))
		name_from_db = cursor.fetchone()
		if name_from_db is not None:
			conn.close()
			await update.message.reply_text("[✘] This user account is Already Exists!\n\nUse Another User Name!")
			return
		cursor.execute("insert into users (user_name,name,password) values(?,?,?);",(update.message.chat.username,name,passwords,))
		conn.commit()
		conn.close()
		calculation[update.message.chat.username] = ""
		await update.message.reply_text("[✔] Register Successfully!",reply_markup=menu_markup)
async def login(update: Update,context: ContextTypes.DEFAULT_TYPE):
	calculation[update.message.chat.username] = ""
	if not context.args or len(context.args) < 2:
		await update.message.reply_text("[✘] Argument Not Found!\nThere must be at least 2 Arguments\n\nUsage: /login <name> <password>")
		return
	if len(context.args) > 2:
		await update.message.reply_text("[✘] Too Many Arguments!\n\nUsage: /login <name> <password>")
		return
	conn,cursor = start_db()
	cursor.execute("select * from users where name=? and password=? and user_name = ?",(context.args[0],context.args[1],update.message.chat.username,))
	user_info = cursor.fetchone()
	if user_info is None:
		conn.close()
		await update.message.reply_text("[✘] Invalid User Name or Password!")
		return
	await update.message.reply_text("[✓] Login Successfull!",reply_markup=menu_markup)
def main():
	request = HTTPXRequest(read_timeout=60,write_timeout=60)
	app = Application.builder().token(token).request(request).build()
	app.add_handler(CommandHandler('start',start))
	app.add_handler(CallbackQueryHandler(button_manager))
	app.add_handler(CommandHandler('register',register))
	app.add_handler(CommandHandler('login',login))
	print('Bot is running ...')
	app.run_polling()

if __name__=="__main__":
	main()
