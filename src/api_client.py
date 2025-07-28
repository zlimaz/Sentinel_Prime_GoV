import requests
import datetime

def get_deputies_list():
    """Busca a lista de todos os deputados em exercício."""
    url = "https://dadosabertos.camara.leg.br/api/v2/deputados?ordem=ASC&ordenarPor=nome"
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()["dados"]
    except requests.RequestException as e:
        print(f"Erro ao buscar lista de deputados: {e}")
        return []

def get_deputy_expenses(deputy_id, months=3):
    """Busca todas as despesas de um deputado nos últimos X meses."""
    all_expenses = []
    today = datetime.date.today()
    # Itera pelos meses para fazer buscas mais focadas e evitar timeouts
    for i in range(months):
        target_date = today - datetime.timedelta(days=i * 30)
        url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{deputy_id}/despesas"
        params = {
            "ano": target_date.year,
            "mes": target_date.month,
            "itens": 100,
            "pagina": 1
        }
        headers = {"Accept": "application/json"}
        
        # Loop de paginação para o mês corrente
        page_url = url
        while page_url:
            try:
                response = requests.get(page_url, headers=headers, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                all_expenses.extend(data["dados"])
                
                next_link = next((link["href"] for link in data["links"] if link["rel"] == "next"), None)
                page_url = next_link
                params = {} # Params só são necessários na primeira requisição
            except requests.RequestException as e:
                # Silenciosamente ignora erros de um mês específico para não parar o processo todo
                # print(f"Aviso: Falha ao buscar despesas para o deputado {deputy_id} no mês {target_date.month}/{target_date.year}: {e}")
                break
    return all_expenses
