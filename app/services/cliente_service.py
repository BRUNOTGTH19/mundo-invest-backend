import logging

from app.repositories.cliente_repo import ClienteRepository
from app.schemas import ClienteCreate, ClienteResponse
from app.pipefy.mutations import MUTATION_CREATE_CARD

logger = logging.getLogger(__name__)


class ClienteService:
    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def criar_cliente(self, dados: ClienteCreate) -> ClienteResponse:
        cliente = self.repo.criar(dados)

        # Montar mutation que seria enviada ao Pipefy (simulação)
        # Em produção: POST https://api.pipefy.com/graphql com Authorization: Bearer <token>
        mutation = MUTATION_CREATE_CARD.format(
            nome=cliente.nome,
            email=cliente.email,
            patrimonio=cliente.valor_patrimonio,
        )
        # A mutation é apenas logada internamente — não exposta na resposta HTTP
        logger.info("[Pipefy][simulação] mutation createCard para %s:\n%s", cliente.email, mutation)

        return ClienteResponse.model_validate(cliente)