from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.sessao import obter_sessao

router = APIRouter(tags=["saúde"])


@router.get("/saude", summary="Verifica se a API e o banco estão no ar")
def saude(sessao: Session = Depends(obter_sessao)) -> dict:
    sessao.execute(text("SELECT 1"))
    return {"api": "ok", "banco": "ok"}
