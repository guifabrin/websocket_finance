import tornado.ioloop
import tornado.web
import tornado.httpserver

from app.handlers import main_handler


def make_app():
    settings = {
        'debug': True,
        # other stuff
    }
    return tornado.web.Application([
        (r"/", main_handler.MainHandler),
        (r'/js/(.*)', tornado.web.StaticFileHandler,
         {'path': './dist/scripts'}),
        (r'/css/(.*)', tornado.web.StaticFileHandler,
         {'path': './dist/styles'}),
        (r'/images/(.*)', tornado.web.StaticFileHandler,
         {'path': './dist/images'}),
    ], **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
