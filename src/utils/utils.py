import os

def createMention(username: str, id: int) -> str:
  return "["+username+"](tg://user?id="+str(id)+")"

def read_file(file_name: str) -> list[str]:
  f = open(os.path.join(os.path.dirname(__file__), file_name), 'r')
  lines = f.readlines()
  f.close()
  return lines
  