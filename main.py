from tornado import httpserver, web, ioloop
import threading
import json
from tornado import websocket
from tornado import web

class EventBus(object):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if EventBus._instance is None:
            with EventBus._lock:
                if EventBus._instance is None:
                    EventBus._instance = super(EventBus, cls).__new__(cls)
        return EventBus._instance

    def __init__(self):
        self.clients = []

    def subscribe(self, client):
        self.clients.append(client)

    def unsubscribe(self, client):
        self.clients.remove(client)

    def broadcast(self, message):
        for client in list(self.clients):
            client.write_message(str(message))


class HomeHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

    def check_origin(self, origin):
        return True

class WebSocketHandler(websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)
        self.event_bus = EventBus()

    def open(self):
        self.event_bus.subscribe(self)

    def on_message(self, message):
        json_message = json.loads(message)
        self.write_message(json_message)

    def on_close(self):
        self.event_bus.unsubscribe(self)

    def check_origin(self, origin):
        return True

settings = {
    'auto_reload': True,
}

application = web.Application([
    (r'/', HomeHandler),
    (r'/websocket/', WebSocketHandler),
], **settings)

if __name__ == "__main__":
    http_server = httpserver.HTTPServer(application)
    http_server.listen(8007)
    ioloop.IOLoop.instance().start()