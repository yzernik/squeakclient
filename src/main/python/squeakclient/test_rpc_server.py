import requests
import json


def main():
    url = "http://localhost:8554/jsonrpc"
    headers = {'content-type': 'application/json'}

    # Example echo method
    payload = {
        "method": "echo",
        "params": ["echome!"],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    assert response["result"] == "echome!"
    assert response["jsonrpc"]
    assert response["id"] == 0

    # generate_signing_key method
    payload = {
        "method": "generate_signing_key",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    assert response["jsonrpc"]
    assert response["id"] == 0
    print(response["result"])

    # get_signing_key method
    payload = {
        "method": "get_signing_key",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    assert response["jsonrpc"]
    assert response["id"] == 0
    print(response["result"])

    # get_address method
    payload = {
        "method": "get_address",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    assert response["jsonrpc"]
    assert response["id"] == 0
    print(response["result"])

    # make_squeak method
    payload = {
        "method": "make_squeak",
        "params": ["hello world!"],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    assert response["jsonrpc"]
    assert response["id"] == 0
    print(response["result"])


if __name__ == "__main__":
    main()
