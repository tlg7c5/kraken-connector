"""Message signatures and nonces required for authenticated endpoints."""
import base64
import hashlib
import hmac
import time
import urllib.parse
from typing import Dict


def get_nonce() -> int:
    """Nonce counter.

    Returns:
        An ever-increasing unsigned integer up to 64 bits wide.
    """
    return int(time.time() * 1000)


def sign_message(api_secret: str, data: Dict, urlpath: str):
    postdata = urllib.parse.urlencode(data)

    # Unicode-objects must be encoded before hashing
    encoded = (str(data["nonce"]) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    signature = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(signature.digest())

    return sigdigest.decode()


def _sign(self, data, urlpath):
    """Sign request data according to Kraken's scheme.

    :param data: API request parameters
    :type data: dict
    :param urlpath: API URL path sans host
    :type urlpath: str
    :returns: signature digest
    """
    postdata = urllib.parse.urlencode(data)

    # Unicode-objects must be encoded before hashing
    encoded = (str(data["nonce"]) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    signature = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(signature.digest())

    return sigdigest.decode()
