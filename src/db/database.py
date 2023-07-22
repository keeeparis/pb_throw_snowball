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
  chat_id = ForeignKeyField(Chat)
  date = DateField()
  
  class Meta:
    table_name = 'Interaction'
    indexes = (
      (('from_user', 'to_user'), False),
    )

# Create Tables
with db:
  db.create_tables([User, Chat, Interaction, UserChat], safe=True)

db.close()