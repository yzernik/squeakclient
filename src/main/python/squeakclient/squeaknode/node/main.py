import argparse
import logging

from squeak.params import SelectParams

# from squeakclient.squeaknode.core.data.secret_key import load_secret_key
from squeakclient.squeaknode.core.stores.storage import Storage
from squeakclient.squeaknode.node.clientsqueaknode import ClientSqueakNode
from squeakclient.squeaknode.node.stores.memory.storage import MemoryStorage


def load_storage(args: argparse.Namespace) -> Storage:
    if args.storage_type == 'memory':
        return MemoryStorage()
    else:
        raise NotImplementedError()


def parse_args():
    parser = argparse.ArgumentParser(
        description="squeaknode runs a node using squeak protocol. ",
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
        '--verbose',
        '-v',
        dest='warn_verbose',
        action='store_true',
        help='Show WARNING level logging',
    )
    parser.add_argument(
        '--vverbose',
        '-vv',
        dest='info_verbose',
        action='store_true',
        help='Show INFO level logging',
    )
    parser.add_argument(
        '--vvverbose',
        '-vvv',
        dest='debug_verbose',
        action='store_true',
        help='Show DEBUG level logging',
    )
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.ERROR)
    args = parse_args()
    if args.warn_verbose:
        logging.getLogger().setLevel(logging.WARNING)
    if args.info_verbose:
        logging.getLogger().setLevel(logging.INFO)
    if args.debug_verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    SelectParams('testnet')

    # secret_key = load_secret_key()
    secret_key = None
    storage = load_storage(args)

    node = ClientSqueakNode(secret_key, storage)
    node.start()


if __name__ == "__main__":
    main()
