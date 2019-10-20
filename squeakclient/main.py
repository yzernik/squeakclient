import argparse
import logging
import threading
import time

from squeak.params import SelectParams

from squeakclient.squeaknode.core.blockchain import Blockchain
from squeakclient.squeaknode.core.lightning_client import LightningClient
from squeakclient.squeaknode.core.stores.storage import Storage
from squeakclient.squeaknode.node.clientsqueaknode import ClientSqueakNode
from squeakclient.squeaknode.node.rpc_blockchain import RPCBlockchain
from squeakclient.squeaknode.node.rpc_lightning_client import RPCLightningClient
from squeakclient.squeaknode.node.stores.memory.storage import MemoryStorage
from squeakclient.squeaknode.rpc.route_guide_server import RouteGuideServicer


def load_storage() -> Storage:
    return MemoryStorage()


def load_blockchain(rpc_host, rpc_port, rpc_user, rpc_pass) -> Blockchain:
    return RPCBlockchain(
        host=rpc_host,
        port=rpc_port,
        rpc_user=rpc_user,
        rpc_password=rpc_pass,
    )


def load_lightning_client(rpc_host, rpc_port, network) -> LightningClient:
    return RPCLightningClient(
        host=rpc_host,
        port=rpc_port,
        network=network,
    )


def _start_node(storage, blockchain, lightning_client):
    node = ClientSqueakNode(storage, blockchain, lightning_client)
    thread = threading.Thread(
        target=node.start,
        args=(),
    )
    thread.daemon = True
    thread.start()
    return node, thread


def _start_route_guide_rpc_server(node):
    server = RouteGuideServicer(node)
    thread = threading.Thread(
        target=server.serve,
        args=(),
    )
    thread.daemon = True
    thread.start()
    return server, thread


def parse_args():
    parser = argparse.ArgumentParser(
        description="squeaknode runs a node using squeak protocol. ",
    )
    parser.add_argument(
        '--network',
        dest='network',
        type=str,
        default='mainnet',
        choices=['mainnet', 'testnet', 'regtest', 'simnet'],
        help='The bitcoin network to use',
    )
    parser.add_argument(
        '--rpcport',
        dest='rpcport',
        type=int,
        default=None,
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
        '--btcd.rpcport',
        dest='btcd_rpcport',
        type=int,
        default=18332,
        help='Blockchain (bitcoin) backend port',
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
        '--lnd.rpchost',
        dest='lnd_rpchost',
        type=str,
        default='localhost',
        help='Lightning network backend hostname',
    )
    parser.add_argument(
        '--lnd.rpcport',
        dest='lnd_rpcport',
        type=int,
        default=10009,
        help='Lightning network backend port',
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

    print('network:', args.network, flush=True)
    SelectParams(args.network)

    storage = load_storage()
    blockchain = load_blockchain(
        args.btcd_rpchost,
        args.btcd_rpcport,
        args.btcd_rpcuser,
        args.btcd_rpcpass,
    )
    lightning_client = load_lightning_client(
        args.lnd_rpchost,
        args.lnd_rpcport,
        args.network,
    )

    node, thread = _start_node(storage, blockchain, lightning_client)

    # start rpc server
    route_guide_server, route_guide_server_thread = _start_route_guide_rpc_server(node)

    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()
