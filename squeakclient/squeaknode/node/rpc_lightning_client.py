from typing import Optional

import logging
import requests
import json
import grpc
import os

from squeakclient.squeaknode.core.lightning_client import LightningClient

import squeakclient.rpc_pb2 as ln
import squeakclient.rpc_pb2_grpc as lnrpc

import codecs

import socket


logger = logging.getLogger(__name__)


# Due to updated ECDSA generated tls.cert we need to let gprc know that
# we need to use that cipher suite otherwise there will be a handhsake
# error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

# Lnd cert is at ~/.lnd/tls.cert on Linux and
# ~/Library/Application Support/Lnd/tls.cert on Mac
cert = open(os.path.expanduser('~/.lnd/tls.cert'), 'rb').read()
creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('lnd:10009', creds)
stub = lnrpc.LightningStub(channel)


def isOpen(ip,port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect((ip, int(port)))
      s.shutdown(2)
      return True
   except:
      return False

def checkIsOpen(ip,port):
    logger.info("is open? isOpen('{}', {}): ".format(ip, port) + str(isOpen(ip, port)))


# Lnd admin macaroon is at ~/.lnd/data/chain/bitcoin/simnet/admin.macaroon on Linux and
# ~/Library/Application Support/Lnd/data/chain/bitcoin/simnet/admin.macaroon on Mac
with open(os.path.expanduser('~/.lnd/data/chain/bitcoin/testnet/admin.macaroon'), 'rb') as f:
    macaroon_bytes = f.read()
    macaroon = codecs.encode(macaroon_bytes, 'hex')


class RPCLightningClient(LightningClient):
    """Access a lightning deamon using RPC."""

    def get_wallet_balance(self):
        checkIsOpen('lnd', 9735)
        checkIsOpen('lnd', 9736)
        checkIsOpen('lnd', 9737)
        checkIsOpen('lnd', 9738)
        checkIsOpen('lnd', 9739)

        checkIsOpen('lnd', 10008)
        checkIsOpen('lnd', 10009)
        checkIsOpen('lnd', 10010)
        checkIsOpen('lnd', 10011)
        checkIsOpen('lnd', 10012)
        checkIsOpen('lnd', 10013)
        checkIsOpen('lnd', 18556)

        checkIsOpen('lnd_btc', 10008)
        checkIsOpen('lnd_btc', 10009)
        checkIsOpen('blockchain', 8334)
        checkIsOpen('blockchain', 18334)
        checkIsOpen('blockchain', 18556)
        checkIsOpen('blockchain', 28902)
        checkIsOpen('btcd', 8334)
        checkIsOpen('btcd', 18334)
        checkIsOpen('btcd', 18556)
        checkIsOpen('btcd', 28902)

        try:
            # Retrieve and display the wallet balance
            response = stub.WalletBalance(ln.WalletBalanceRequest(), metadata=[('macaroon', macaroon)])
            return response.total_balance
        except Exception as e:
            logger.error('error: ' + str(e))
            raise e
