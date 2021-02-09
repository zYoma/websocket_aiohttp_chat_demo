import subprocess
from asyncio import set_event_loop_policy

import pytest
from aiohttp.test_utils import TestServer, TestClient
from aiohttp.web import Application
from sqlalchemy_utils import create_database, drop_database
from uvloop import new_event_loop, EventLoopPolicy


@pytest.fixture(scope="session", autouse=True)
def loop():
    """
    Необходимо передавать всем асинхронным фикстурам

    Пример:

    .. code-block:: python
        :emphasize-lines: 2

        @pytest.fixture(scope="session)
        async def my_async_fixture(loop):
            # fixture code

    :return: event loop
    """
    loop = new_event_loop()
    set_event_loop_policy(EventLoopPolicy())
    yield loop

    loop.close()


@pytest.fixture(scope="session")
def client_factory(loop):
    """
    Фабрика для создания тестовых клиентов


    .. code-block:: python
        :emphasize-lines: 3,4

        @pytest.fixture(scope="session, autouse=True)
        async def client(temp_db, loop, client_factory):
            ini_app = await init_app(build='test', enable_auth=false)
            client = await client_factory(ini_app)
            await client.start_server()
            yield client
            await client.close()
            ...


    :param loop: фикстура loop
    :param app: Передается вложенной корутине
    :type app: aiohttp.web.Application
    """
    async def make_client(app: Application) -> TestClient:
        return TestClient(TestServer(app))

    return make_client


@pytest.fixture(scope="session")
def before_migration_setup():
    """
    Фикстура, которую можно переопределять внутри проектного conftest.py для целей проекта,
    если требуется изменить стандартное поведение
    """
    def before_migration_setup_callable(test_database_dsn):
        create_database(test_database_dsn)
    return before_migration_setup_callable


@pytest.fixture(scope="session")
def after_migration_setup():
    """
    Фикстура затычка, которую можно переопределить внутри проектного conftest.py для выполнения дополнительных
    действий после проведения миграций. Должна возвращать callable объект
    """
    def placeholder(test_database_dsn):
        pass
    return placeholder


@pytest.fixture(scope="session")
def last_test_db_action():
    """
    Фикстура, которую можно переопределять внутри проектного conftest.py для целей проекта,
    если требуется изменить стандартное поведение
    """
    def last_test_db_action_callable(test_database_dsn):
        drop_database(test_database_dsn)
    return last_test_db_action_callable


@pytest.fixture(scope="session")
def gino_test_db_factory(test_database_dsn, before_migration_setup, after_migration_setup, last_test_db_action):
    """
    Фабрика для создания тестовых БД

    Зависит от фикстуры `test_database_dsn`, которая должна
    присутствовать в conftest используещего проекта.

    Накатывает миграции на базу, если внутренней функции make_test_db
    передать аргумент с алиасом алембика (у нас определяется в .env файле и
    подгружается внутри settings.py)

     .. code-block:: python
        :emphasize-lines: 12

        #conftest.py

        @pytest.fixture(scope="session", autouse=True)
        def test_database_dsn():
            database = ProjectGinoDB(name="whatever", build="test")
            database_dsn = database.cfg['dsn']
            return database_dsn


        @pytest.fixture(scope="session", autouse=True)
        def temp_db(gino_test_db_factory):
            return gino_test_db_factory(alembic_db_alias=ALEMBIC_TEST_DB)


    :param before_migration_setup: фикстура для предварительных манипуляций с базой:
    создание и прочие манипуляции, которые необходимо сделать перед миграциями (заполнить, например).
    По умолчанию создает базу данных по полученному dsn.
    Можно переопределить в conftest.py проекта, например, чтобы чтобы создавать не базу данных, а схему,
    если при тестировании нужно создавать/удалять только схему
    :param after_migration_setup: фикстура для дополнительных манипуляций с
    базой, которые необходимо сделать после миграций.
    По умолчанию ничего не выполняет, можно переопределить в conftest.py проекта
    :param last_test_db_action: фикстура для манипуляций с базой, которые необходимо сделать после выполнения тестов.
    По умолчанию удаляет базу по переданному dsn. Можно переопределить в conftest.py проекта, например,
    чтобы чтобы удалять не базу данных, а схему, если при тестировании нужно создавать/удалять только схему.
    :param test_database_dsn: фикстура с DSN тестовой базы
    :param alembic_db_alias: ALEMBIC_TEST_DB из .env
    """

    def _make_migrations(alembic_db_alias: str):
        command = f'alembic -x db={alembic_db_alias} upgrade head'
        subprocess.run(command, stdout=subprocess.PIPE,
                       encoding='utf-8', shell=True)

    def make_test_db(alembic_db_alias: str = None):
        before_migration_setup(test_database_dsn)
        if alembic_db_alias:
            _make_migrations(alembic_db_alias)
        after_migration_setup(test_database_dsn)

    yield make_test_db
    last_test_db_action(test_database_dsn)


