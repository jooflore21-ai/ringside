"""Núcleo exigido pelo PDF: usuario, categoria, produto, pedido, item_pedido."""

from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CriadoEmMixin

PAPEIS = ("cliente", "admin")
STATUS_PEDIDO = ("aguardando_pagamento", "pago", "enviado", "entregue", "cancelado")


def _in(coluna: str, valores: tuple[str, ...]) -> str:
    lista = ", ".join(f"'{v}'" for v in valores)
    return f"{coluna} IN ({lista})"


class Usuario(CriadoEmMixin, Base):
    __tablename__ = "usuario"
    __table_args__ = (CheckConstraint(_in("papel", PAPEIS), name="ck_usuario_papel"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    papel: Mapped[str] = mapped_column(String(20), nullable=False, server_default="cliente")

    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="usuario")


class Categoria(Base):
    __tablename__ = "categoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    produtos: Mapped[list["Produto"]] = relationship(back_populates="categoria")


class Produto(CriadoEmMixin, Base):
    __tablename__ = "produto"
    __table_args__ = (
        CheckConstraint("preco > 0", name="ck_produto_preco_positivo"),
        CheckConstraint("estoque >= 0", name="ck_produto_estoque_nao_negativo"),
        # Um produto se liga a no máximo um: evento (ingresso), lutador, facção ou cinturão (réplica).
        CheckConstraint(
            "num_nonnulls(evento_id, lutador_id, faccao_id, cinturao_id) <= 1",
            name="ck_produto_um_vinculo",
        ),
        Index("ix_produto_nome", "nome"),
        Index("ix_produto_categoria_id", "categoria_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estoque: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    imagem_url: Mapped[str | None] = mapped_column(String(500))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categoria.id", ondelete="RESTRICT"), nullable=False
    )
    evento_id: Mapped[int | None] = mapped_column(ForeignKey("evento.id", ondelete="RESTRICT"))
    lutador_id: Mapped[int | None] = mapped_column(ForeignKey("lutador.id", ondelete="RESTRICT"))
    faccao_id: Mapped[int | None] = mapped_column(ForeignKey("faccao.id", ondelete="RESTRICT"))
    cinturao_id: Mapped[int | None] = mapped_column(ForeignKey("cinturao.id", ondelete="RESTRICT"))

    categoria: Mapped["Categoria"] = relationship(back_populates="produtos")
    evento: Mapped["Evento | None"] = relationship(back_populates="ingressos")  # noqa: F821
    lutador: Mapped["Lutador | None"] = relationship(back_populates="produtos")  # noqa: F821
    faccao: Mapped["Faccao | None"] = relationship(back_populates="produtos")  # noqa: F821
    cinturao: Mapped["Cinturao | None"] = relationship(back_populates="replicas")  # noqa: F821


class Pedido(CriadoEmMixin, Base):
    __tablename__ = "pedido"
    __table_args__ = (
        CheckConstraint(_in("status", STATUS_PEDIDO), name="ck_pedido_status"),
        CheckConstraint("valor_total >= 0", name="ck_pedido_valor_total"),
        Index("ix_pedido_usuario_id", "usuario_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="aguardando_pagamento"
    )
    valor_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    usuario: Mapped["Usuario"] = relationship(back_populates="pedidos")
    itens: Mapped[list["ItemPedido"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )


class ItemPedido(Base):
    __tablename__ = "item_pedido"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_item_pedido_quantidade"),
        CheckConstraint("preco_unitario > 0", name="ck_item_pedido_preco_unitario"),
        Index("ix_item_pedido_pedido_id", "pedido_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedido.id", ondelete="CASCADE"), nullable=False
    )
    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produto.id", ondelete="RESTRICT"), nullable=False
    )
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    # Preço praticado no momento da compra: mudar o produto depois não altera o pedido.
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    pedido: Mapped["Pedido"] = relationship(back_populates="itens")
    produto: Mapped["Produto"] = relationship()
