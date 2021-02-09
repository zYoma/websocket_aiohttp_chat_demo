from chat.views import Index, WebSocket


chat_ws_url = '/ws/{user}'
test_url = '/test'


routes = [
    (chat_ws_url, WebSocket),
    (test_url, Index),
    
    ]