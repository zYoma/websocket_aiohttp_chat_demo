from sqlalchemy import create_engine

from app import init_app
from config.settings import DB_BINDINGS, ALEMBIC_TEST_DB
from utils.custom_pytest_fixtures import *


@pytest.fixture(scope="session", autouse=True)
async def client(temp_db, loop, client_factory):
    ini_app = await init_app(build='test')
    client = await client_factory(ini_app)
    await client.start_server()
    yield client
    await client.close()


@pytest.fixture(scope="session", autouse=True)
def test_database_dsn():
    database_dsn = DB_BINDINGS['chat']['test']['dsn']
    return database_dsn


@pytest.fixture(scope="session", autouse=True)
def temp_db(gino_test_db_factory):
    """Тестовая база"""
    return gino_test_db_factory(alembic_db_alias=ALEMBIC_TEST_DB)


# @pytest.fixture(scope="session", autouse=True)
# def extra_post_test_db_setup(test_database_dsn, auth_token):
#     def insert_auth_token():
#         engine = create_engine(test_database_dsn)
#         sql = f'INSERT INTO auth_token (employee_id, token) VALUES (1, \'{auth_token}\')'
#         engine.execute(sql)
#     return insert_auth_token
