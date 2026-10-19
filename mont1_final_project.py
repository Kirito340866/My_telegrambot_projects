from telegram import Update
from telegram.ext import Application,CommandHandler,ContextTypes
from telegram.request import HTTPXRequest
import sqlite3
import re
import os
token = os.getenv('token')
conn = sqlite3.connect('test.db')
cursor = conn.cursor()
cursor.execute("""
create table if not exists users(
id integer primary key autoincrement,
name varchar(100) not null,
age integer not null,
country varchar(100) not null);
""")
conn.commit()
def start_db():
	conn = sqlite3.connect("test.db")
	cursor = conn.cursor()
	return conn,cursor

usage = "Usage:\n/help : To see Usages\n/register <name> <age> <country>\n/profile <name>\n/update <name> <age> <country>\n/delete <name>\n/users : To see users\n\n"
async def start(update: Update,context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(f"Hello, {update.message.chat.first_name}\nWelcome from my first project!\n\n{usage}")
async def help(update: Update,context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(f"======[ Help ]======\n\n{usage}")
async def register(update: Update,context: ContextTypes.DEFAULT_TYPE):
	if not context.args or len(context.args) < 3:
		await update.message.reply_text("[✘] Arguments Not Found!\n\nUsage:\n/register <name> <age> <country>\n")
		return
	try:
		age = int(context.args[1])
	except ValueError:
		await update.message.reply_text("[✘] Age must be integer")
		return
	country = " ".join(context.args[2:])
	name = context.args[0]
	if not name[-1].isdigit() or not re.match(r"\b[a-zA-Z]",name):
		await update.message.reply_text("[✘] User name must start with letter and end with digit (E.g: kirito340866)")
		return
	conn,cursor = start_db()
	cursor.execute("insert into users(name,age,country) values(?,?,?)",(context.args[0],age,country,))
	conn.commit()
	conn.close()
	await update.message.reply_text("[✓] Registered Successfully!")
async def profile(update: Update,context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("[✘] Argument Not Found!\n\nUsage:\n/profile <name>\n")
		return
	if len(context.args) > 1:
		await update.message.reply_text("[✘] Too Many Argument!\n\nUsage:\n/profile <name>\n")
		return
	name = context.args[0]
	if not name[-1].isdigit() or not re.match(r"\b[a-zA-Z]",name):
		await update.message.reply_text("[✘] User name must start with letter and end with digit (E.g: kirito340866)")
		return
	conn,cursor = start_db()
	cursor.execute("select * from users where name = ?",(name,))
	user = cursor.fetchone()
	if user is None:
		conn.close()
		await update.message.reply_text("[✘] User Not Found!")
		return
	await update.message.reply_text(f"User Profile:\n\nID: {user[0]}\nName: {user[1]}\nAge: {user[2]}\nCountry: {user[3]}")
	conn.close()
async def update(update: Update,context: ContextTypes.DEFAULT_TYPE):
	if not context.args or len(context.args) < 3:
		await update.message.reply_text("[✘] Argument Not Found!\n\nUsage:\n/update <name> <age> <country>\n")
		return
	try:
		age = int(context.args[1])
	except ValueError:
		await update.message.reply_text("[✘] Age must be integer")
		return
	name = context.args[0]
	if not name[-1].isdigit() or not re.match(r"\b[a-zA-Z]",name):
		await update.message.reply_text("[✘] User name must start with letter and end with digit (E.g: kirito340866)")
		return
	country = " ".join(context.args[2:])
	conn,cursor = start_db()
	cursor.execute("select * from users where name = ?",(name,))
	user = cursor.fetchone()
	if user is None:
		conn.close()
		await update.message.reply_text("[✘] User Not Found!")
		return
	cursor.execute("update users set age = ?,country = ? where name = ?",(age,country,name,))
	conn.commit()
	conn.close()
	await update.message.reply_text("[✓] Updated Successfully!")
async def delete(update: Update,context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("[✘] Argument Not Found\n\nUsage:\n/delete <name>\n")
		return
	if len(context.args) > 1:
		await update.message.reply_text("[✘] Too Many Arguments\n\nUsage:\n/delete <name>\n")
		return
	name = context.args[0]
	if not name[-1].isdigit() or not re.match(r"\b[a-zA-Z]",name):
		await update.message.reply_text("[✘] User name must start with letter and end with digit (E.g: kirito340866)")
		return
	conn,cursor = start_db()
	cursor.execute("select * from users where name=?",(name,))
	user = cursor.fetchone()
	if user is None:
		conn.close()
		await update.message.reply_text("[✘] User Not Found!")
		return
	cursor.execute("delete from users where name=?",(name,))
	conn.commit()
	conn.close()
	await update.message.reply_text("[✓] Deleted Successfully!")
async def users(update: Update,context: ContextTypes.DEFAULT_TYPE):
	usrs = ""
	conn,cursor = start_db()
	cursor.execute("select * from users")
	user = cursor.fetchall()
	for i,ur in enumerate(user,1):
		usrs += f"{i}. {ur[1]}\n"
	await update.message.reply_text(f"====[ USERS ]====\n\n{usrs}")
	conn.close()
def main():
	request = HTTPXRequest(read_timeout=60,write_timeout=60)
	app = Application.builder().token(token).request(request).build()
	app.add_handler(CommandHandler('start',start))
	app.add_handler(CommandHandler('help',help))
	app.add_handler(CommandHandler('register',register))
	app.add_handler(CommandHandler('profile',profile))
	app.add_handler(CommandHandler('update',update))
	app.add_handler(CommandHandler('delete',delete))
	app.add_handler(CommandHandler('users',users))
	print('Bot is running ...')
	app.run_polling()
if __name__=="__main__":
	main()
