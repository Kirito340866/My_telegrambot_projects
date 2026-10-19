from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes,CallbackQueryHandler,ConversationHandler
from telegram.request import HTTPXRequest
import logging
import os
import asyncio
import sqlite3
logging.basicConfig(
	format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	level = logging.INFO
)
token = os.getenv('token')
logger = logging.getLogger(__name__)
def start_db():
	conn = sqlite3.connect("notes.db")
	cursor = conn.cursor()
	return conn,cursor

conn,cursor = start_db()
cursor.execute("""
create table if not exists user_tasks(
id integer primary key autoincrement,
chat_id integer not null,
content text not null,
is_check varchar(100));
""")
conn.commit()
conn.close()
#buttons

add_task = InlineKeyboardButton(text="Add Task",callback_data="add_task")
tasks = InlineKeyboardButton(text="My Tasks",callback_data="tasks")
done = InlineKeyboardButton(text="Check Tasks",callback_data="done")
edit_task = InlineKeyboardButton(text="Edit Task",callback_data="edit_task")
del_task = InlineKeyboardButton(text="Delete Task",callback_data="del_task")
del_all_task = InlineKeyboardButton(text="Delete All Task",callback_data="del_all")
help = InlineKeyboardButton(text="Help",callback_data="help")
back = InlineKeyboardButton(text="Back To Menu",callback_data="back")
menu_keyboard = [[add_task,tasks],[done,edit_task],[del_task,del_all_task],[help]]
menu_markup = InlineKeyboardMarkup(menu_keyboard)
back_key = [[back]]
back_markup = InlineKeyboardMarkup(back_key)

def add_task(chat_id,content):
	conn,cursor = start_db()
	cursor.execute("insert into user_tasks (chat_id,content,is_check) values(?,?,?)",(chat_id,content,'✘',))
	conn.commit()
	conn.close()

def tasks(chat_id):
	conn,cursor = start_db()
	cursor.execute("select id,content,is_check from user_tasks where chat_id = ?",(chat_id,))
	my_tasks = cursor.fetchall()
	if not my_tasks:
		conn.close()
		return "[✘] You don't Have Tasks"
	result = ""
	for task in my_tasks:
		result += f"ID: {task[0]} | [{task[2]}] {task[1]}\n"
	conn.close()
	return result

def done(chat_id,id):
	conn,cursor = start_db()
	cursor.execute("select id,content,is_check from user_tasks where chat_id = ? AND id = ?", (chat_id, id))
	task = cursor.fetchone()
	if task is None:
		conn.close()
		return "[✘] You Don't have task with this ID"
	cursor.execute("update user_tasks set is_check = '✓' where id = ? AND chat_id = ?",(id,chat_id))
	cursor.execute("select id,content,is_check from user_tasks where chat_id = ? AND id = ?", (chat_id, id))
	task = cursor.fetchone()
	conn.commit()
	conn.close()
	return f"ID: {task[0]} | [{task[2]}] {task[1]}"

def edit_task(chat_id,id,content):
	conn,cursor = start_db()
	cursor.execute("select * from user_tasks where id = ? and chat_id = ?",(id,chat_id,))
	task = cursor.fetchone()
	if task is None:
		conn.close()
		return "[✘] You don't have task with this id!"
	cursor.execute("update user_tasks set content = ?, is_check = '✘' where chat_id = ? and id = ?",(content,chat_id,id,))
	cursor.execute("select	id,content,is_check from user_tasks where id = ? and chat_id = ?",(id,chat_id,))
	result_task = cursor.fetchone()
	result = f"[✓] Updated Successfully!\n\nID: {result_task[0]} | [{result_task[2]}] {result_task[1]}"
	conn.commit()
	conn.close()
	return result
def del_task(chat_id,id):
	conn,cursor = start_db()
	cursor.execute("select * from user_tasks where chat_id = ? and id = ?",(chat_id,id,))
	task = cursor.fetchone()
	if task is None:
		conn.close()
		return "[✘] You don't have Task with this ID"
	cursor.execute("delete from user_tasks where chat_id = ? and id = ?",(chat_id,id,))
	result = "[✓] Task is Deleted Successfully!"
	conn.commit()
	conn.close()
	return result

