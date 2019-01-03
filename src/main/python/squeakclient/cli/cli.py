import sys

import argparse

PROMPT = 'squeaknode-cli>'


def parse_args():
    parser = argparse.ArgumentParser(
        description="CLI for interacting with squeaknode.",
    )
    return parser.parse_args()


def handle_command(line):
    print(line)


def cli():
    print(PROMPT, end=' ', flush=True)
    for line in sys.stdin:
        line = line.strip()
        if line:
            handle_command(line)
        print(PROMPT, end=' ', flush=True)


def main():
    parse_args()
    cli()


if __name__ == "__main__":
    main()
