from app.schemas import RefreshTokenSchema
from app.core.config import settings
from app.core.exceptions.token import DecodeTokenException
from app.core.utils.token_helper import TokenHelper

class JwtService:
    async def verify_token(self, token: str) -> None:
        TokenHelper.decode(token=token)

    async def refresh_access_token(
        self,
        refresh_token: str
    ) -> str:
        refresh_token = TokenHelper.decode(token=refresh_token)
        if refresh_token.get("sub") != "refresh":
            raise DecodeTokenException()

        return TokenHelper.encode(payload={
            "id": refresh_token.get("id"),
            "onyen": refresh_token.get("onyen")
        }, expire_period=settings.ACCESS_TOKEN_EXPIRES_MINUTES)