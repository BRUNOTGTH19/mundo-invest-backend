from app.repositories.cliente_repo import ClienteRepository
from app.schemas import ClienteCreate, ClienteResponse
from app.pipefy.mutations import MUTATION_CREATE_CARD

class ClienteService:
    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def criar_cliente(self, dados: ClienteCreate) -> tuple[ClienteResponse, str]:
        cliente = self.repo.criar(dados)
        # Simulação: montamos a mutation que seria enviada ao Pipefy
        mutation = MUTATION_CREATE_CARD.format(
            nome=cliente.nome,
            email=cliente.email,
            patrimonio=cliente.valor_patrimonio
        )
        # Em produção, aqui faríamos uma requisição HTTP para a API do Pipefy
        return ClienteResponse.model_validate(cliente), mutation