"""Camada do tema: evento, lutador, facção, luta, participante, cinturão e reinados."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CriadoEmMixin

ALINHAMENTOS = ("face", "heel")
TIPOS_LUTA = ("simples", "duplas", "triple_threat")
DIVISOES = ("simples", "duplas")


def _in(coluna: str, valores: tuple[str, ...]) -> str:
    lista = ", ".join(f"'{v}'" for v in valores)
    return f"{coluna} IN ({lista})"


class Evento(CriadoEmMixin, Base):
    __tablename__ = "evento"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    local: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    lutas: Mapped[list["Luta"]] = relationship(
        back_populates="evento", cascade="all, delete-orphan", order_by="Luta.ordem"
    )
    ingressos: Mapped[list["Produto"]] = relationship(back_populates="evento")  # noqa: F821


class Lutador(CriadoEmMixin, Base):
    __tablename__ = "lutador"
    __table_args__ = (
        CheckConstraint(_in("alinhamento", ALINHAMENTOS), name="ck_lutador_alinhamento"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_ringue: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    alinhamento: Mapped[str] = mapped_column(String(10), nullable=False, server_default="face")
    bio: Mapped[str | None] = mapped_column(Text)
    foto_url: Mapped[str | None] = mapped_column(String(500))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    # Facção atual (só a atual; o histórico que importa é o de títulos, em reinado_lutador).
    faccao_id: Mapped[int | None] = mapped_column(ForeignKey("faccao.id", ondelete="RESTRICT"))

    faccao: Mapped["Faccao | None"] = relationship(back_populates="membros")
    produtos: Mapped[list["Produto"]] = relationship(back_populates="lutador")  # noqa: F821
    participacoes: Mapped[list["Participante"]] = relationship(back_populates="lutador")


class Luta(Base):
    __tablename__ = "luta"
    __table_args__ = (
        CheckConstraint(_in("tipo", TIPOS_LUTA), name="ck_luta_tipo"),
        CheckConstraint("ordem > 0", name="ck_luta_ordem"),
        # Duas lutas não ocupam a mesma posição no card do evento.
        UniqueConstraint("evento_id", "ordem", name="uq_luta_evento_ordem"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(
        ForeignKey("evento.id", ondelete="CASCADE"), nullable=False
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, server_default="simples")
    # Preenchido = luta valendo esse cinturão.
    cinturao_id: Mapped[int | None] = mapped_column(ForeignKey("cinturao.id", ondelete="RESTRICT"))

    evento: Mapped["Evento"] = relationship(back_populates="lutas")
    cinturao: Mapped["Cinturao | None"] = relationship(back_populates="lutas")
    participantes: Mapped[list["Participante"]] = relationship(
        back_populates="luta", cascade="all, delete-orphan"
    )


class Participante(Base):
    """Tabela associativa N:N com chave primária composta."""

    __tablename__ = "participante"

    luta_id: Mapped[int] = mapped_column(
        ForeignKey("luta.id", ondelete="CASCADE"), primary_key=True
    )
    lutador_id: Mapped[int] = mapped_column(
        ForeignKey("lutador.id", ondelete="RESTRICT"), primary_key=True
    )

    luta: Mapped["Luta"] = relationship(back_populates="participantes")
    lutador: Mapped["Lutador"] = relationship(back_populates="participacoes")


class Faccao(CriadoEmMixin, Base):
    """Grupo de lutadores (stable). Pode deter cinturões de duplas."""

    __tablename__ = "faccao"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    logo_url: Mapped[str | None] = mapped_column(String(500))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    membros: Mapped[list["Lutador"]] = relationship(back_populates="faccao")
    produtos: Mapped[list["Produto"]] = relationship(back_populates="faccao")  # noqa: F821
    reinados: Mapped[list["Reinado"]] = relationship(back_populates="faccao")


class Cinturao(CriadoEmMixin, Base):
    __tablename__ = "cinturao"
    __table_args__ = (CheckConstraint(_in("divisao", DIVISOES), name="ck_cinturao_divisao"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    divisao: Mapped[str] = mapped_column(String(10), nullable=False, server_default="simples")
    descricao: Mapped[str | None] = mapped_column(Text)
    imagem_url: Mapped[str | None] = mapped_column(String(500))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    reinados: Mapped[list["Reinado"]] = relationship(
        back_populates="cinturao", order_by="Reinado.inicio"
    )
    lutas: Mapped[list["Luta"]] = relationship(back_populates="cinturao")
    replicas: Mapped[list["Produto"]] = relationship(back_populates="cinturao")  # noqa: F821


class Reinado(Base):
    """Período em que um cinturão esteve com um campeão. fim nulo = reinado atual."""

    __tablename__ = "reinado"
    __table_args__ = (
        CheckConstraint("fim IS NULL OR fim >= inicio", name="ck_reinado_periodo"),
        # Só um reinado em aberto (campeão atual) por cinturão: índice único parcial.
        Index(
            "uq_reinado_atual_por_cinturao", "cinturao_id",
            unique=True, postgresql_where=text("fim IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cinturao_id: Mapped[int] = mapped_column(
        ForeignKey("cinturao.id", ondelete="RESTRICT"), nullable=False
    )
    # Preenchido em cinturão de duplas: a facção é a campeã.
    faccao_id: Mapped[int | None] = mapped_column(ForeignKey("faccao.id", ondelete="RESTRICT"))
    inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fim: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    cinturao: Mapped["Cinturao"] = relationship(back_populates="reinados")
    faccao: Mapped["Faccao | None"] = relationship(back_populates="reinados")
    campeoes: Mapped[list["ReinadoLutador"]] = relationship(
        back_populates="reinado", cascade="all, delete-orphan"
    )


class ReinadoLutador(Base):
    """Lutadores que detinham o cinturão naquele reinado.

    Em simples é um lutador; em duplas, os membros da facção NAQUELE momento.
    Assim o título fica no histórico do lutador mesmo se ele sair da facção.
    """

    __tablename__ = "reinado_lutador"
    __table_args__ = (Index("ix_reinado_lutador_lutador_id", "lutador_id"),)

    reinado_id: Mapped[int] = mapped_column(
        ForeignKey("reinado.id", ondelete="CASCADE"), primary_key=True
    )
    lutador_id: Mapped[int] = mapped_column(
        ForeignKey("lutador.id", ondelete="RESTRICT"), primary_key=True
    )

    reinado: Mapped["Reinado"] = relationship(back_populates="campeoes")
    lutador: Mapped["Lutador"] = relationship()
