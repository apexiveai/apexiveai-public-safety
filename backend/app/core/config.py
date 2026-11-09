from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "APEXIVEAI PUBLIC SAFETY API"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://aps_user:change_this_password@localhost:5433/aps_db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:5173"
    oidc_issuer: str = "http://localhost:8080/realms/apexiveai"
    oidc_jwks_url: str = "http://localhost:8080/realms/apexiveai/protocol/openid-connect/certs"
    oidc_audience: str = "aps-api"
    auth_enabled: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
