"""Conexão com o banco e uma sessão por requisição (injetada via Depends)."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import obter_settings

engine = create_engine(obter_settings().database_url, pool_pre_ping=True)
SessaoLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def obter_sessao() -> Iterator[Session]:
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()
