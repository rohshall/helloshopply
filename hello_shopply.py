from hello_es import Model
import tornado.web
import tornado.ioloop

class HelloShopplyServiceHandler(tornado.web.RequestHandler):

    def get(self):
        model = Model()
        self.set_header('Content-Type', 'application/json')
        self.write(model.get_message()['allinfo'])    

application = tornado.web.Application([
  (r'/', HelloShopplyServiceHandler),
  ])

if __name__ == '__main__':
  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()
