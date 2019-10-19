import logging
import grpc
import os

from squeakclient.squeaknode.core.lightning_client import LightningClient

import squeakclient.rpc_pb2 as ln
import squeakclient.rpc_pb2_grpc as lnrpc

import codecs


logger = logging.getLogger(__name__)


# Due to updated ECDSA generated tls.cert we need to let gprc know that
# we need to use that cipher suite otherwise there will be a handhsake
# error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'
os.environ["GRPC_VERBOSITY"] = 'DEBUG'

# Lnd cert is at ~/.lnd/tls.cert on Linux and
# ~/Library/Application Support/Lnd/tls.cert on Mac
cert = open(os.path.expanduser('~/.lnd/tls.cert'), 'rb').read()
creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('lnd:10009', creds)
stub = lnrpc.LightningStub(channel)

# Lnd admin macaroon is at ~/.lnd/data/chain/bitcoin/simnet/admin.macaroon on Linux and
# ~/Library/Application Support/Lnd/data/chain/bitcoin/simnet/admin.macaroon on Mac
with open(os.path.expanduser('~/.lnd/data/chain/bitcoin/simnet/admin.macaroon'), 'rb') as f:
    macaroon_bytes = f.read()
    macaroon = codecs.encode(macaroon_bytes, 'hex')


class RPCLightningClient(LightningClient):
    """Access a lightning deamon using RPC."""

    def get_wallet_balance(self):
        # Retrieve and display the wallet balance
        return stub.WalletBalance(ln.WalletBalanceRequest(), metadata=[('macaroon', macaroon)])
