import tornado.ioloop
import tornado.web
import tornado.httpserver

from app.handlers.http import main_handler
from app.handlers.api.v1 import users_handler, posts_handler
from app.repositories import user_repository, post_repository
from app.database.database import create


def make_app():
    settings = {
        'debug': True,
    }
    return tornado.web.Application([
        (r"/", main_handler.MainHandler),
        (r'/api/v1/users/?(.*)?', users_handler.UsersHandler,
         dict(repository=user_repository.UserRepository())),
        (r'/api/v1/posts/?(.*)?', posts_handler.PostsHandler,
         dict(repository=post_repository.PostRepository())),
        (r'/js/(.*)', tornado.web.StaticFileHandler,
         {'path': './dist/scripts'}),
        (r'/css/(.*)', tornado.web.StaticFileHandler,
         {'path': './dist/styles'}),
        (r'/images/(.*)', tornado.web.StaticFileHandler,
         {'path': './dist/images'}),
    ], **settings)


if __name__ == "__main__":
    create()
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
