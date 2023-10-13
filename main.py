from flask import Flask, Response, render_template


class EndpointAction(object):
    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        result = self.action()
        return result


class Core(object):
    NAME = "3Dasha"

    def __init__(self):
        self.app = Flask(self.NAME)
        self.host = "localhost"
        self.port = 5000
        self.debug = True
        self.__add_endpoints()

    def run(self):
        self.app.run(self.host, self.port, self.debug)

    def __add_endpoints(self):
        self.__add_endpoint(endpoint='/', endpoint_name='index', handler=self.__index)

    @staticmethod
    def __index():
        return render_template("index.html")

    def __add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))


if __name__ == "__main__":
    core = Core()
    core.run()

