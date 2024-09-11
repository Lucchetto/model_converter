from enum import IntEnum
import os
from typing import Dict, Any
from datetime import datetime, timezone
import logging
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64

from src.LicenseData import LicenseData, PlayStoreLicenseData, SteamLicenseData

class PlayStoreLicensingStatus(IntEnum):
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

class LicenseValidator:
    
    __LICENSE_RESPONSE_VALIDITY_TIME = 6 * 60 * 60 * 1000
    
    play_console_pub_key = None
    steam_partner_web_api_key = None
    
    def __init__(self):
        play_console_pub_key_str = os.environ.get('PLAY_CONSOLE_PUB_KEY')
        if play_console_pub_key_str:
            logging.info("PLAY_CONSOLE_PUB_KEY defined, Play Store licensing validation will be performed")
            key = serialization.load_der_public_key(
                base64.b64decode(play_console_pub_key_str), 
                backend=default_backend()
            )
            # Check if the key is an instance of RSA public key
            if isinstance(key, rsa.RSAPublicKey):
                self.play_console_pub_key = key
            else:
                raise ValueError("The key is not an RSA public key.")
        else:
            logging.info("LICENSING_PUB_KEY not defined, no Play Store licensing validation will be performed")
        
        self.steam_partner_web_api_key = os.environ.get("STEAM_PARTNER_WEB_API_KEY")
        if self.steam_partner_web_api_key:
            logging.info("STEAM_PARTNER_WEB_API_KEY defined, Steam licensing validation will be performed")
        else:
            logging.info("STEAM_PARTNER_WEB_API_KEY not defined, no Steam licensing validation will be performed")
    
    @staticmethod
    def safe_str_to_int(s, default=None):
        """Safely convert a string to an integer. If conversion fails, return the default value."""
        try:
            return int(s)
        except ValueError:
            return default
    
    def validate_play_store_license(self, license_data: PlayStoreLicenseData | None) -> bool:
        # license_data is always valid when no Play Store key is defined
        if self.play_console_pub_key == None:
            return True
        
        if license_data is None:
            return False
        
        signed_data_split = license_data.signed_data.split("|")
        if len(signed_data_split) < 6:
            return False
        license_status = PlayStoreLicensingStatus.from_value(LicenseValidator.safe_str_to_int(signed_data_split[0]))
        package_name = signed_data_split[2]
        # Remove extra data separated with |{timestamp}:{extra_data}
        timestamp = int(signed_data_split[5].split(":")[0])
        # License responses with old timestamp should considered invalid too
        if (timestamp + self.__LICENSE_RESPONSE_VALIDITY_TIME < datetime.now(timezone.utc).timestamp() * 1000):
            return False

        # Checking signature is not necessary if not licensed or if licensed check signature is provided
        if license_status is not PlayStoreLicensingStatus.LICENSED or license_data.signature is None:
            return False

        # Verify reponse data integrity if status is licensed
        try:
            self.play_console_pub_key.verify(
                base64.b64decode(license_data.signature),
                license_data.signed_data.encode(),
                padding.PKCS1v15(),
                hashes.SHA1()
            )
            return True
        except InvalidSignature as _:
            return False

    def validate_steam_license(self, license_data: SteamLicenseData) -> bool:
        pass