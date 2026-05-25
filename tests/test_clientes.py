def test_criar_cliente_valido(client):
    """Criação com payload válido deve retornar 201 e status inicial correto."""
    payload = {
        "cliente_nome": "João Silva",
        "cliente_email": "joao@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250000,
    }
    response = client.post("/clientes/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "João Silva"
    assert data["email"] == "joao@example.com"
    assert data["status"] == "Aguardando Análise"
    assert data["prioridade"] is None
    assert "id" in data
    assert "criado_em" in data


def test_criar_cliente_email_invalido(client):
    """E-mail inválido deve retornar 422."""
    payload = {
        "cliente_nome": "Teste",
        "cliente_email": "nao_e_um_email",
        "tipo_solicitacao": "Novo",
        "valor_patrimonio": 100000,
    }
    response = client.post("/clientes/", json=payload)
    assert response.status_code == 422


def test_criar_cliente_campo_obrigatorio_faltando(client):
    """Payload sem campo obrigatório deve retornar 422."""
    payload = {
        "cliente_nome": "Teste",
        "tipo_solicitacao": "Novo",
        "valor_patrimonio": 100000,
        # cliente_email ausente
    }
    response = client.post("/clientes/", json=payload)
    assert response.status_code == 422


def test_criar_cliente_mutation_nao_exposta(client):
    """A resposta da API não deve vazar detalhes internos de integração."""
    payload = {
        "cliente_nome": "Segura",
        "cliente_email": "segura@example.com",
        "tipo_solicitacao": "Novo",
        "valor_patrimonio": 150000,
    }
    response = client.post("/clientes/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "mutation" not in data
    assert "pipefy" not in str(data).lower()