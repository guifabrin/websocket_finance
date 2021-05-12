import tornado.web


class FeedHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("../../templates/feed_handler.html")
