import os
from typing import Union
from telegram import User

def createMention(user: Union[User, None]) -> str:
  if user == None:
    return ''
  
  if user.username == None:
    return user.first_name
  else:
    return f"[{user.username}](tg://user?id={str(user.id)})"

def read_file(file_name: str) -> list[str]:
  f = open(os.path.join(os.path.dirname(__file__), file_name), 'r')
  lines = f.readlines()
  f.close()
  return lines
  