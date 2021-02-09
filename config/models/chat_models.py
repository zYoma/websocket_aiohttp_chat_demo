import datetime

from sqlalchemy.ext.declarative import declarative_base

from config.settings import CHAT_ENGINE as db

Base = declarative_base()
metadata = Base.metadata


class ChatMessage(db.Model):
    __tablename__ = 'chat_message'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())
    text =  db.Column(db.Text, nullable=False)
