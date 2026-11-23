"""Configuração lida das variáveis de ambiente. Nenhum segredo fica no código."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    # Chave curta é fácil de quebrar por força bruta: exige pelo menos 32 caracteres.
    jwt_secret: str = Field(min_length=32)
    jwt_algoritmo: str = "HS256"
    jwt_expira_minutos: int = 60
    frontend_origem: str = "http://localhost:5173"
    admin_email: str
    admin_senha: str


@lru_cache
def obter_settings() -> Settings:
    return Settings()
