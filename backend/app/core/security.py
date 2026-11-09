from functools import lru_cache
from typing import Any
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

bearer = HTTPBearer(auto_error=False)

@lru_cache(maxsize=1)
def jwks_client() -> PyJWKClient:
    return PyJWKClient(settings.oidc_jwks_url, cache_keys=True)

def get_current_principal(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict[str, Any]:
    if not settings.auth_enabled:
        return {"sub": "local-development-user", "preferred_username": "local-admin", "roles": ["APS_ADMIN"], "org_id": "local-development"}
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    try:
        signing_key = jwks_client().get_signing_key_from_jwt(credentials.credentials)
        claims = jwt.decode(
            credentials.credentials, signing_key.key, algorithms=["RS256"],
            issuer=settings.oidc_issuer, audience=settings.oidc_audience,
            options={"require": ["exp", "iat", "sub", "iss"]},
        )
        realm_access = claims.get("realm_access", {})
        claims["roles"] = realm_access.get("roles", [])
        return claims
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc

def require_roles(*allowed_roles: str):
    def dependency(principal: dict = Depends(get_current_principal)):
        if not set(allowed_roles).intersection(principal.get("roles", [])):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return principal
    return dependency
