import tornado.web


class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("../../templates/register_handler.html")
