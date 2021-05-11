import json
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    def set_default_headers(self, *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Content-Type", "application/json")

    def write_error(self, status_code, message=None):
        self.set_status(status_code)
        if message:
            self.finish(json.dumps({
                "message": message
            }))
        elif status_code:
            self.set_status(status_code)
            self.finish()

    def write_response(self, status_code, result=None):
        self.set_status(status_code)
        if result:
            self.finish(self.to_json(result))
        elif status_code:
            self.set_status(status_code)
            self.finish()

    def to_json(self, result):
        try:
            if type(result) is list:
                serializable_result = [row.to_dict() for row in result]
            else:
                serializable_result = result.to_dict()
            return json.dumps(serializable_result)
        except:
            return json.dumps(result)
