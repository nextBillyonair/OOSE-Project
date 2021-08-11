from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import os
from flask_socketio import SocketIO
from flask_hashing import Hashing

config = os.getenv('CONFIG', 'development')

app = Flask(__name__)
SESSION_TYPE = 'redis'
app.config.from_object(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()

app.config['DEBUG'] = True
if config == "development":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pwatso14@localhost/footsie'
elif config == 'testing':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/footsie'
else:
    raise ValueError("Invalid configuration for server, use testing or development")

app.secret_key = 'super secret key'

hashing = Hashing(app)

db = SQLAlchemy(app)
socketio = SocketIO(app)

from app.views import ChatsView, ChatView, RequestsView, UserView, TimerView, UserSettingView, RelationView
from app.models import BaseModel, ChatNames, Chats, Messages, Requests, User, UserRelations
from app.views.helperFunctions import AuthenticateHelper, GraphHelper, RequestHelper
