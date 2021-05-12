import tornado.web


class HttpHandler(tornado.web.RequestHandler):
    template = ''

    def initialize(self, template):
        self.template = template

    def get(self):
        self.render('../../templates/'+self.template+'.html')
