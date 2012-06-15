import hello_es
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import options, define
from tornado.ioloop import IOLoop

define("port", default=8888, help="run on the given port", type=int)


class HelloShopplyServiceHandler(tornado.web.RequestHandler):
  def get(self):
    model = hello_es.Model()
    self.set_header('Content-Type', 'application/json')
    self.write(model.get_message()['allinfo'])    


def main():
  tornado.options.parse_command_line()
  application = tornado.web.Application([
    (r'/', HelloShopplyServiceHandler),
    ])
  application.listen(options.port)
  print('running tornado on port %d' % options.port)
  IOLoop.instance().start()


if __name__ == '__main__':
  main()
