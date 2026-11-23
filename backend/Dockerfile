FROM python:3.12-slim

WORKDIR /app

# Instala as dependências antes de copiar o código: o Docker reaproveita
# essa camada em cache enquanto o requirements.txt não mudar.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Migrations -> seed -> servidor. Ver entrypoint.sh.
CMD ["sh", "entrypoint.sh"]
