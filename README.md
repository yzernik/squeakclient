Usage
=====

Start a bitcoin client with RPC server:

```
open /Applications/Bitcoin-Qt.app --args -server -rpcuser=my_user -rpcpassword=my_pass
```

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
make clean
python -m fbs freeze
open target/SqueakClient.app --args --network=testnet --log-level=debug
```

or to view log output

```
target/SqueakClient.app/Contents/MacOS/SqueakClient --network=testnet --log-level=debug
```


Docker
======

First, initialize submodule
```
git submodule update --init --recursive
```

Set up X windows:
https://cntnr.io/running-guis-with-docker-on-mac-os-x-a14df6a76efc

Start the client in docker-compose:
```
cd docker
docker-compose build
docker-compose up sqk_btc
```

or try using the ctl:
```
docker-compose run -d --name alice sqk_btc
docker-compose run -d --name bob sqk_btc
docker exec -i -t alice bash
# ./start-sqkctl.sh
squeaknode-cli> echo foooo
squeaknode-cli> addpeer bob
```


Testing
=======

```
docker-compose -f docker-compose.yml -f docker-compose.test.yml build
docker-compose -f docker-compose.yml -f docker-compose.test.yml up
```
then in `Peers` tab, add peer connection to other peer.
