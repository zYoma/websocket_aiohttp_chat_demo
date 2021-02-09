import pytest

from chat.routes import test_url


@pytest.fixture
def index_request_data():
    return {
        'url': test_url,
        'return_json_body': False,
    }

@pytest.fixture
def get_all_chat_message_sql():
    return "SELECT chat_message.nickname, chat_message.created_date, chat_message.text FROM chat_message WHERE chat_message.created_date > CURRENT_DATE ORDER BY chat_message.created_date"


@pytest.fixture
def create_chat_message_request_data():
    return {
        'nickname': 'tester',
        'text': 'text',
    }
