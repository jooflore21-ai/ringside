"""Erros de domínio e handlers centralizados no formato Problem Details (RFC 9457).

O service lança uma exceção com nome; o handler traduz para HTTP.
Nenhuma rota precisa de try/except.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("ringside")


class ErroDominio(Exception):
    status = 400
    tipo = "erro-de-dominio"
    titulo = "Erro de domínio"

    def __init__(self, detalhe: str):
        super().__init__(detalhe)
        self.detalhe = detalhe


class NaoEncontrado(ErroDominio):
    status, tipo, titulo = 404, "nao-encontrado", "Recurso não encontrado"


class Conflito(ErroDominio):
    status, tipo, titulo = 409, "conflito", "Conflito com o estado atual"


class EstoqueInsuficiente(Conflito):
    tipo, titulo = "estoque-insuficiente", "Estoque insuficiente"


class NaoAutenticado(ErroDominio):
    status, tipo, titulo = 401, "nao-autenticado", "Autenticação necessária"


class SemPermissao(ErroDominio):
    status, tipo, titulo = 403, "sem-permissao", "Acesso negado"


def _problema(request: Request, status: int, tipo: str, titulo: str, detalhe, **extra):
    corpo = {
        "type": f"/erros/{tipo}",
        "title": titulo,
        "status": status,
        "detail": detalhe,
        "instance": request.url.path,
        **extra,
    }
    headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None
    return JSONResponse(corpo, status_code=status, media_type="application/problem+json", headers=headers)


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(ErroDominio)
    async def _dominio(request: Request, exc: ErroDominio):
        return _problema(request, exc.status, exc.tipo, exc.titulo, exc.detalhe)

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException):
        # Rota inexistente (404), método errado (405) etc. no mesmo formato dos demais erros.
        return _problema(request, exc.status_code, f"http-{exc.status_code}", str(exc.detail), str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def _validacao(request: Request, exc: RequestValidationError):
        campos = [
            {"campo": ".".join(str(p) for p in e["loc"][1:]), "mensagem": e["msg"]}
            for e in exc.errors()
        ]
        return _problema(
            request, 422, "validacao", "Dados inválidos",
            "Um ou mais campos não passaram na validação.", erros=campos,
        )

    @app.exception_handler(Exception)
    async def _inesperado(request: Request, exc: Exception):
        # Registra o erro completo no log do servidor; o cliente recebe só a mensagem genérica.
        log.exception("Erro inesperado em %s %s", request.method, request.url.path)
        # Não vaza stack trace para o cliente.
        return _problema(request, 500, "erro-interno", "Erro interno", "Tente novamente mais tarde.")
