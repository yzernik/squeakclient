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

Set up the DISPLAY.
For Mac:
https://cntnr.io/running-guis-with-docker-on-mac-os-x-a14df6a76efc

For Ubuntu:
https://medium.com/@SaravSun/running-gui-applications-inside-docker-containers-83d65c0db110

Set the DISPLAY environment variable with the value from the previous step:
```
export DISPLAY=10.0.0.10:0
```

Start the client in docker-compose:
```
cd docker
docker-compose build
docker-compose up sqk_btc
```

Testing
=======

```
make itest
```
