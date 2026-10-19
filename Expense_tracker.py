from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,CommandHandler,MessageHandler,filters,CallbackQueryHandler,ConversationHandler,ContextTypes
from telegram.request import HTTPXRequest
from telegram.constants import ChatAction
import sqlite3
import os
def start_db():
	conn = sqlite3.connect('test.db')
	cursor = conn.cursor()
	return conn,cursor
token = os.getenv('token')
clear_history = InlineKeyboardButton(text="Clear History",callback_data="clear_history")
income = InlineKeyboardButton(text="+ Add Income", callback_data="income")
expense = InlineKeyboardButton(text="- Add Expense", callback_data="expense")
balance = InlineKeyboardButton(text="Balance",callback_data="balance")
history = InlineKeyboardButton(text="History",callback_data="history")
report = InlineKeyboardButton(text="Report",callback_data="report")
help = InlineKeyboardButton(text="Help",callback_data="help")
back1 = InlineKeyboardButton(text="Back To Menu",callback_data="back1")
see_all = InlineKeyboardButton(text="See All",callback_data="see_all")
see_income = InlineKeyboardButton(text="See Income",callback_data="see_income")
see_expense = InlineKeyboardButton(text="See Expense",callback_data="see_expense")
history_keyboard = [[see_income,see_expense],[see_all,back1]]
history_view = InlineKeyboardMarkup(history_keyboard)
back_keyboard = [[back1]]
back_markup = InlineKeyboardMarkup(back_keyboard)
menu_keyboard = [[income,expense],[balance,history],[report,help]]
menu_markup = InlineKeyboardMarkup(menu_keyboard)
report_keyboard = [[back1,clear_history]]
report_markup = InlineKeyboardMarkup(report_keyboard)
categories = """
1) Salary
2) Freelance
3) Foods
4) Gifts
5) Others
"""
async def start(update: Update,context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_chat_action(chat_id=update.message.chat.id,action=ChatAction.TYPING)
	await update.message.reply_text(f"""
==============================
                     Expense Tracker
==============================
Hello, {update.message.chat.first_name}

Welcome to Expense Tracker Bot! 💰

I am here to help you manage your money right inside Telegram. Before you start, here is what I can do for you:

📈 Track daily Income & Expenses by category
📊 Generate instant Daily & Monthly financial reports
⚙️ Set a Monthly Budget and get overspending alerts
📥 Export all your financial records into a CSV file
🔐 Keep your personal financial data 100% private

""",reply_markup=menu_markup)
async def button_handler(update: Update,context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query
	await query.answer()
	if query.data == "back1":
		await query.edit_message_text(f"""
==============================
                     Expense Tracker
==============================
Hello, {query.message.chat.first_name}

Welcome to Expense Tracker Bot! 💰

I am here to help you manage your money right inside Telegram. Before you start, here is what I can do for you:

📈 Track daily Income & Expenses by category
📊 Generate instant Daily & Monthly financial reports
⚙️ Set a Monthly Budget and get overspending alerts
📥 Export all your financial records into a CSV file
🔐 Keep your personal financial data 100% private
""",reply_markup=menu_markup)

	elif query.data == "help":
		await query.edit_message_text("""
Help Menu:

[+ Add Income] Button    - To add amount of Income
[- Add Expense] Button   - To add amount of Expense
[History] Button         - To see your Income and Expense history
[Balance] Button         - To see your Balance
[Report] Button          - To see Your monthly Reports\n""",reply_markup=back_markup)
	elif query.data == "history":
		conn,cursor = start_db()
		cursor.execute("select * from user_logs where chat_id = ? order by id desc limit 2",(query.message.chat.id,))
		history_list = cursor.fetchall()
		if history_list is None or len(history_list) == 0:
			conn.close()
			await query.message.reply_text("[✘] You History is Empty!")
			return
		his_result = ""
		for history in history_list:
			if not str(history[3]).startswith('-'):
				his_result += f"[+] {history[2]}           + {history[3]} MMK\nNote: {history[4]}\nAt:     {history[5]}\n\n"
			else:
				his_result += f"[-] {history[2]}            {history[3]} MMK\nNote: {history[4]}\nAt:     {history[5]}\n\n"
		await query.edit_message_text(f"📜 Transaction History\n\n{his_result}",reply_markup=history_view)
		conn.close()
	elif query.data == "see_all":
		conn,cursor = start_db()
		cursor.execute("Select * from user_logs where chat_id = ?",(query.message.chat.id,))
		history_list = cursor.fetchall()
		his_result = ""
		for history in history_list:
			if not str(history[3]).startswith('-'):
				his_result += f"[+] {history[2]}           + {history[3]} MMK\nNote: {history[4]}\nAt:     {history[5]}\n\n"
			else:
				his_result += f"[-] {history[2]}            {history[3]} MMK\nNote: {history[4]}\nAt:     {history[5]}\n\n"
		await query.edit_message_text(f"📜 Transaction History\n\n{his_result}",reply_markup=history_view)
		conn.close()
	elif query.data == "see_income":
		conn,cursor = start_db()
		cursor.execute("select * from user_logs where  chat_id = ?",(query.message.chat.id,))
		history_list = cursor.fetchall()
		his_result = ""
		for history in history_list:
			if not str(history[3]).startswith('-'):
				his_result += f"[+] {history[2]}           + {history[3]} MMK\nNote: {history[4]}\nAt:     {history[5]}\n\n"
		await query.edit_message_text(f"📜 Transaction History\n\n{his_result}",reply_markup=history_view)
		conn.close()
	elif query.data == "see_expense":
		conn,cursor = start_db()
		cursor.execute("select * from user_logs where  chat_id = ?",(query.message.chat.id,))
		history_list = cursor.fetchall()
		his_result = ""
		for history in history_list:
			if str(history[3]).startswith('-'):
				his_result += f"[-] {history[2]}            {history[3]} MMK\nNote: {history[4]}\nAt:     {history[5]}\n\n"
		await query.edit_message_text(f"📜 Transaction History\n\n{his_result}",reply_markup=history_view)
		conn.close()
	elif query.data == "balance":
		conn,cursor = start_db()
		cursor.execute("select * from Accounts where chat_id = ?",(query.message.chat.id,))
		balance = cursor.fetchone()
		if balance is None:
			conn.close()
			await query.message.reply_text("[✘] Your Wallet is Empty!\nAdd Income First")
			return
		result = f"""
💰 Your Balance

{'Balance':<15}:{balance[2]} MMK

{'Income':<15}:{balance[4]} MMK
{'Expense':<15}:{balance[3]} MMK

"""
		await query.edit_message_text(result,reply_markup=back_markup)
		conn.close()
	elif query.data == "report":
		conn,cursor = start_db()
		cursor.execute("select * from Accounts where chat_id = ?",(query.message.chat.id,))
		balance = cursor.fetchone()
		if balance is None:
			conn.close()
			await query.message.reply_text("[✘] You Wallet is Empty!\nAdd Income First")
			return
		income = balance[4]
		expense = balance[3]
		current_balance = balance[2]
		salary = 0
		freelance = 0
		foods = 0
		gifts = 0
		others = 0
		cursor.execute("select category,amount from user_logs where chat_id = ?",(query.message.chat.id,))
		category_list = cursor.fetchall()
		for cat in category_list:
			if str(cat[1]).startswith('-'):
				if cat[0].lower() == "salary":
					salary += 1
				if cat[0].lower() == "freelance":
					freelance += 1
				if cat[0].lower() == "foods":
					foods += 1
				if cat[0].lower() == "gifts":
					gifts += 1
				if cat[0].lower() == "others":
					others += 1
		salary_bar = "█" * salary if salary > 0 else "░"
		free_bar = "█" * freelance if freelance > 0 else "░"
		food_bar = "█" * foods if foods > 0 else "░"
		gift_bar = "█" * gifts if gifts > 0 else "░"
		other_bar = "█" * others if others > 0 else "░"
		def bar(bar):
			while len(bar) < 25:
				bar += "░"
			return bar
		salary_bar = bar(salary_bar)
		free_bar = bar(free_bar)
		food_bar = bar(food_bar)
		gift_bar = bar(gift_bar)
		other_bar = bar(other_bar)
		def bar_checker(bars):
			full_bar = "█" * 25
			warning = ""
			for bar in bars:
				if  full_bar in bar:
					warning = "[!] One Of Your Expense Category is reach its Limit\nYou Can Clear History to restart it"
					return warning
			return warning
		bars = [salary_bar,free_bar,food_bar,gift_bar,other_bar]
		warning = bar_checker(bars)
		await query.edit_message_text(f"""
📊 Financial Report

{'Balance':<15}:{balance[2]} MMK

{'Income':<15}:{balance[4]} MMK
{'Expense':<15}:{balance[3]} MMK


📈 Expense Breakdown

{'Salary':<18}:{salary_bar}
{'Freelance':<15}:{free_bar}
{'Foods':<17}:{food_bar}
{'Gifts':<20}:{gift_bar}
{'Others':<17}:{other_bar}

{warning}
""",reply_markup=report_markup)
	elif query.data == "clear_history":
		yes = InlineKeyboardButton(text="Yes",callback_data="yes")
		no = InlineKeyboardButton(text="No",callback_data="no")
		yes_no = [[yes,no]]
		yes_or_no = InlineKeyboardMarkup(yes_no)
		await query.edit_message_text("[!] Are Your Sure You want to Clear History!",reply_markup=yes_or_no)
	elif query.data == "yes":
		conn,cursor = start_db()
		cursor.execute("delete from user_logs where chat_id = ?",(query.message.chat.id,))
		cursor.execute("update Accounts set Total_Income=0, Total_expense=0,Total_balance = 0 where chat_id = ?",(query.message.chat.id,))
		conn.commit()
		conn.close()
		await query.edit_message_text("[✓] Your History was cleared Successfully!",reply_markup=back_markup)
	elif query.data == "no":
		await query.edit_message_text("[✓] Process is Canceled",reply_markup=back_markup)

#================================================================================================================================================
async def error_handler(update: Update,context: ContextTypes.DEFAULT_TYPE):
	error = context.error
	print(f"An Error Occurs: {error}")
async def income_start(update: Update,context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query
	await query.answer()
	if query.data == "income":
		await query.message.reply_text("[*] Enter Income Amount")
		return 0
async def expense_start(update: Update,context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query
	await query.answer()
	await query.message.reply_text("[*] Enter Expense Amount")
	return 0
#For income
async def get_income(update: Update,context: ContextTypes.DEFAULT_TYPE):
	amount = update.message.text
	try:
		amount = int(amount)
	except ValueError:
		await update.message.reply_text("[✘] Amount must be Number!")
		return 0
	if amount <= 0:
		await update.message.reply_text("[✘] Amount must be Greater Than Zero!")
		return 0
	context.user_data['amount'] = amount
	await update.message.reply_text(f"[*] Select Catetgory\n\n{categories}")
	return 1
async def get_income_category(update: Update,context: ContextTypes.DEFAULT_TYPE):
	category = update.message.text
	try:
		category = int(category)
	except ValueError:
		await update.message.reply_text("[✘] Your Selection must be Number")
		return 1
	if not category in [1,2,3,4,5]:
		await update.message.reply_text("[✘] Select Numbers Only Contains")
		return 1
	if category == 1:
		category_text = "Salary"
	elif category == 2:
		category_text = "Freelance"
	elif category == 3:
		category_text = "Foods"
	elif category == 4:
		category_text = "Gifts"
	elif category == 5:
		category_text = "Others"
	context.user_data['category'] = category_text
	await update.message.reply_text("[*] Enter Note")
	return 2
async def get_income_note(update: Update,context: ContextTypes.DEFAULT_TYPE):
	note = update.message.text
	context.user_data['note'] = note
	amount = context.user_data['amount']
	category = context.user_data['category']
	conn,cursor = start_db()
	cursor.execute("select Total_balance,Total_Income from Accounts where chat_id = ?",(update.message.chat.id,))
	current_balance = cursor.fetchone()
	if current_balance is None:
		current_balance = 0
		total = amount
		cursor.execute("insert into Accounts(chat_id,Total_balance,Total_Income) values(?,?,?)",(update.message.chat.id,total,total,))
		cursor.execute("insert into user_logs(chat_id,category,amount,note) values(?,?,?,?)",(update.message.chat.id,category,f"+{amount}",note,))
	else:
		total = amount + current_balance[0]
		total_income = amount + current_balance[1]
		cursor.execute("update Accounts set Total_balance = ?, Total_Income = ? where chat_id = ?",(total,total_income,update.message.chat.id,))
		cursor.execute("insert into user_logs(chat_id,category,amount,note) values(?,?,?,?)",(update.message.chat.id,category,f"+{amount}",note,))

	cursor.execute("select Total_balance from Accounts where chat_id = ?",(update.message.chat.id,))
	new_total_balance = cursor.fetchone()
	conn.commit()
	conn.close()
	success_text=f"""
✅ The Income have been record
💰 Amount: {amount} MMK
📂 Category: {category}
📝 Note: {note}
💵 Total Balance: {new_total_balance[0]} MMK
"""
	await update.message.reply_text(success_text,reply_markup=back_markup)
	return ConversationHandler.END
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
	context.user_data.pop('amount',None)
	context.user_data.pop('category',None)
	context.user_data.pop('mark',None)
	await update.message.reply_text("[+] Process is Cancled")
	return ConversationHandler.END

#For Expense
async def get_expense_amount(update: Update,context: ContextTypes.DEFAULT_TYPE):
	amount = update.message.text
	try:
		amount = int(amount)
	except ValueError:
		await update.message.reply_text("[✘] Amount must be Numbers")
		return 0
	if amount <= 0:
		await update.message.reply_text("[✘] Amount must be Greater than Zero")
		return 0
	conn,cursor = start_db()
	cursor.execute("select Total_balance from Accounts where chat_id = ?",(update.message.chat.id,))
	total_balance = cursor.fetchone()
	if total_balance is None:
		conn.close()
		await update.message.reply_text("[✘] Your Wallet is Empty!\n\nUse [Add Income] Button First")
		return ConversationHandler.END
	context.user_data['amount'] = amount
	await update.message.reply_text(f"[*] Enter Category\n\n{categories}")
	return 1
async def get_expense_category(update: Update,context: ContextTypes.DEFAULT_TYPE):
	category = update.message.text
	try:
		category = int(category)
	except ValueError:
		await update.message.reply_text("[✘] Enter Number Only")
		return 1
	if not category in [1,2,3,4,5]:
		await update.message.reply_text("[✘] Select Number Only Contains")
		return 1
	if category == 1:
		category_text = "Salary"
	elif category == 2:
		category_text = "Freelance"
	elif category == 3:
		category_text = "Foods"
	elif category == 4:
		category_text = "Gifts"
	elif category == 5:
		category_text = "Others"
	context.user_data['category'] = category_text
	await update.message.reply_text("[*] Enter Note")
	return 2
async def get_expense_note(update: Update,context: ContextTypes.DEFAULT_TYPE):
	note = update.message.text
	context.user_data['note'] = note
	amount = context.user_data['amount']
	category = context.user_data['category']
	conn,cursor = start_db()
	cursor.execute("select Total_balance,Total_expense from Accounts where chat_id = ?",(update.message.chat.id,))
	total_balance = cursor.fetchone()
	if total_balance is None:
		conn.close()
		await update.message.reply_text("[✘] Your Wallet is Empty!\n\nUse [Add Income] Button First")
		return ConversationHandler.END
	current_balance = total_balance[0] - amount
	new_expense = amount + total_balance[1]
	cursor.execute("update Accounts set Total_balance = ?, Total_expense = ? where chat_id = ?",(current_balance,new_expense,update.message.chat.id,))
	cursor.execute("insert into user_logs(chat_id,category,amount,note) values(?,?,?,?)",(update.message.chat.id,category,f"- {amount}",note,))
	conn.commit()
	conn.close()
	await update.message.reply_text(f"""
✅ The expense has been recorded.
💸 Amount: {amount} MMK
🍜 Category: {category}
📝 Note: {note}
💵 Updated Balance: {current_balance} MMK
""",reply_markup=back_markup)
	return ConversationHandler.END

def main():
	request = HTTPXRequest(read_timeout=120,write_timeout=120)
	app = Application.builder().token(token).request(request).build()
	app.add_handler(CommandHandler('start',start))
	app.add_error_handler(error_handler)
	income_conversation = ConversationHandler(
		entry_points=[CallbackQueryHandler(income_start,pattern='income')],
		states={
			0: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_income)],
			1: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_income_category)],
			2: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_income_note)]
		},
		fallbacks = [CommandHandler('cancel',cancel)]
	)
	expense_conversation = ConversationHandler(
		entry_points=[CallbackQueryHandler(expense_start,pattern='expense')],
		states = {
			0: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_expense_amount)],
			1: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_expense_category)],
			2: [MessageHandler(filters.TEXT & ~filters.COMMAND,get_expense_note)]
		},
		fallbacks=[CommandHandler('cancel',cancel)]
	)
	app.add_handler(income_conversation)
	app.add_handler(expense_conversation)
	app.add_handler(CallbackQueryHandler(button_handler))
	print("Bot is Running ...")
	app.run_polling()
main()

