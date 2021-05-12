import tornado.ioloop
import tornado.web
import tornado.httpserver

from app.handlers.http import main_handler, register_handler, login_handler
from app.handlers.api.v1 import users_handler, posts_handler
from app.repositories import user_repository, post_repository
from app.database.database import create


def make_app():
    settings = {
        'debug': True,
    }
    main_user_repository = user_repository.UserRepository()
    main_post_repository = post_repository.PostRepository()
    return tornado.web.Application([
        (r"/", main_handler.MainHandler),
        (r"/register", register_handler.RegisterHandler),
        (r"/login", login_handler.LoginHandler),
        (r'/api/v1/users/?(.*)?', users_handler.UsersHandler,
         dict(repository=main_user_repository)),
        (r'/api/v1/posts/?(.*)?', posts_handler.PostsHandler,
         dict(repository=main_post_repository)),
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
