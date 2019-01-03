from pathlib import Path

from squeak.core.signing import CSigningKey

from squeakclient.squeaknode.core.data.data_dir import create_data_dir
from squeakclient.squeaknode.core.data.data_dir import DATA_DIR


SECRET_KET_FILE = Path(DATA_DIR) / 'secret_key.dat'


def save_secret_key(secret_key: CSigningKey) -> None:
    """Save the secret key to the secret key file."""
    s = str(secret_key)
    create_data_dir()
    with open(SECRET_KET_FILE, 'w') as f:
        f.write(s)


def load_secret_key() -> CSigningKey:
    """Load the secret key from the secret key file."""
    with open(SECRET_KET_FILE, 'r') as f:
        s = f.read()
    return CSigningKey(s)
