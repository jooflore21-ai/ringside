"""Hash de senha (bcrypt) e emissão/leitura de JWT."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import obter_settings


def gerar_hash(senha: str) -> str:
    # bcrypt é lento de propósito e embute um salt aleatório em cada hash.
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def conferir_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


def criar_token(usuario_id: int, papel: str) -> str:
    s = obter_settings()
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "papel": papel,
        "iat": agora,
        "exp": agora + timedelta(minutes=s.jwt_expira_minutos),
    }
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algoritmo)


def ler_token(token: str) -> dict:
    """Lança jwt.InvalidTokenError se o token for inválido ou expirado."""
    s = obter_settings()
    return jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algoritmo])
