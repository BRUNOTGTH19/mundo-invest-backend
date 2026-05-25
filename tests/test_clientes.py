def test_criar_cliente_valido(client):
    payload = {
        "cliente_nome": "João Silva",
        "cliente_email": "joao@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250000
    }
    response = client.post("/clientes/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "João Silva"
    assert data["email"] == "joao@example.com"
    assert data["status"] == "Aguardando Análise"
    assert data["prioridade"] is None