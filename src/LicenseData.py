class LicenseData:
    pass

class SteamLicenseData(LicenseData):
    def __init__(self, auth_ticket: bytes):
        self.auth_ticket = auth_ticket

class PlayStoreLicenseData(LicenseData):
    def __init__(self, signed_data: str, signature: str | None):
        self.signed_data = signed_data
        self.signature = signature
        