from aiohttp import web, WSMsgType
from loguru import logger

from chat.services.querysets import create_chat_message_queryset, get_all_chat_message_queryset
from chat.services.utils import get_time_now, time_to_str

class Index(web.View):

    async def get(self):
        ip = self.request.remote

        return web.Response(text=ip, status=200)


class WebSocket(web.View):

    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        
        self.user = self.request.match_info['user']
        self.request.app.wslist[self.user] = ws

        await self.get_last_message(ws)      

        async for msg in ws:

            if msg.type == WSMsgType.text:
                if msg.data == 'close':
                    await ws.close()
                    break

                else:
                    await create_chat_message_queryset(self.user, msg.data)
                    await self.broadcast(msg.data)

            elif msg.type == WSMsgType.error:
                break

            elif msg.type == WSMsgType.closed:
                await ws.close()
                break

        await self.disconnect(ws, self.user)

        return ws
    
    def get_user_in_chat(self):
        return [user for user in self.request.app.wslist]

    async def get_last_message(self, ws):
        """ Шлем пользователю последние сообщения при подключении. """
        messeges = await get_all_chat_message_queryset().gino.all()

        for mes in messeges[-30:]:
            message = {
                'text': mes.text,
                'user': mes.nickname,
                'time': time_to_str(mes.created_date),
                'user_list': self.get_user_in_chat(),
            }
            await self.send_massage(ws, mes.nickname, message)


    async def broadcast(self, text, user=None):
        """ Отправка сообщений всем. """
        user = self.user if user is None else user

        message = {
            'text': text,
            'user': user,
            'time': get_time_now(),
            'user_list': self.get_user_in_chat(),
        }

        for user, ws in list(self.request.app.wslist.items()):
            await self.send_massage(ws, user, message)

    async def send_massage(self, ws, user, message):
        """ Отправка сообщения. """
        try:
            await ws.send_json(message)
        except ConnectionResetError:
            await self.disconnect(ws, user=user)


    async def disconnect(self, ws, user):
        """ Закрываем соединение и отправлем сообщение о выходе. """
        self.request.app.wslist.pop(user, None)
        await ws.close()