#add_task
async def start_add_task(update: Update,context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query
	await query.answer()
	if query.data == "add_task":
		await query.message.reply_text("Send Me the Task")
		return 0

async def get_task(update: Update,context: ContextTypes.DEFAULT_TYPE):
	content = update.message.text
	await asyncio.to_thread(add_task,update.effective_user.id,content)
	await update.message.reply_text("[✓] Task Added Successfully!",reply_markup=menu_markup)
	return ConversationHandler.END

#show_tasks and handle other buttons
async def start_show_tasks(update: Update,context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query
	await query.answer()
	if query.data == 'tasks':
		result = await asyncio.to_thread(tasks,query.from_user.id)
		await query.edit_message_text(result,reply_markup=back_markup)
	elif query.data == "back":
		await query.edit_message_text(f"Hello, {query.message.chat.first_name}\nWelcome To My [Personal Task Manager bot]\n",reply_markup=menu_markup)
	elif query.data == "del_all":
		yes = InlineKeyboardButton(text="Yes",callback_data="yes")
		no = InlineKeyboardButton(text="No",callback_data="no")
		yes_no = [[yes,no]]
		result = await asyncio.to_thread(tasks,query.from_user.id)
		if result == "[✘] You don't Have Tasks":
			await query.edit_message_text("[✘] You don't Have Tasks",reply_markup=back_markup)
			return
		verify_markup = InlineKeyboardMarkup(yes_no)
		await query.edit_message_text("Are You Sure you want to Deleted All Tasks?",reply_markup=verify_markup)
	elif query.data == "yes":
		conn,cursor = start_db()
		cursor.execute("delete from user_tasks where chat_id = ?",(query.from_user.id,))
		conn.commit()
		conn.close()
		await query.edit_message_text("[✓] All of your tasks are deleted successfully",reply_markup=menu_markup)
	elif query.data == "no":
		await query.edit_message_text("[✓] Process is Canceled",reply_markup=menu_markup)
	elif query.data == "help":
		help_message = """
Help Menu:

[Add Task] Button            - To Add Tasks
[My Tasks] Button            - To see all of your tasks
[Delete Tasks] Button        - To delete tasks by id
[Delete All Tasks] Button    - To delete all tasks
[Check Tasks] Button         - To set the tasks as done
[Edit Task] Button           - To edit the existed task
[Help] Button                - To see Help Menu
"""
		await query.edit_message_text(help_message,reply_markup=back_markup)


#checking_task
async def start_checking_task(update: Update,context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query
	await query.answer()
	if query.data == "done":
		result = await asyncio.to_thread(tasks,query.from_user.id)
		if result == "[✘] You don't Have Tasks":
			await query.edit_message_text("[✘] You don't Have Tasks",reply_markup=back_markup)
			return
		await query.message.reply_text(f"Send me the ID of the task!\n\n{result}")
		return 0
async def get_check_task(update: Update,context: ContextTypes.DEFAULT_TYPE):
	id = update.message.text
	try:
		id = int(id)
	except ValueError:
		await update.message.reply_text("[✘] Id must be number!")
		return 0
	result = await asyncio.to_thread(done,update.effective_user.id,id)
	await update.message.reply_text(result,reply_markup=menu_markup)
	return ConversationHandler.END

#Edit_task
async def start_editing_task(update: Update,context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query
	await query.answer()
	if query.data == "edit_task":
		result = await asyncio.to_thread(tasks,query.from_user.id)
		if result == "[✘] You don't Have Tasks":
			await query.edit_message_text("[✘] You don't Have Tasks",reply_markup=back_markup)
			return
		await query.message.reply_text(f"Send me the ID of the task!\n\n{result}",)
		return 0
async def get_edit_id(update: Update,context: ContextTypes.DEFAULT_TYPE):
	id = update.message.text
	try:
		id = int(id)
	except ValueError:
		await update.message.reply_text("[✘] ID must be number!")
		return 0
	context.user_data['id'] = id
	await update.message.reply_text("Send me the New Task!")
	return 1

async def get_edit_task(update: Update,context: ContextTypes.DEFAULT_TYPE):
	content = update.message.text
	id = context.user_data['id']
	result = await asyncio.to_thread(edit_task,update.effective_user.id,id,content)
	await update.message.reply_text(result,reply_markup=menu_markup)
	return ConversationHandler.END


#deleting_task
async def start_deleting_task(update: Update,context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query
	await query.answer()
	if query.data == "del_task":
		result = await asyncio.to_thread(tasks,query.from_user.id)
		if result == "[✘] You don't Have Tasks":
			await query.edit_message_text("[✘] You Have No Tasks Yet",reply_markup=back_markup)
			return
		await query.message.reply_text(f"Send me the ID of the task!\n\n{result}")
		return 0
async def get_del_id(update: Update,context: ContextTypes.DEFAULT_TYPE):
	id = update.message.text
	try:
		id = int(id)
	except ValueError:
		await update.message.reply_text("[✘] ID must be number!")
		return 0
	result = await asyncio.to_thread(del_task,update.effective_user.id,id)
	await update.message.reply_text(result,reply_markup=menu_markup)
	return ConversationHandler.END


#cancel
async def cancel(update: Update,context: ContextTypes.DEFAULT_TYPE):
	context.user_data.pop('id',None)
	await update.message.reply_text("[✓] Process is Canceled")
	return ConversationHandler.END

#start
async def start(update: Update,context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(f"Hello, {update.message.chat.first_name}\nWelcome To My [Personal Task Manager bot]\n",reply_markup=menu_markup)

def main():
	if not token:
		print("[✘] Token Not Found")
		return
	request = HTTPXRequest(read_timeout=60,write_timeout=60)
	app = Application.builder().token(token).request(request).build()
	app.add_handler(CommandHandler('start',start))
	add_task_conversation = ConversationHandler(
		entry_points = [CallbackQueryHandler(start_add_task,pattern='add_task')],
		states = {
			0: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_task)]
		},
		fallbacks = [CommandHandler('cancel',cancel)]
	)
	check_task_conversation = ConversationHandler(
		entry_points = [CallbackQueryHandler(start_checking_task,pattern='done')],
		states = {
			0: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_check_task)]
		},
		fallbacks = [CommandHandler('cancel',cancel)],
	)
	edit_task_conversation = ConversationHandler(
		entry_points = [CallbackQueryHandler(start_editing_task,pattern='edit_task')],
		states = {
			0: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_edit_id)],
			1: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_edit_task)]
		},
		fallbacks = [CommandHandler('cancel',cancel)]
	)
	del_task_conversation = ConversationHandler(
		entry_points = [CallbackQueryHandler(start_deleting_task,pattern='del_task')],
		states = {
			0: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_del_id)]
		},
		fallbacks = [CommandHandler('cancel',cancel)]
	)
	app.add_handler(del_task_conversation)
	app.add_handler(edit_task_conversation)
	app.add_handler(check_task_conversation)
	app.add_handler(add_task_conversation)
	app.add_handler(CallbackQueryHandler(start_show_tasks))
	logger.info("Bot is running ...")
	app.run_polling()
main()

