from werkzeug.exceptions import abort
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher


class RPCServer(object):

    def __init__(self, node, port, username, password):
        self.node = node
        self.port = port
        self.username = username
        self.password = password

    def start(self):
        app = self.get_application()
        run_simple('localhost', self.port, app)

    def check_auth(self, username, password):
        """This function is called to check if a username /
        password combination is valid.
        """
        return username == self.username and password == self.password

    def get_application(self):
        def application(environ, start_response):
            request = Request(environ)
            auth = request.authorization
            print(auth)
            if not auth or not self.check_auth(auth.username, auth.password):
                abort(401)

            # Dispatcher is dictionary {<method_name>: callable}
            dispatcher["echo"] = self.echo
            dispatcher["addpeer"] = self.addpeer
            dispatcher["generate_signing_key"] = self.generate_signing_key
            dispatcher["get_signing_key"] = self.get_signing_key
            dispatcher["get_address"] = self.get_address
            dispatcher["make_squeak"] = self.make_squeak

            response = JSONRPCResponseManager.handle(
                request.data, dispatcher)

            response = Response(response.json, mimetype='application/json')
            return response(environ, start_response)
        return application

    def echo(self, s):
        return s

    def addpeer(self, host):
        return str(self.node.connect_host(host))

    def generate_signing_key(self):
        return str(self.node.generate_signing_key())

    def get_signing_key(self):
        return str(self.node.get_signing_key())

    def get_address(self):
        return str(self.node.get_address())

    def make_squeak(self, content):
        return str(self.node.make_squeak(content))
