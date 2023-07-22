import datetime
from peewee import *

from src.db.database import Chat, User, Interaction, UserChat, db

def create_chat(chat_id: int) -> None:
  Chat.create(id=chat_id, reg_date=datetime.datetime.now())
  
def create_user(id: int, username: str, first_name: str, last_name: str) -> None:
  User.create(id=id, username=username, first_name=first_name, last_name=last_name, reg_date=datetime.datetime.now())
  
def create_user_chat(user_id: int, chat_id: int) -> None:
  user = User.get(User.id == user_id)
  chat = Chat.get(Chat.id == chat_id)
  UserChat.create(user=user, chat=chat)
  
def create_interaction(from_user_id: int, to_user_id: int, chat_id: int) -> None:
  from_user = User.get(User.id == from_user_id)
  to_user = User.get(User.id == to_user_id)
  Interaction.create(from_user=from_user, to_user=to_user, chat_id=chat_id, date=datetime.datetime.now())
  
  
  
def chat_exists(chat_id: int) -> bool:
  try:
    Chat.get_by_id(chat_id)
    return True
  except DoesNotExist:
    return False
  
def user_exists(user_id: int) -> bool:
  try:
    User.get_by_id(user_id)
    return True
  except DoesNotExist:
    return False



def user_in_chat(chat_id: int, user_id: int) -> bool:
  query = (User
         .select()
         .join(UserChat)
         .join(Chat)
         .where((User.id == user_id) & (Chat.id == chat_id)))
  return query.exists(db)

def get_all_users(chat_id: int):
  query = (User
         .select()
         .join(UserChat)
         .join(Chat)
         .where(Chat.id == chat_id))  
  return query
 
 
 
def user_targets(chat_id: int, user_id: int):
  query = (User
          .select(User, fn.COUNT(User.id).alias('user_count'))
          .join(Interaction, on=Interaction.to_user)
          .where((Interaction.from_user == user_id) & (Interaction.chat_id == chat_id))
          .group_by(User)
          .order_by(fn.COUNT(User.id).desc()))
  return query
  