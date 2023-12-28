import random
from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from telegram.constants import ParseMode

from src.db.database import db
from src.db.utils import chat_exists, create_chat, create_interaction, create_user, \
  create_user_chat, user_targets, get_all_users, user_exists, user_in_chat
from src.utils.utils import read_file, createMention

lines = read_file('../../assets/throw_output.txt')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Send a message when the command /start is issued."""
  db.connect(reuse_if_open=True)
  
  chat_id = update.message.chat_id
    
  if chat_exists(chat_id=chat_id): 
    db.close()
    return await context.bot.send_message(
      text="Бот уже инициализорован. Принять учатие можно с помощью команды /play, кидать снежки /throw", 
      chat_id=chat_id
    )
  else:
    create_chat(chat_id=chat_id)
    db.close()
    return await context.bot.send_message(
      text="Отлично, игра началась. Принять учатие можно с помощью команды /play, кидать снежки /throw",
      chat_id=chat_id
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Send a message when the command /help is issued."""
  # await update.message.reply_text("Help!")
  chat_id = update.message.chat_id
  
  await context.bot.send_message(
      text="/start -> Активировать бота \n/play -> Активировать игрока \n/throw -> Бросить снежок \n/list -> Список игроков \n/stats -> Статистика\n", 
      chat_id=chat_id
    )
  
async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Register user when command /play is issued."""
  db.connect(reuse_if_open=True)
   
  current_user = update.effective_user
  chat_id = update.message.chat_id
    
  if not chat_exists(chat_id=chat_id):
    db.close()
    return await context.bot.send_message(
      text="Сначала инициализируйте бота с помощью команды /start",
      chat_id=chat_id
    )
  
  mention = createMention(current_user.username, current_user.id)
  response_first = f"{mention} теперь участвует в игре!"
  response_already = f"{mention} уже участвует в игре!"
  
  if not user_in_chat(chat_id=chat_id, user_id=current_user.id):
    if not user_exists(current_user.id):
      create_user(id=current_user.id, username=current_user.username, first_name=current_user.first_name, last_name=current_user.last_name)
    
    create_user_chat(user_id=current_user.id, chat_id=chat_id)

    db.close()
    return await context.bot.send_message(
      text=response_first,
      chat_id=chat_id,
      parse_mode="Markdown"
    )
  else:
    db.close()
    return await context.bot.send_message(
      text=response_already,
      chat_id=chat_id,
      parse_mode="Markdown"
    )   
  
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
  """Show registered users when command /list is issued."""
  db.connect(reuse_if_open=True)
  
  chat_id = update.message.chat_id
  
  if not chat_exists(chat_id=chat_id):
    db.close()
    return await context.bot.send_message(
      text="Сначала инициализируйте бота с помощью команды /start",
      chat_id=chat_id
    )
  
  query = get_all_users(chat_id=chat_id)
  
  if query.count() == 0:
    db.close()
    return await context.bot.send_message(
      text="В этом чате никто не хочет играть :(",
      chat_id=chat_id,
    )
  
  output = ''
  
  for i, user in enumerate(query):
    output += f"{i+1}. {createMention(username=user.username, id=user.id)}\n"
     
  db.close() 
  return await context.bot.send_message(
    text=output,
    chat_id=chat_id,
    parse_mode="Markdown"
  )

# async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#   chat_id = update.message.chat_id
#   current_user = update.effective_user
  
#   userInfo = await context.bot.get_chat_member(chat_id=chat_id, user_id=current_user.id)
#   isAdmin = userInfo.status == 'creator' or 'administrator'
  
#   values = update.message.text.replace('/remove_user', '')
  
#   if len(values) == 0:
#     await update.message.reply_text(
#       f"Вы не добавили username для удаления"
#     )
#   else: 
#     await update.message.reply_text(
#       f"{values}"
#     )
  
async def throw_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Throw snowball when command /throw is issued."""
  db.connect(reuse_if_open=True)
  
  current_user = update.effective_user
  chat_id = update.message.chat_id
  
  if not chat_exists(chat_id=chat_id):
    db.close()
    return await context.bot.send_message(
      text="Сначала инициализируйте бота с помощью команды /start",
      chat_id=chat_id
    )
    
  if not user_in_chat(chat_id=chat_id, user_id=current_user.id):
    db.close()
    return await context.bot.send_message(
      text="Сначала Вы должны зарегистроваться с помощью команды /play",
      chat_id=chat_id,
    )
    
  users = get_all_users(chat_id=chat_id)
  number_of_users = users.count()
  
  if number_of_users == 1:
    db.close()
    return await context.bot.send_message(
      text='Участвует только один человек. Мы же не позволим ему кидать снежки в самого себя?',
      chat_id=chat_id
    )
  
  target_user = ''
  target_user_id = current_user.id
  
  while target_user_id == current_user.id: 
    randomValue = random.randint(1, number_of_users)
    
    for i, user in enumerate(users):
      if i+1 == randomValue:
        target_user = user
        target_user_id = user.id
  
  create_interaction(from_user_id=current_user.id, to_user_id=target_user_id, chat_id=chat_id)
  
  current_user_link = createMention(current_user.username, current_user.id)
  target_user_link = createMention(target_user.username, target_user.id)
  
  random_line = random.randint(0, len(lines) - 1)
  text = lines[random_line].replace('{A}', current_user_link).replace('{B}', target_user_link)
    
  db.close()
  return await context.bot.send_message(
    text=text,
    chat_id=chat_id,
    parse_mode="Markdown",
    disable_notification=True
  )
    
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
  """Show stats when command /stats is issued."""
  db.connect(reuse_if_open=True)
  
  current_user = update.effective_user
  chat_id = update.message.chat_id
  
  if not chat_exists(chat_id=chat_id):
    db.close()
    return await context.bot.send_message(
      text="Сначала инициализируйте бота с помощью команды /start",
      chat_id=chat_id
    )
    
  if not user_in_chat(chat_id=chat_id, user_id=current_user.id):
    db.close()
    return await context.bot.send_message(
      text="Сначала Вы должны зарегистроваться с помощью команды /play",
      chat_id=chat_id,
    )
  
  query = user_targets(chat_id=chat_id, user_id=current_user.id)
  total = 0
  output_rest = ''
  
  for i, user in enumerate(query.dicts()):
    # total += user.user_count
    # output_rest += f"{i+1}. {user.username} — _{user.user_count} раз(а)_.\n"
    
    total += user.get('user_count')
    output_rest += f"{i+1}. {escape_markdown(user.get('username'), 2)} — _{user.get('user_count')} раз(а)_.\n"

  output_start_1 = f"Брошено снежков: *{total}*.\n"
  output_start_2 = f"Из них:\n" if total > 0 else ''
  output_start = output_start_1 + output_start_2
  output = output_start + output_rest

  db.close() 
  
  return await context.bot.send_message(
    text=output.replace(".", "\.").replace("(", "\(").replace(")", "\)"),
    chat_id=chat_id,
    parse_mode=ParseMode.MARKDOWN_V2
  )