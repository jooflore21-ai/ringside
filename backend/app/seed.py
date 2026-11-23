"""Carga inicial: 1 admin, 3 categorias, 15 produtos, 2 eventos, 5 lutadores,
2 facções, 2 cinturões e o histórico de reinados.

Idempotente: se o admin já existe, não faz nada. Assim rodar
`docker compose up` várias vezes não duplica dados.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal

from sqlalchemy import select

from app.core.config import obter_settings
from app.core.seguranca import gerar_hash
from app.db.sessao import SessaoLocal
from app.models import (
    Categoria, Cinturao, Evento, Faccao, Luta, Lutador, Participante, Produto, Reinado,
    ReinadoLutador, Usuario,
)


FUSO = ZoneInfo("America/Sao_Paulo")


def _data(texto: str) -> datetime:
    # Horários pensados no fuso de Brasília; o banco guarda com fuso (TIMESTAMPTZ).
    return datetime.fromisoformat(texto).replace(tzinfo=FUSO)


def executar() -> None:
    s = obter_settings()
    with SessaoLocal() as sessao, sessao.begin():
        if sessao.scalar(select(Usuario).where(Usuario.email == s.admin_email)):
            print("   Seed já aplicado, nada a fazer.")
            return

        sessao.add(Usuario(nome="Booker", email=s.admin_email,
                           senha_hash=gerar_hash(s.admin_senha), papel="admin"))

        ingressos, camisetas, colecionaveis = (
            Categoria(nome="Ingressos"), Categoria(nome="Camisetas"), Categoria(nome="Colecionáveis"))
        sessao.add_all([ingressos, camisetas, colecionaveis])

        # Facções: o Bando do Corvo (vilões) e a Irmandade do Oeste (mocinhos).
        bando = Faccao(nome="Bando do Corvo", descricao="Chegam juntos, batem juntos, fogem juntos.")
        irmandade = Faccao(nome="Irmandade do Oeste", descricao="Honra, chimarrão e cadeirada.")
        sessao.add_all([bando, irmandade])

        # Taylor Skinner já foi da Irmandade e saiu: hoje não tem facção (faccao=None),
        # mas o título de duplas que ganhou com ela continua no histórico dele.
        skinner = Lutador(nome_ringue="Taylor Skinner", alinhamento="face",
                          bio="O campeão brasileiro mais jovem da história.")
        corvo = Lutador(nome_ringue="Corvo Negro", alinhamento="heel", faccao=bando,
                        bio="Ninguém sabe de onde ele veio.")
        caos = Lutador(nome_ringue="Doutor Caos", alinhamento="heel", faccao=bando,
                       bio="Diploma falso, golpes reais.")
        aco = Lutador(nome_ringue="Gaúcho de Aço", alinhamento="face", faccao=irmandade,
                      bio="Força bruta e chimarrão.")
        peao = Lutador(nome_ringue="Peão Bravo", alinhamento="face", faccao=irmandade,
                       bio="Entrou na Irmandade no lugar de Taylor Skinner.")
        sessao.add_all([skinner, corvo, caos, aco, peao])

        principal = Cinturao(nome="Cinturão Ringside", divisao="simples",
                             descricao="O título principal da promoção.")
        duplas = Cinturao(nome="Cinturão de Duplas Ringside", divisao="duplas",
                          descricao="Disputado por facções.")
        sessao.add_all([principal, duplas])

        def reinado(cinturao, campeoes, inicio, fim=None, faccao=None):
            r = Reinado(cinturao=cinturao, faccao=faccao, inicio=_data(inicio),
                        fim=_data(fim) if fim else None)
            r.campeoes = [ReinadoLutador(lutador=l) for l in campeoes]
            return r

        sessao.add_all([
            # Simples: Corvo Negro foi campeão; Taylor Skinner é o atual.
            reinado(principal, [corvo], "2026-03-14T21:00", "2026-08-22T21:30"),
            reinado(principal, [skinner], "2026-08-22T21:30"),
            # Duplas: a facção é a campeã; reinado_lutador guarda quem estava nela.
            reinado(duplas, [skinner, aco], "2026-01-10T20:00", "2026-06-06T22:00", faccao=irmandade),
            reinado(duplas, [corvo, caos], "2026-06-06T22:00", faccao=bando),
        ])

        noite = Evento(nome="Noite do Ringside", data_hora=_data("2026-12-12T20:00"),
                       local="Ginásio Municipal, Chapecó")
        guerra = Evento(nome="Guerra no Oeste", data_hora=_data("2027-02-20T19:30"),
                        local="Centro de Eventos, Maravilha")
        sessao.add_all([noite, guerra])
        sessao.flush()  # gera os ids para usar nas lutas

        luta1 = Luta(evento=noite, ordem=1, tipo="simples")
        luta1.participantes = [Participante(lutador=aco), Participante(lutador=caos)]
        # Luta valendo título: o cinturão é informado em cinturao.
        luta2 = Luta(evento=noite, ordem=2, tipo="simples", cinturao=principal)
        luta2.participantes = [Participante(lutador=skinner), Participante(lutador=corvo)]
        luta3 = Luta(evento=guerra, ordem=1, tipo="duplas", cinturao=duplas)
        luta3.participantes = [Participante(lutador=l) for l in (aco, peao, corvo, caos)]
        luta4 = Luta(evento=guerra, ordem=2, tipo="triple_threat")
        luta4.participantes = [Participante(lutador=l) for l in (skinner, aco, caos)]
        sessao.add_all([luta1, luta2, luta3, luta4])

        def p(nome, preco, estoque, categoria, **extra):
            return Produto(nome=nome, preco=Decimal(preco), estoque=estoque, categoria=categoria, **extra)

        sessao.add_all([
            # 6 ingressos: cada setor de cada evento é um produto
            p("Ringside — Noite do Ringside", "180.00", 2, ingressos, evento=noite),
            p("Cadeira — Noite do Ringside", "90.00", 60, ingressos, evento=noite),
            p("Arquibancada — Noite do Ringside", "40.00", 200, ingressos, evento=noite),
            p("Ringside — Guerra no Oeste", "200.00", 20, ingressos, evento=guerra),
            p("Cadeira — Guerra no Oeste", "100.00", 80, ingressos, evento=guerra),
            p("Arquibancada — Guerra no Oeste", "45.00", 300, ingressos, evento=guerra),
            # 5 camisetas
            p("Camiseta Taylor Skinner", "89.90", 25, camisetas, lutador=skinner),
            p("Camiseta Corvo Negro", "79.90", 15, camisetas, lutador=corvo),
            p("Camiseta Gaúcho de Aço", "79.90", 0, camisetas, lutador=aco),  # esgotada de propósito
            p("Camiseta Doutor Caos", "79.90", 12, camisetas, lutador=caos),
            p("Camiseta Bando do Corvo", "84.90", 20, camisetas, faccao=bando),
            # 4 colecionáveis
            p("Réplica do Cinturão Ringside", "450.00", 3, colecionaveis, cinturao=principal),
            p("Pôster autografado Taylor Skinner", "59.90", 10, colecionaveis, lutador=skinner),
            p("Máscara do Corvo Negro", "120.00", 5, colecionaveis, lutador=corvo),
            p("Caneca Ringside", "39.90", 30, colecionaveis),
        ])
    print("   Seed aplicado: 1 admin, 3 categorias, 15 produtos, 2 eventos, 5 lutadores, "
              "2 facções, 2 cinturões, 4 reinados.")


if __name__ == "__main__":
    executar()
