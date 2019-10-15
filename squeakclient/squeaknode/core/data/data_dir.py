from pathlib import Path


# TODO: Use different dir for testnet.
DATA_DIR = Path.home() / '.squeak'


def create_data_dir() -> None:
    """Create the data dir if it does not yet exist."""
    Path(DATA_DIR).mkdir(exist_ok=True)
