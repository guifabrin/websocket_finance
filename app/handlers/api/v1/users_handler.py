import tornado.web


class UsersHandler(tornado.web.RequestHandler):
    def post(self):
        self.write(self.request.body)
