#!/bin/bash

# Wait for nodes to start up.
sleep 10

# Connect alice to bob.
# ./sqk_ctl.exp "sqk_alice" "addpeer sqk_bob"
add_peer_output=$(./sqk_ctl.exp "sqk_alice" "addpeer sqk_bob")
echo "add_peer_output"
echo $add_peer_output
echo $add_peer_output
echo $add_peer_output
echo $add_peer_output
echo $add_peer_output

# Get alice's peers.
sleep 1
# ./sqk_ctl.exp "sqk_alice" "getpeers"
get_peers_output=$(./sqk_ctl.exp "sqk_alice" "getpeers")
echo "get_peers_output"
echo $get_peers_output
echo $get_peers_output
echo $get_peers_output
echo $get_peers_output
echo $get_peers_output

exit 0
