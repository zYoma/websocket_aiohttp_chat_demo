from utils.dialect import LiteralDialect
from chat.services.querysets import create_chat_message_queryset, get_all_chat_message_queryset
from .test_chat_fixtures import *


async def test_index_view(client_get, index_request_data):
    response = await client_get(**index_request_data)

    assert response.status == 200

def test_get_all_chat_message_queryset(get_all_chat_message_sql):
    queryset = get_all_chat_message_queryset()
    orm_sql = LiteralDialect.get_sql_with_var(queryset)

    assert orm_sql == get_all_chat_message_sql


async def test_create_chat_message(create_chat_message_request_data):
    await create_chat_message_queryset(**create_chat_message_request_data)
    messeges = await get_all_chat_message_queryset().gino.first()

    assert messeges[2] == 'text'
