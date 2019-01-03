import requests
import json


class RPCClient(object):
    """Access the squeaknode using RPC."""

    def __init__(
            self,
            host: str,
            port: int,
            rpc_user: str,
            rpc_password: str,
    ) -> None:
        # self.url = f"http://{rpc_user}:{rpc_password}@{host}:{port}/jsonrpc"
        self.url = f"http://{host}:{port}/jsonrpc"
        # self.url = f'https://{rpc_user}:{rpc_password}@{host}:{port}'
        self.headers = {'content-type': 'application/json'}
        self.auth = (rpc_user, rpc_password)

    def make_request(self, method, *params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        try:
            response = requests.post(
                self.url,
                data=json.dumps(payload),
                headers=self.headers,
                auth=self.auth,
            ).json()
            return response["result"]
        except Exception:
            raise RPCClientError()

    def echo(self, s) -> str:
        return self.make_request("echo", s)

    def addpeer(self, host) -> str:
        return self.make_request("addpeer", host)


class RPCClientError(Exception):
    pass
