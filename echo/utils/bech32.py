from typing import Optional

from nostr_sdk import SecretKey, PublicKey


def nsec_to_hex(nsec: str) -> Optional[str]:
    try:
        sk = SecretKey.parse(nsec)
        return sk.to_hex()
    except Exception:
        return None


def npub_to_hex(npub: str) -> Optional[str]:
    try:
        pk = PublicKey.parse(npub)
        return pk.to_hex()
    except Exception:
        return None


def hex_to_npub(hex_key: str) -> Optional[str]:
    try:
        pk = PublicKey.parse(hex_key)
        return pk.to_bech32()
    except Exception:
        return None


def hex_to_nsec(hex_key: str) -> Optional[str]:
    try:
        sk = SecretKey.parse(hex_key)
        return sk.to_bech32()
    except Exception:
        return None


def is_nsec(value: str) -> bool:
    return value.startswith("nsec1") and len(value) > 10


def is_npub(value: str) -> bool:
    return value.startswith("npub1") and len(value) > 10


def is_hex(value: str) -> bool:
    return len(value) == 64 and all(c in "0123456789abcdef" for c in value.lower())
