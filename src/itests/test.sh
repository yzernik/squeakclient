#!/bin/bash

# Wait for nodes to start up.
sleep 10

# Connect alice to bob.
add_peer_output=$(./sqk_ctl.exp "sqk_alice" "addpeer sqk_bob")
echo "add_peer_output"
echo $add_peer_output
if [ "$add_peer_output" != "None" ]; then
    echo "add_peer_output is not correct"
    exit 1
fi

# Get alice's peers.
sleep 1
get_peers_output=$(./sqk_ctl.exp "sqk_alice" "getpeers")
echo "get_peers_output"
echo $get_peers_output

[[ $date =~ ^[0-9]{8}$ ]]

if [[ "$get_peers_output"  =~ ^\[Peer(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b:18555)\]$ ]]; then
    echo "get_peers_output is not correct"
    exit 1
fi


# Get sqk's peers.
sleep 1
get_peers_output=$(./sqk_ctl.exp "sqk_alice" "getpeers")
echo "get_peers_output"
echo $get_peers_output

# Get alice's wallet balance.
sleep 1
get_wallet_balance_output=$(./sqk_ctl.exp "sqk_alice" "getwalletbalance")
echo "get_wallet_balance_output"
echo $get_wallet_balance_output
if [ "$get_wallet_balance_output" != "0" ]; then
    echo "get_wallet_balance_output is not correct"
    exit 1
fi

exit 0
