from telegram import Update
from telegram.ext import ContextTypes
import random
from src.util import chat_exists, create_chat, create_interaction, create_user, \
  create_user_chat, createMention, get_all_users, read_file, \
  user_exists, user_in_chat
from src.database import db

lines = read_file('../assets/throw_output.txt')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Send a message when the command /start is issued."""
  chat_id = update.message.chat_id
  
  db.connect(reuse_if_open=True)
    
  if chat_exists(chat_id=chat_id): 
    await context.bot.send_message(
      text="Бот уже инициализорован. Принять учатие можно с помощью команды /play, кидать снежки /throw", 
      chat_id=chat_id
    )
  else:
    create_chat(chat_id=chat_id)
    
    await context.bot.send_message(
      text="Отлично, игра началась. Принять учатие можно с помощью команды /play, кидать снежки /throw",
      chat_id=chat_id
    )
  db.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Send a message when the command /help is issued."""
  # await update.message.reply_text("Help!")
  chat_id = update.message.chat_id
  
  await context.bot.send_message(
      text="/start -> Активировать бота \n/play -> Активировать игрока \n/throw -> Бросить снежок \n", 
      chat_id=chat_id
    )
  
async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Register user when command /play is issued."""
   
  current_user = update.effective_user
  chat_id = update.message.chat_id
    
  if not chat_exists(chat_id=chat_id):
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

    await context.bot.send_message(
      text=response_first,
      chat_id=chat_id,
      parse_mode="Markdown"
    )
  else:
    await context.bot.send_message(
      text=response_already,
      chat_id=chat_id,
      parse_mode="Markdown"
    )   
  
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
  """Show registered users when command /list is issued."""

  chat_id = update.message.chat_id
  
  if not chat_exists(chat_id=chat_id):
    return await context.bot.send_message(
      text="Сначала инициализируйте бота с помощью команды /start",
      chat_id=chat_id
    )
  
  query = get_all_users(chat_id=chat_id)
  
  if query.count() == 0:
    return await context.bot.send_message(
      text="В этом чате никто не хочет играть :(",
      chat_id=chat_id,
    )
  
  output = ''
  
  for i, user in enumerate(query):
    output += f"{i+1}. {createMention(username=user.username, id=user.id)}\n"
      
  await context.bot.send_message(
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
  
  current_user = update.effective_user
  chat_id = update.message.chat_id
  
  if not chat_exists(chat_id=chat_id):
    return await context.bot.send_message(
      text="Сначала инициализируйте бота с помощью команды /start",
      chat_id=chat_id
    )
    
  if not user_in_chat(chat_id=chat_id, user_id=current_user.id):
    return await context.bot.send_message(
      text="Сначала Вы должны зарегистроваться с помощью команды /play",
      chat_id=chat_id,
    )
    
  users = get_all_users(chat_id=chat_id)
  number_of_users = users.count()
  
  if number_of_users == 1:
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
  
  create_interaction(from_user_id=current_user.id, to_user_id=target_user_id)
  
  current_user_link = createMention(current_user.username, current_user.id)
  target_user_link = createMention(target_user.username, target_user.id)
  
  random_line = random.randint(0, len(lines))
  text = lines[random_line].replace('{A}', current_user_link).replace('{B}', target_user_link)
    
  await context.bot.send_message(
    text=text,
    chat_id=chat_id,
    parse_mode="Markdown",
    disable_notification=True
  )
    
  