# Mundo Invest — Backend Challenge

API REST desenvolvida em **Python + FastAPI** para gerenciamento de clientes e integração simulada com o **Pipefy** via GraphQL.

---

## Estrutura do projeto

```
mundo-invest-backend/
├── app/
│   ├── main.py              # Entrypoint FastAPI
│   ├── config.py            # Variáveis de ambiente
│   ├── database.py          # Configuração SQLAlchemy / SQLite
│   ├── models.py            # Modelos ORM (Cliente, EventoWebhook)
│   ├── schemas.py           # Schemas Pydantic (request / response)
│   ├── pipefy/
│   │   └── mutations.py     # Mutations GraphQL (createCard, updateCardField)
│   ├── repositories/
│   │   ├── cliente_repo.py  # Acesso a dados — tabela clientes
│   │   └── evento_repo.py   # Acesso a dados — tabela eventos_webhook
│   ├── services/
│   │   ├── cliente_service.py   # Regras de negócio — criação de cliente
│   │   └── webhook_service.py   # Regras de negócio — processamento de webhook
│   └── routers/
│       ├── clientes.py      # Endpoint POST /clientes
│       └── webhooks.py      # Endpoint POST /webhooks/pipefy/card-updated
└── tests/
    ├── conftest.py          # Fixtures pytest (banco SQLite em memória, TestClient)
    ├── test_clientes.py     # Testes do fluxo de criação de cliente
    └── test_webhooks.py     # Testes do fluxo de webhook
```

### Separação de camadas

| Camada | Responsabilidade |
|---|---|
| **Router** | Receber e validar a requisição HTTP, delegar ao service |
| **Service** | Orquestrar regras de negócio e montar a mutation Pipefy |
| **Repository** | Isolar todo acesso ao banco de dados |
| **Pipefy** | Strings GraphQL exatas conforme a documentação oficial |

---

## Como executar localmente

### Pré-requisitos

- Python 3.11+
- pip

### Instalação

```bash
git clone https://github.com/BRUNOTGTH19/mundo-invest-backend.git
cd mundo-invest-backend
pip install -r requirements.txt
```

### Iniciar o servidor

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.  
Documentação interativa: `http://localhost:8000/docs`

---

## Como executar os testes

```bash
pytest tests/ -v
```

Saída esperada: **10 passed**.

Os testes usam um banco SQLite isolado criado e destruído a cada execução — sem efeito colateral no banco de desenvolvimento.

---

## Exemplos de requisição (curl)

### POST /clientes — Criar cliente

```bash
curl -X POST http://localhost:8000/clientes/ \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000
  }'
```

Resposta `201 Created`:

```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao.silva@example.com",
  "tipo_solicitacao": "Atualização cadastral",
  "valor_patrimonio": 250000.0,
  "status": "Aguardando Análise",
  "prioridade": null,
  "criado_em": "2026-05-25T10:00:00Z"
}
```

---

### POST /webhooks/pipefy/card-updated — Simulação de webhook

```bash
curl -X POST http://localhost:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }'
```

Resposta `200 OK` (primeira chamada):

```json
{
  "status": "processed",
  "cliente_id": 1,
  "prioridade": "prioridade_alta"
}
```

Resposta `200 OK` (chamada repetida com mesmo `event_id`):

```json
{
  "status": "ignored",
  "message": "Evento já processado"
}
```

---

## Mutations GraphQL do Pipefy

As mutations foram pesquisadas na documentação oficial do Pipefy:

- `createCard`: https://api-docs.pipefy.com/reference/mutations/createCard/
- `updateCardField`: https://api-docs.pipefy.com/reference/mutations/updateCardField/

Estão estruturadas em `app/pipefy/mutations.py`. Em produção, o envio seria feito via:

```bash
POST https://api.pipefy.com/graphql
Authorization: Bearer <PIPEFY_TOKEN>
Content-Type: application/json
```

A mutation `updateCardField` usa **aliases GraphQL** (`update_status` e `update_prioridade`) para permitir duas chamadas ao mesmo campo no mesmo bloco de mutation — exigência da especificação GraphQL.

---

## Visão de produção na AWS (opcional)

### Arquitetura proposta

```
API Gateway → Lambda (FastAPI via Mangum) → RDS PostgreSQL
                                          → DynamoDB (idempotência)
                                          → SQS → Lambda worker (Pipefy)
```

### Detalhamento

**Recepção de requisições**  
O API Gateway recebe as chamadas HTTP e as encaminha para uma função Lambda que executa a aplicação FastAPI empacotada com [Mangum](https://github.com/jordaneremieff/mangum). Isso elimina a necessidade de gerenciar servidores ou contêineres para um volume inicial moderado.

**Banco de dados**  
O SQLite local seria substituído por **Amazon RDS (PostgreSQL)** em uma subnet privada. Para alta disponibilidade, usa-se Multi-AZ com read replica para relatórios. A string de conexão é injetada via **AWS Secrets Manager**, nunca em variáveis de ambiente diretas.

**Idempotência de webhooks em escala**  
A tabela `eventos_webhook` migraria para **DynamoDB** com `event_id` como partition key e TTL de 30 dias. O DynamoDB oferece latência de um dígito em milissegundos e escala horizontal automática — ideal para verificações de duplicidade em alta frequência.

**Desacoplamento do envio para o Pipefy**  
Em vez de chamar a API do Pipefy de forma síncrona dentro do Lambda do webhook, a Lambda publica a mutation em uma fila **SQS**. Um segundo Lambda worker consome a fila e executa o envio com retry automático. Isso evita que uma instabilidade do Pipefy afete o tempo de resposta da API.

**Escalabilidade**  
Lambda escala automaticamente por invocação concorrente. O gargalo seria o pool de conexões do RDS — mitigável com **RDS Proxy**, que mantém um pool persistente entre as execuções efêmeras do Lambda.

**Observabilidade**  
CloudWatch Logs + métricas customizadas para taxa de webhooks duplicados, tempo de resposta por endpoint e falhas de envio ao Pipefy.