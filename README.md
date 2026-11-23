# Ringside — loja de ingressos e merch de wrestling

Trabalho final de Desenvolvimento de Aplicações Web (UNOCHAPECÓ).
Loja virtual full-stack de uma promoção de wrestling fictícia: o fã compra
ingressos e produtos; o administrador (Booker) gerencia eventos, lutadores,
produtos, estoque e pedidos.

## Stack

| Camada | Tecnologia |
| --- | --- |
| Banco | PostgreSQL 16 + migrations com Alembic |
| Back-end | Python, FastAPI, Pydantic, SQLAlchemy 2.0 |
| Front-end | React + Vite, Material UI, React Router, Axios |
| Infra | Docker Compose (db + api + web) |

## Como rodar

```bash
cp .env.example .env      # depois troque as senhas e a JWT_SECRET
docker compose up --build
```

| Endereço | O que é |
| --- | --- |
| http://localhost:5173 | Front-end |
| http://localhost:8000/docs | Documentação da API (Swagger) |
| http://localhost:8000/saude | API e banco no ar |

O banco fica acessível na sua máquina pela porta **5433** (DBeaver/pgAdmin), para não colidir com um PostgreSQL já instalado.

Ao subir, a API aplica as migrations e roda o seed (1 admin, 3 categorias,
15 produtos, 2 eventos, 4 lutadores). O login do admin é o `ADMIN_EMAIL` /
`ADMIN_SENHA` do `.env`.

Recomeçar do zero (apaga o banco): `docker compose down -v && docker compose up --build`

## Estrutura

```
backend/
  app/
    api/rotas/     rotas (só traduzem HTTP)
    schemas/       DTOs Pydantic de entrada e saída
    servicos/      regras de negócio
    repositorios/  acesso a dados
    models/        tabelas SQLAlchemy
    core/          config, segurança (bcrypt/JWT), erros RFC 9457
    db/            conexão e sessão por requisição
    seed.py        carga inicial
  alembic/versions migrations
frontend/
  src/
    api/           cliente Axios
    contexts/      AuthContext e CarrinhoContext
    components/    componentes reutilizáveis
    pages/         telas
docs/              modelo lógico e DER
```

## Fluxo de trabalho no Git

- `main` sempre funcionando.
- Cada funcionalidade numa branch `feature/...`, unida por Pull Request.
- Commits pequenos e descritivos.
