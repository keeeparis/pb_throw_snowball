from decouple import config
from peewee import *

db_config = {
  'user': config('DB_USER'),
  'password': config('DB_PWD'),
  'host': config('DB_HOST'),
  'database': config('DB'),
}

db = MySQLDatabase(**db_config)

class BaseModel(Model):
  class Meta:
    database = db
    
class User(BaseModel):
  id = BigAutoField(unique=True)
  username = CharField()
  first_name = CharField()
  last_name = CharField(null=True)
  reg_date = DateField()
  
  class Meta: 
    table_name = 'User'

class Chat(BaseModel):
  id = BigAutoField(unique=True)
  reg_date = DateField()
  
  class Meta: 
    table_name = 'Chat'

class UserChat(BaseModel):
  user = ForeignKeyField(User)
  chat = ForeignKeyField(Chat)
  
  class Meta:
    table_name = 'UserChat'

class Interaction(BaseModel):
  from_user = ForeignKeyField(User, backref='interactions')
  to_user = ForeignKeyField(User, backref='interact_to')
  date = DateField()
  
  class Meta:
    table_name = 'Interaction'
    indexes = (
      (('from_user', 'to_user'), True),
    )

# Create Tables
with db:
  db.create_tables([User, Chat, Interaction, UserChat], safe=True)


# try:
#   user1 = User.create(id=1, username='user1')
#   user2 = User.create(id=2, username='user2')
#   user3 = User.create(id=3, username='user3')
  
#   chat111 = Chat.create(id=111)
#   chat222 = Chat.create(id=222)
  
# except IntegrityError:
#   print('already created - user and chats')
  
# try:
#     user1 = User.get(User.username == 'user1')
#     user2 = User.get(User.username == 'user2')
#     user3 = User.get(User.username == 'user3')
#     chat111 = Chat.get(Chat.id == 111)
#     chat222 = Chat.get(Chat.id == 222)
    
#     # UserChat.create(user=user1, chat=chat111)
#     # UserChat.create(user=user2, chat=chat222)
#     # UserChat.create(user=user3, chat=chat111)
#     # UserChat.create(user=user3, chat=chat222)
# except IntegrityError:
#     pass



# query = (User
#          .select()
#          .join(UserChat)
#          .join(Chat)
#          .where(Chat.id == 111))

# for user in query:
#     print(user.username)  # should return user1, user3
    
# chats = (Chat
#           .select()
#           .join(UserChat)
#           .join(User)
#           .where(User.username == 'user3'))

# for chat in chats:
#     print(chat.id)  # should return 111, 222
    
# userchats = (UserChat
#          .select(UserChat, User, Chat)
#          .join(Chat)
#          .switch(UserChat)
#          .join(User)
#          .order_by(User.username))

# for user_chat in userchats:
#   print(user_chat.user.username, '->', user_chat.chat.id)


# print('After initialization of db', db.is_closed())
  
# print('is user1 in chat222 ')
# query = (User
#          .select()
#          .join(UserChat)
#          .join(Chat)
#          .where((User.username == 'user1') & (Chat.id == 111)))

# print(query.exists(db)) # check if exists

# create_tables()
db.close()
# db.connect(reuse_if_open=True)
# db.close()