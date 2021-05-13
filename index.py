import tornado.ioloop
import tornado.web
import tornado.httpserver

from app.handlers.http import http_handler
from app.handlers.api.v1 import users_handler, crud_handler, auth_handler
from app.repositories import user_repository, post_repository, session_repository
from app.database.database import create


def make_app():
    settings = {
        'debug': True,
    }
    main_user_repository = user_repository.UserRepository()
    main_post_repository = post_repository.PostRepository()
    main_session_repository = session_repository.SessionRepository()
    return tornado.web.Application([
        (r"/", http_handler.HttpHandler, dict(template='main_handler')),
        (r"/register", http_handler.HttpHandler,
         dict(template='register_handler')),
        (r"/login", http_handler.HttpHandler,
         dict(template='login_handler')),
        (r"/feed", http_handler.HttpHandler, dict(template='feed_handler')),
        (r'/api/v1/users/?(.*)?', users_handler.UsersHandler,
         dict(repository=main_user_repository)),
        (r'/api/v1/posts/?(.*)?', crud_handler.CrudHandler,
         dict(repository=main_post_repository)),
        (r'/api/v1/auth/?(.*)?', auth_handler.AuthHandler,
         dict(user_repository=main_user_repository, session_repository=main_session_repository)),
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
