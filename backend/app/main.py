from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.rotas import rotas_saude
from app.core.config import obter_settings
from app.core.erros import registrar_handlers

app = FastAPI(
    title="Ringside API",
    description="Loja de ingressos e merch de uma promoção de wrestling.",
    version="0.1.0",
)

# CORS liberado só para a origem do front-end, como o trabalho exige.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[obter_settings().frontend_origem],
    allow_credentials=False,  # token vai no cabeçalho Authorization, não em cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_handlers(app)

app.include_router(rotas_saude.router)
