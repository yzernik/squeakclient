from squeak.core import CONTENT_LENGTH


def encode_content(content: str):
    """Convert a string into utf-8 encoded bytes of the required length."""
    encoded = content.encode('utf-8')
    padded = encoded.ljust(CONTENT_LENGTH, b"\x00")
    return padded


def decode_content(data: bytes):
    """Convert utf-8 encoded bytes to a string."""
    unpadded = data.rstrip(b"\00")
    content = unpadded.decode("utf-8", "strict")
    return content