@pytest.fixture(scope="session")
async def client_get(client):
    """
    Вызываемая фикстура для отправки `GET` HTTP-запросов

    Определяет внутри корутину _client_get со следующими аргументами:
        `url`: (str) адрес эндпоинта

        `params`: параметры GET-запроса

        `return_json_body`: (bool) (default=True) нужно ли вернуть тело
        запроса в формате
        json.

        `**other_data`:

    Пример использования:


    .. code-block:: python

        #test_myview_fixtures.py

        @pytest.fixture
        def my_view_credentials():
            credentials = {
                'page': 1,
                'id': 3
            }
            request_data = {
                'url': my_url,
                'params': credentials
            }

            return request_data


    .. code-block:: python

        #test_myview.py
        async def test_my_view_get(client_get,
                                    my_view_credentials,
                                    expected_response_body):
            response, resp_body = await client_get(**my_view_credentials)

            assert response.status == 200
            assert resp_body == expected_response_body

    :param client: фикстура client из ``conftest.py`` проекта
    :return: ответ от сервера в формате json
    """

    async def _client_get(url, params='', _client=client, return_json_body=True, **other_data):
        response = await _client.get(url, params=params, **other_data)

        if return_json_body:
            response_body = await response.json()
            return response, response_body

        return response

    return _client_get


@pytest.fixture(scope="session")
async def client_post(client):
    """
    Вызываемая фикстура для отправки `POST` HTTP-запросов

    Определяет внутри корутину _client_get со следующими аргументами:
        `url`: (str) адрес эндпоинта

        `request_body`: тело запроса

        `return_json_body`: (bool) нужно ли вернуть тело запроса в формате json

        `**kwargs`

    Пример использования:

    .. code-block:: python

        #test_myview.py
        async def test_login_success(client, client_post):
            request_body = {"username": "hello", "password": "world"}
            response, response_body = await client_post(
                login_url,
                request_body,
                return_json_body=True
            )

            assert response.status == 200
            assert response_body["role"] == "PYTHONISTA"

    :param client: фикстура client из ``conftest.py`` проекта
    :return: ответ от сервера в формате json
    """

    async def _client_post(url, request_body, _client=client, return_json_body=False, **kwargs):
        response = await _client.post(
            url,
            data=request_body,
            **kwargs
        )

        if return_json_body:
            response_body = await response.json()
            return response, response_body

        return response

    return _client_post


@pytest.fixture(scope="session")
async def client_delete(client):
    """
    Вызываемая фикстура для отправки `DELETE` HTTP-запросов
    """

    async def _client_delete(url, request_body, _client=client, return_json_body=False, **kwargs):

        response = await _client.delete(
            url,
            data=request_body,
            **kwargs
        )

        if return_json_body:
            response_body = await response.json()
            return response, response_body

        return response

    return _client_delete


@pytest.fixture(scope="session")
async def client_put(client):
    """
    Вызываемая фикстура для отправки `PUT` HTTP-запросов
    Работает аналогично client_post
    """

    async def _client_put(url, request_body, _client=client, return_json_body=False, **kwargs):
        response = await _client.put(
            url,
            data=request_body,
            **kwargs
        )

        if return_json_body:
            response_body = await response.json()
            return response, response_body

        return response

    return _client_put
