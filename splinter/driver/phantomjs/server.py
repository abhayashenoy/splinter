import threading
from Queue import Queue
from tornado.websocket import WebSocketHandler

class Server(threading.Thread):
  def run(self):
    import tornado.ioloop
    import tornado.web

    self.responseQ = Queue()
    application = tornado.web.Application([
        (r"/", WebsocketServer, dict(queue=self.responseQ, thread=self))
      ])
    application.listen(9999)
    self.ioloop = tornado.ioloop.IOLoop.instance()
    self.ioloop.start()

  def stop(self):
    self.ioloop.stop()
    self.join()

  def send(self, message):
    self.server.write_message(message)
    return self.responseQ.get()

class WebsocketServer(WebSocketHandler):
  def initialize(self, queue, thread):
    self.queue = queue
    thread.server = self

  def open(self):
    pass

  def on_message(self, message):
    self.queue.put(message)

  def on_close(self):
    pass

  def allow_draft76(self):
    return True

if __name__ == '__main__':
  server = Server()
  server.start()

