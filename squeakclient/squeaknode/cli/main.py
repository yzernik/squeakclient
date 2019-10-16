import sys

import argparse

from squeakclient.squeaknode.cli.rpc_client import RPCClient

import squeak.params

from squeak.params import SelectParams


PROMPT = 'squeaknode-cli>'


def parse_args():
    parser = argparse.ArgumentParser(
        description="CLI for interacting with squeaknode.",
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
        '--host',
        type=str,
        default='localhost',
        help="RPC server host.",
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help="RPC server port.",
    )
    parser.add_argument(
        '--rpcuser',
        type=str,
        default='',
        help="RPC username.",
    )
    parser.add_argument(
        '--rpcpass',
        type=str,
        default='',
        help="RPC password.",
    )
    return parser.parse_args()


def parse_cmd(cmd):
    parser = argparse.ArgumentParser(
        description="Command sent to the squeaknode CLI.",
    )
    subparsers = parser.add_subparsers(help='sub-command help')

    EchoCommand.add_parser(subparsers)
    AddPeerCommand.add_parser(subparsers)
    GetPeersCommand.add_parser(subparsers)
    GenerateSigningKeyCommand.add_parser(subparsers)
    GetSigningKeyCommand.add_parser(subparsers)
    GetWalletBalanceCommand.add_parser(subparsers)

    return parser.parse_args(cmd.split())


def make_rpc_client(args):
    return RPCClient(
        host=args.host,
        port=args.port or squeak.params.params.RPC_PORT,
        rpc_user=args.rpcuser,
        rpc_password=args.rpcpass,
    )


def handle_command(line, rpc_client):
    try:
        args = parse_cmd(line)
        args.command(args, rpc_client)
    except SystemExit:
        pass


def cli(rpc_client):
    print(PROMPT, end=' ', flush=True)
    for line in sys.stdin:
        line = line.strip()
        if line:
            handle_command(line, rpc_client)
        print(PROMPT, end=' ', flush=True)
    print('', flush=True)


def main():
    args = parse_args()
    SelectParams(args.network)
    rpc_client = make_rpc_client(args)
    cli(rpc_client)


class Command(object):

    @classmethod
    def add_parser(cls, subparsers):
        subparser = cls.setup_subparser(subparsers)
        subparser.set_defaults(command=cls.run)

    @classmethod
    def run(self, args, rpc_client):
        pass


class EchoCommand(Command):

    @classmethod
    def setup_subparser(cls, subparsers):
        subparser = subparsers.add_parser(
            "echo",
            description="Echo a string.",
            add_help=False
        )
        subparser.add_argument(
            "-h", "--help", action="help",
            help='',
        )
        subparser.add_argument(
            's',
            help="The string that will be echoed.",
        )
        subparser.add_argument(
            '--x',
            default='dunno',
            help="This does nothing.",
        )
        return subparser

    @classmethod
    def run(self, args, rpc_client):
        print(rpc_client.echo(args.s))


class AddPeerCommand(Command):

    @classmethod
    def setup_subparser(cls, subparsers):
        subparser = subparsers.add_parser(
            "addpeer",
            description="Add a new peer.",
            add_help=False
        )
        subparser.add_argument(
            "-h", "--help", action="help",
            help='',
        )
        subparser.add_argument(
            'host',
            help="The host of the new peer to connect.",
        )
        return subparser

    @classmethod
    def run(self, args, rpc_client):
        print(rpc_client.addpeer(args.host))


class GetPeersCommand(Command):

    @classmethod
    def setup_subparser(cls, subparsers):
        subparser = subparsers.add_parser(
            "getpeers",
            description="Get connected peers.",
            add_help=False
        )
        subparser.add_argument(
            "-h", "--help", action="help",
            help='',
        )
        return subparser

    @classmethod
    def run(self, args, rpc_client):
        print(rpc_client.getpeers())


class GenerateSigningKeyCommand(Command):

    @classmethod
    def setup_subparser(cls, subparsers):
        subparser = subparsers.add_parser(
            "generatesigningkey",
            description="Generate a new signing key and load it in the client.",
            add_help=False
        )
        subparser.add_argument(
            "-h", "--help", action="help",
            help='',
        )
        return subparser

    @classmethod
    def run(self, args):
        print('Running the generate signing key command.')


class GetSigningKeyCommand(Command):

    @classmethod
    def setup_subparser(cls, subparsers):
        subparser = subparsers.add_parser(
            "getsigningkey",
            description="Generate the signing key from the client.",
            add_help=False
        )
        subparser.add_argument(
            "-h", "--help", action="help",
            help='',
        )
        return subparser

    @classmethod
    def run(self, args):
        print('Running the get signing key command.')


class GetWalletBalanceCommand(Command):

    @classmethod
    def setup_subparser(cls, subparsers):
        subparser = subparsers.add_parser(
            "getwalletbalance",
            description="Get the wallet balance.",
            add_help=False
        )
        subparser.add_argument(
            "-h", "--help", action="help",
            help='',
        )
        return subparser

    @classmethod
    def run(self, args, rpc_client):
        print(rpc_client.getwalletbalance())


if __name__ == "__main__":
    main()
