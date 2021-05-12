import tornado.web


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("../../templates/login_handler.html")
