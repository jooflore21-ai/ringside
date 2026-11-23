"""Importa todos os models para o Alembic enxergar o metadata completo."""

from .base import Base
from .loja import Categoria, ItemPedido, Pedido, Produto, Usuario
from .wrestling import (
    Cinturao, Evento, Faccao, Luta, Lutador, Participante, Reinado, ReinadoLutador,
)

__all__ = [
    "Base",
    "Usuario",
    "Categoria",
    "Produto",
    "Pedido",
    "ItemPedido",
    "Evento",
    "Lutador",
    "Luta",
    "Participante",
    "Faccao",
    "Cinturao",
    "Reinado",
    "ReinadoLutador",
]
