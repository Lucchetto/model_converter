import base64
import logging
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from enum import IntEnum
import os

def setup_pub_key() -> (rsa.RSAPublicKey | None):
    str = os.environ.get('LICENSING_PUB_KEY')
    if str:
        logging.info("LICENSING_PUB_KEY defined, Play Store licensing validation will be performed")
        key = serialization.load_der_public_key(
            base64.b64decode(str), 
            backend=default_backend()
        )
        # Check if the key is an instance of RSA public key
        if isinstance(key, rsa.RSAPublicKey):
            return key
        else:
            raise ValueError("The key is not an RSA public key.")
    else:
        logging.info("LICENSING_PUB_KEY not defined, no licensing validation will be performed")
        return None

class LicensingStatus(IntEnum):
    LICENSED = 0x0
    NOT_LICENSED = 0x1
    LICENSED_OLD_KEY = 0x2
    ERROR_NOT_MARKET_MANAGED = 0x3
    ERROR_SERVER_FAILURE = 0x4
    ERROR_OVER_QUOTA = 0x5
    ERROR_CONTACTING_SERVER = 0x101
    ERROR_INVALID_PACKAGE_NAME = 0x102
    ERROR_NON_MATCHING_UID = 0x103
    UNKNOWN = -1

    @classmethod
    def from_value(cls, value):
        """Get the enum constant for the given value, or UNKNOWN if the value doesn't exist."""
        return cls(value) if value in cls._value2member_map_ else cls.UNKNOWN

def safe_str_to_int(s, default=None):
    """Safely convert a string to an integer. If conversion fails, return the default value."""
    try:
        return int(s)
    except ValueError:
        return default

def validate_license(key: rsa.RSAPublicKey, licensing_response_data: str | None, signature: str | None) -> bool:
    """Validates license response from Play Store
    """
    # Extract license data from response
    if licensing_response_data is None:
        return False
    license_data = licensing_response_data.split("|")
    if len(license_data) < 6:
        return False
    license_status = LicensingStatus.from_value(safe_str_to_int(license_data[0]))
    package_name = license_data[2]

    # Checking signature is not necessary if not licensed or if licensed check signature is provided
    if license_status is not LicensingStatus.LICENSED or signature is None:
        return False

    # Verify reponse data integrity if status is licensed
    try:
        key.verify(
            base64.b64decode(signature),
            licensing_response_data.encode(),
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        return True
    except InvalidSignature as e:
        return False
