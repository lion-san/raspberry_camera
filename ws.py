import os
import sys
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import options
from tornado.ioloop import PeriodicCallback

WPORT = int(os.environ.get("PORT", 8000))

# index.html
class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

# NO SSL index.html
class IndexnHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("indexn.html")

#WS
class WebSocket(tornado.websocket.WebSocketHandler):
    waiters = set() #multi clients connect OK
    wdata = ""

    def open(self):
        print("open websocket connection")
        WebSocket.waiters.add(self) #client add
        self.callback = PeriodicCallback(self._send_message, 30000) #time out taisaku
        self.callback.start()

    def on_close(self):
        WebSocket.waiters.remove(self) #client remove
        self.callback.stop()
        print("close websocket connection")

    def on_message(self, message):
        WebSocket.wdata = message
        WebSocket.send_updates(message)

    @classmethod
    def send_updates(cls, message): #this method is singleton
        print(message + ":connection=" + str(len(cls.waiters)))
        for waiter in cls.waiters:
            try:
                waiter.write_message(message)
            except:
                print("Error sending message", exc_info=True)

    #TIME OUT BOUSHI CALL BACK 30Sec
    def _send_message(self):
        self.write_message("C:POLLING")

app = tornado.web.Application([
    (r"/", IndexHandler),
    (r"/nossl", IndexnHandler),
    (r"/ws", WebSocket),
])


if __name__ == "__main__":
    argvs = sys.argv
    argc = len(argvs)

    options.parse_command_line()
    if argc == 1:
        print("NO SSL CONNECTION")
        app.listen(WPORT)
    else:
        print("SSL CONNECTION")
        app.listen(WPORT, ssl_options={ 
            "certfile": "server.crt",
            "keyfile": "server.key",
        })
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
