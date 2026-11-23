"""faccoes e cinturoes

Acrescenta facções (grupos de lutadores), cinturões e o histórico de títulos.

- faccao: grupo de lutadores; lutador.faccao_id guarda a facção atual.
- cinturao: título de simples ou de duplas.
- reinado: período em que um cinturão esteve com um campeão (fim nulo = atual).
  Em duplas, a facção é a campeã (reinado.faccao_id).
- reinado_lutador: quem segurava o cinturão naquele reinado. Guarda os membros
  da facção NAQUELE momento, então o título continua no histórico do lutador
  mesmo que ele saia da facção depois.
- luta.cinturao_id: luta valendo título (substitui o tipo 'titulo').
- produto.faccao_id e produto.cinturao_id: merch de facção e réplica de cinturão.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "faccao",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )
    op.create_table(
        "cinturao",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("divisao", sa.String(length=10), server_default="simples", nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("imagem_url", sa.String(length=500), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("divisao IN ('simples', 'duplas')", name="ck_cinturao_divisao"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )
    op.create_table(
        "reinado",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cinturao_id", sa.Integer(), nullable=False),
        sa.Column("faccao_id", sa.Integer(), nullable=True),
        sa.Column("inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fim", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("fim IS NULL OR fim >= inicio", name="ck_reinado_periodo"),
        sa.ForeignKeyConstraint(["cinturao_id"], ["cinturao.id"], name="fk_reinado_cinturao", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["faccao_id"], ["faccao.id"], name="fk_reinado_faccao", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    # Só um campeão atual por cinturão: índice único PARCIAL (só linhas com fim nulo).
    op.create_index(
        "uq_reinado_atual_por_cinturao", "reinado", ["cinturao_id"],
        unique=True, postgresql_where=sa.text("fim IS NULL"),
    )
    op.create_table(
        "reinado_lutador",
        sa.Column("reinado_id", sa.Integer(), nullable=False),
        sa.Column("lutador_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["reinado_id"], ["reinado.id"], name="fk_reinado_lutador_reinado", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lutador_id"], ["lutador.id"], name="fk_reinado_lutador_lutador", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("reinado_id", "lutador_id"),
    )
    # "Títulos de um lutador" busca por lutador_id; a PK composta começa por reinado_id.
    op.create_index("ix_reinado_lutador_lutador_id", "reinado_lutador", ["lutador_id"])

    op.add_column("lutador", sa.Column("faccao_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_lutador_faccao", "lutador", "faccao", ["faccao_id"], ["id"], ondelete="RESTRICT")

    # Luta valendo título passa a ser indicada pelo cinturão, não pelo tipo.
    op.add_column("luta", sa.Column("cinturao_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_luta_cinturao", "luta", "cinturao", ["cinturao_id"], ["id"], ondelete="RESTRICT")
    op.execute("UPDATE luta SET tipo = 'simples' WHERE tipo = 'titulo'")
    op.drop_constraint("ck_luta_tipo", "luta", type_="check")
    op.create_check_constraint("ck_luta_tipo", "luta", "tipo IN ('simples', 'duplas', 'triple_threat')")

    op.add_column("produto", sa.Column("faccao_id", sa.Integer(), nullable=True))
    op.add_column("produto", sa.Column("cinturao_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_produto_faccao", "produto", "faccao", ["faccao_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_produto_cinturao", "produto", "cinturao", ["cinturao_id"], ["id"], ondelete="RESTRICT")
    op.drop_constraint("ck_produto_evento_ou_lutador", "produto", type_="check")
    op.create_check_constraint(
        "ck_produto_um_vinculo", "produto",
        "num_nonnulls(evento_id, lutador_id, faccao_id, cinturao_id) <= 1",
    )


def downgrade() -> None:
    op.drop_constraint("ck_produto_um_vinculo", "produto", type_="check")
    op.create_check_constraint(
        "ck_produto_evento_ou_lutador", "produto", "evento_id IS NULL OR lutador_id IS NULL"
    )
    op.drop_constraint("fk_produto_cinturao", "produto", type_="foreignkey")
    op.drop_constraint("fk_produto_faccao", "produto", type_="foreignkey")
    op.drop_column("produto", "cinturao_id")
    op.drop_column("produto", "faccao_id")

    op.drop_constraint("ck_luta_tipo", "luta", type_="check")
    op.create_check_constraint(
        "ck_luta_tipo", "luta", "tipo IN ('simples', 'duplas', 'triple_threat', 'titulo')"
    )
    # Devolve a informação de "luta valendo título" para o tipo antigo.
    op.execute("UPDATE luta SET tipo = 'titulo' WHERE cinturao_id IS NOT NULL")
    op.drop_constraint("fk_luta_cinturao", "luta", type_="foreignkey")
    op.drop_column("luta", "cinturao_id")

    op.drop_constraint("fk_lutador_faccao", "lutador", type_="foreignkey")
    op.drop_column("lutador", "faccao_id")

    op.drop_index("ix_reinado_lutador_lutador_id", table_name="reinado_lutador")
    op.drop_table("reinado_lutador")
    op.drop_index("uq_reinado_atual_por_cinturao", table_name="reinado")
    op.drop_table("reinado")
    op.drop_table("cinturao")
    op.drop_table("faccao")
