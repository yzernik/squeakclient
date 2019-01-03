import sys
import time
import threading

import argparse
import logging

from squeak.params import SelectParams
from squeak.params import params

from squeakclient.gui.app import AppContext

from squeakclient.squeaknode.core.blockchain import Blockchain
from squeakclient.squeaknode.core.stores.storage import Storage
from squeakclient.squeaknode.node.clientsqueaknode import ClientSqueakNode
from squeakclient.squeaknode.node.stores.memory.storage import MemoryStorage
from squeakclient.squeaknode.node.rpc_blockchain import RPCBlockchain
from squeakclient.squeaknode.node.rpc import RPCServer


def load_storage() -> Storage:
    return MemoryStorage()


def load_blockchain(rpc_host, rpc_user, rpc_pass) -> Blockchain:
    return RPCBlockchain(
        host=rpc_host,
        port=18556,
        rpc_user=rpc_user,
        rpc_password=rpc_pass,
    )


def _start_node(network, rpc_host, rpc_user, rpc_pass):
    SelectParams(network)
    storage = load_storage()
    blockchain = load_blockchain(rpc_host, rpc_user, rpc_pass)
    node = ClientSqueakNode(storage, blockchain)
    thread = threading.Thread(
        target=node.start,
        args=(),
    )
    thread.daemon = True
    thread.start()
    print('Started node')
    return node, thread


def _start_rpc_server(node, rpc_port, rpc_user, rpc_pass):
    rpc_server = RPCServer(node, rpc_port, rpc_user, rpc_pass)
    thread = threading.Thread(
        target=rpc_server.start,
        args=(),
    )
    thread.daemon = True
    thread.start()
    print('Started rpc server')
    return rpc_server, thread


def parse_args():
    parser = argparse.ArgumentParser(
        description="squeaknode runs a node using squeak protocol. ",
    )
    parser.add_argument(
        '--network',
        dest='network',
        type=str,
        default='mainnet',
        choices=['mainnet', 'testnet', 'regtest'],
        help='The bitcoin network to use',
    )
    parser.add_argument(
        '--rpcport',
        dest='rpcport',
        type=int,
        default=params.RPC_PORT,
        help='RPC server port number',
    )
    parser.add_argument(
        '--rpcuser',
        dest='rpcuser',
        type=str,
        default='',
        help='RPC username',
    )
    parser.add_argument(
        '--rpcpass',
        dest='rpcpass',
        type=str,
        default='',
        help='RPC password',
    )
    parser.add_argument(
        '--storage-type',
        dest='storage_type',
        type=str,
        default='memory',
        choices=['memory', 'sqllite'],
        help='Type of storage to use for the node',
    )
    parser.add_argument(
        '--btcd.rpchost',
        dest='btcd_rpchost',
        type=str,
        default='localhost',
        help='Blockchain (bitcoin) backend hostname',
    )
    parser.add_argument(
        '--btcd.rpcuser',
        dest='btcd_rpcuser',
        type=str,
        default='',
        help='Blockchain (bitcoin) backend username',
    )
    parser.add_argument(
        '--btcd.rpcpass',
        dest='btcd_rpcpass',
        type=str,
        default='',
        help='Blockchain (bitcoin) backend password',
    )
    parser.add_argument(
        '--headless',
        dest='headless',
        action='store_true',
        help='Run in headlesss mode, without GUI',
    )
    parser.add_argument(
        '--no-headless',
        dest='headless',
        action='store_false',
        help='Do not run in headlesss mode',
    )
    parser.add_argument(
        '--log-level',
        dest='log_level',
        type=str,
        default='info',
        help='Logging level',
    )
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.ERROR)
    args = parse_args()
    level = args.log_level.upper()
    print("level: " + level, flush=True)
    logging.getLogger().setLevel(level)

    rpc_host = args.btcd_rpchost
    rpc_user = args.btcd_rpcuser
    rpc_pass = args.btcd_rpcpass
    print('rpc host:', rpc_host, flush=True)
    print('rpc user:', rpc_user, flush=True)
    print('rpc pass:', rpc_pass, flush=True)

    node, thread = _start_node(args.network, rpc_host, rpc_user, rpc_pass)

    # start rpc server
    rpc_server, rpc_server_thread = _start_rpc_server(node, args.rpcport, args.rpcuser, args.rpcpass)

    if not args.headless:
        appctxt = AppContext(node)
        exit_code = appctxt.run()
        sys.exit(exit_code)
    else:
        while True:
            time.sleep(10)


if __name__ == '__main__':
    main()
