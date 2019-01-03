import argparse

from squeak.core.signing import CSigningKey

from squeakclient.squeaknode.core.secret_key import save_secret_key


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a new secret key.",
    )
    return parser.parse_args()


def generate_secret_key():
    signing_key = CSigningKey.generate()
    save_secret_key(signing_key)


def main():
    parse_args()
    generate_secret_key()


if __name__ == "__main__":
    main()
