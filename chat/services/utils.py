import datetime

import aiocron

from chat.services.querysets import del_old_chat_message_queryset


def get_time_now():
    return time_to_str(datetime.datetime.now())


def time_to_str(time):
    return time.strftime("%H:%M")


@aiocron.crontab('0 1 * * *')
async def db_cleanup():
    """ Удаляет старые сообщения из БД. Запускается раз в день. """
    await del_old_chat_message_queryset().gino.status()
    print('БД очищена')
