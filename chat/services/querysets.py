import datetime
from typing import Type
from sqlalchemy.sql.selectable import Select

from config.models.chat_models import ChatMessage
from config.settings import CHAT_ENGINE as db


def create_chat_message_queryset(nickname: str, text: str) -> Type[Select]:

    return ChatMessage.create(nickname=nickname, text=text, created_date=datetime.datetime.now())


def get_all_chat_message_queryset() -> Type[Select]:

    return ChatMessage.select('nickname', 'created_date', 'text') \
        .where(ChatMessage.created_date > db.func.current_date()) \
        .order_by(ChatMessage.created_date)


def del_old_chat_message_queryset() -> Type[Select]:

    return ChatMessage.delete.where(ChatMessage.created_date < db.func.current_date())
