import random


def generate_nonce():
    return random.SystemRandom().getrandbits(64)
