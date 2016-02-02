from tornado import httpserver, web, ioloop
import threading
import json
from tornado import websocket
from tornado import web

class EventBus(object):
    clients = list()

    @classmethod
    def subscribe(cls, client):
        cls.clients.append(client)

    @classmethod
    def unsubscribe(cls, client):
        cls.clients.remove(client)

    @classmethod
    def broadcast(cls, message):
        for client in list(cls.clients):
            client.write_message(str(message))


class HomeHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

    def check_origin(self, origin):
        return True


class WebSocketHandler(websocket.WebSocketHandler):
    def open(self):
        EventBus.subscribe(self)

    def on_message(self, message):
        json_message = json.loads(message)
        EventBus.broadcast(json_message)

    def on_close(self):
        EventBus.unsubscribe(self)

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
