import logging
from pydantic import BaseModel, ValidationError
import requests

class SteamUser_AuthenticateUserTicketRequest(BaseModel):
    key: str
    appid: int
    ticket: str
    identity: str

class SteamUser_AuthenticateUserTicketResponse(BaseModel):
    result: str
    steamid: str
    ownersteamid: str
    vacbanned: bool
    publisherbanned: bool

class SteamUser_CheckAppOwnershipRequest(BaseModel):
    key: str
    steamid: str
    appid: int

class SteamUser_CheckAppOwnershipResponse(BaseModel):
    ownsapp: bool
    permanent: bool
    timestamp: str
    ownersteamid: int
    sitelicense: bool

class SteamUserApiClient:
    
    @staticmethod
    def authenticate_user_ticket(request: SteamUser_AuthenticateUserTicketRequest) -> SteamUser_AuthenticateUserTicketResponse | None:
        url = "https://partner.steam-api.com/ISteamUserAuth/AuthenticateUserTicket/v1"
        response = requests.get(url, params=request.model_dump())
        
        try:
            return SteamUser_AuthenticateUserTicketResponse.model_validate(response.json()["response"]["params"])
        except ValidationError as e:
            logging.exception(e)
            return None

    @staticmethod
    def check_app_ownership(request: SteamUser_CheckAppOwnershipRequest) -> SteamUser_CheckAppOwnershipResponse | None:
        url = "https://partner.steam-api.com/ISteamUser/CheckAppOwnership/v2"
        response = requests.get(url, params=request.model_dump())
        print(response.json())
        
        try:
            return SteamUser_CheckAppOwnershipResponse.model_validate(response.json()["appownership"])
        except ValidationError as e:
            logging.exception(e)
            return None