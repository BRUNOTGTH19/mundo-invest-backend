from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ClienteCreate, ClienteResponse
from app.repositories.cliente_repo import ClienteRepository
from app.services.cliente_service import ClienteService

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=ClienteResponse, status_code=201)
def criar_cliente(payload: ClienteCreate, db: Session = Depends(get_db)):
    repo = ClienteRepository(db)
    service = ClienteService(repo)
    try:
        cliente, mutation = service.criar_cliente(payload)
        # A mutation retornada não é exposta ao cliente, apenas logada/processada
        return cliente
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))