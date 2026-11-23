FROM node:20-alpine

WORKDIR /app

# Dependências primeiro, para o Docker reaproveitar o cache.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173

# --host expõe o servidor do Vite para fora do contêiner.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
