from sqlalchemy.orm import Session
from app.models import Cliente
from app.schemas import ClienteCreate

class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, dados: ClienteCreate) -> Cliente:
        cliente = Cliente(
            nome=dados.cliente_nome,
            email=dados.cliente_email,
            tipo_solicitacao=dados.tipo_solicitacao,
            valor_patrimonio=dados.valor_patrimonio,
            status="Aguardando Análise"
        )
        self.db.add(cliente)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente

    def buscar_por_email(self, email: str) -> Cliente | None:
        return self.db.query(Cliente).filter(Cliente.email == email).first()

    def atualizar_status_prioridade(self, cliente: Cliente, status: str, prioridade: str):
        cliente.status = status
        cliente.prioridade = prioridade
        self.db.commit()
        self.db.refresh(cliente)