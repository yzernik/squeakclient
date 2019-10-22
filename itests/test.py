# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the gRPC route guide client."""
from __future__ import print_function

import logging
import random
import time

import grpc
import route_guide_pb2
import route_guide_pb2_grpc


def make_route_note(message, latitude, longitude):
    return route_guide_pb2.RouteNote(
        message=message,
        location=route_guide_pb2.Point(latitude=latitude, longitude=longitude))


def guide_get_one_feature(stub, point):
    feature = stub.GetFeature(point)
    if not feature.location:
        print("Server returned incomplete feature")
        return

    if feature.name:
        print("Feature called %s at %s" % (feature.name, feature.location))
    else:
        print("Found no feature at %s" % feature.location)


def guide_get_feature(stub):
    guide_get_one_feature(stub,
                          route_guide_pb2.Point(
                              latitude=409146138, longitude=-746188906))
    guide_get_one_feature(stub, route_guide_pb2.Point(latitude=0, longitude=0))


def guide_list_features(stub):
    rectangle = route_guide_pb2.Rectangle(
        lo=route_guide_pb2.Point(latitude=400000000, longitude=-750000000),
        hi=route_guide_pb2.Point(latitude=420000000, longitude=-730000000))
    print("Looking for features between 40, -75 and 42, -73")

    features = stub.ListFeatures(rectangle)

    for feature in features:
        print("Feature called %s at %s" % (feature.name, feature.location))


def generate_route(feature_list):
    for _ in range(0, 10):
        random_feature = feature_list[random.randint(0, len(feature_list) - 1)]
        print("Visiting point %s" % random_feature.location)
        yield random_feature.location


def generate_messages():
    messages = [
        make_route_note("First message", 0, 0),
        make_route_note("Second message", 0, 1),
        make_route_note("Third message", 1, 0),
        make_route_note("Fourth message", 0, 0),
        make_route_note("Fifth message", 1, 0),
    ]
    for msg in messages:
        print("Sending %s at %s" % (msg.message, msg.location))
        yield msg


def guide_route_chat(stub):
    responses = stub.RouteChat(generate_messages())
    for response in responses:
        print("Received message %s at %s" % (response.message,
                                             response.location))


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('sqk_alice:50051') as alice_channel, \
         grpc.insecure_channel('sqk_bob:50051') as bob_channel, \
         grpc.insecure_channel('sqk_carol:50051') as carol_channel:

        # Make the stubs
        alice_stub = route_guide_pb2_grpc.RouteGuideStub(alice_channel)
        bob_stub = route_guide_pb2_grpc.RouteGuideStub(bob_channel)
        carol_stub = route_guide_pb2_grpc.RouteGuideStub(carol_channel)

        print("-------------- GetFeature --------------")
        guide_get_feature(alice_stub)
        print("-------------- ListFeatures --------------")
        guide_list_features(alice_stub)
        print("-------------- RouteChat --------------")
        guide_route_chat(alice_stub)

        print("-------------- WalletBalance --------------")
        balance = alice_stub.WalletBalance(route_guide_pb2.WalletBalanceRequest())
        print("Balance: %s" % balance)
        print("Balance confirmed %s %s" % (balance.total_balance, balance.total_balance))
        assert balance.total_balance == 1505000000000

        print("-------------- AddPeer --------------")
        # Connect alice to bob
        addr = route_guide_pb2.Addr(host='sqk_bob')
        request = route_guide_pb2.AddPeerRequest(
            addr=addr,
        )
        alice_stub.AddPeer(request)
        time.sleep(1)

        # Connect bob to carol
        addr = route_guide_pb2.Addr(host='sqk_carol')
        request = route_guide_pb2.AddPeerRequest(
            addr=addr,
        )
        bob_stub.AddPeer(request)
        time.sleep(1)

        # Check how many peers alice has.
        time.sleep(5)
        request = route_guide_pb2.ListPeersRequest()
        alice_peers = alice_stub.ListPeers(request).peers
        bob_peers = bob_stub.ListPeers(request).peers
        carol_peers = carol_stub.ListPeers(request).peers
        print("Alice peers: %s" % alice_peers)
        assert len(alice_peers) >= 2
        print("Bob peers: %s" % bob_peers)
        assert len(bob_peers) >= 2
        print("Carol peers: %s" % carol_peers)
        assert len(carol_peers) >= 2

        print("-------------- GenerateSigningKey --------------")
        request = route_guide_pb2.GenerateSigningKeyRequest()
        alice_address = alice_stub.GenerateSigningKey(request).address
        bob_address = bob_stub.GenerateSigningKey(request).address
        carol_address = carol_stub.GenerateSigningKey(request).address
        print("Generated signing key for Alice with address: %s" % alice_address)
        print("Generated signing key for Bob with address: %s" % bob_address)
        print("Generated signing key for Alice with address: %s" % carol_address)

        print("-------------- MakeSqueak --------------")
        content = 'hello world!'
        request = route_guide_pb2.MakeSqueakRequest(
            content=content,
        )
        response = alice_stub.MakeSqueak(request)
        squeak = response.squeak
        print("Made squeak: %s" % squeak)
        assert 'hello world!' == squeak.content
        assert 400 == squeak.block_height


if __name__ == '__main__':
    logging.basicConfig()
    run()
