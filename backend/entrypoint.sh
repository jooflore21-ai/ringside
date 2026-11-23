#!/bin/sh
set -e

echo "1/3 Aplicando migrations (alembic upgrade head)..."
alembic upgrade head

echo "2/3 Carregando dados iniciais (seed)..."
python -m app.seed

echo "3/3 Subindo a API em http://localhost:8000 (docs em /docs)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
