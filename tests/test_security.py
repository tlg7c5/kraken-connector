"""Tests for the security module (nonce generation and HMAC signing)."""

from kraken_connector.security import get_nonce, sign_message


def test_get_nonce_returns_int():
    nonce = get_nonce()
    assert isinstance(nonce, int)


def test_get_nonce_is_microsecond_precision():
    nonce = get_nonce()
    assert (
        len(str(nonce)) >= 16
    ), f"Nonce {nonce} should have at least 16 digits (microseconds)"


def test_get_nonce_is_non_decreasing():
    n1 = get_nonce()
    n2 = get_nonce()
    assert n2 >= n1


def test_sign_message_deterministic():
    api_secret = "kQH5HW/8p1uGOVjbgWA7FunAmGO8lsSUXNsu3eow76sz84Q18fWxnyRzBHCd3pd5nE9qa99HAZtuZuj6F1huXg=="  # noqa: S105
    data = {
        "nonce": 1616492376594,
        "ordertype": "limit",
        "pair": "XBTUSD",
        "price": "37500",
        "type": "buy",
        "volume": "1.25",
    }
    urlpath = "/0/private/AddOrder"

    sig = sign_message(api_secret, data, urlpath)
    expected = "4/dpxb3iT4tp/ZCVEwSnEsLxx0bqyhLpdfOpc6fn7OR8+UClSV5n9E6aSS8MPtnRfp32bAb0nmbRn6H8ndwLUQ=="
    assert sig == expected


def test_sign_message_returns_string():
    api_secret = "kQH5HW/8p1uGOVjbgWA7FunAmGO8lsSUXNsu3eow76sz84Q18fWxnyRzBHCd3pd5nE9qa99HAZtuZuj6F1huXg=="  # noqa: S105
    data = {"nonce": 12345}
    urlpath = "/0/public/Time"

    sig = sign_message(api_secret, data, urlpath)
    assert isinstance(sig, str)
