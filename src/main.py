import requests
import datetime
from pprint import pprint


def get_deputies_list():
    url = "https://dadosabertos.camara.leg.br/api/v2/deputados?ordem=ASC&ordenarPor=nome"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["dados"]
    else:
        print(f"Erro ao buscar deputados: {response.status_code}")
        return []


def get_deputy_expenses(deputy_id, months=3):
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=months * 30)

    # A API espera o ano e o mês em listas
    year_months = set()
    current_date = start_date
    while current_date <= today:
        year_months.add((current_date.year, current_date.month))
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    years = [str(ym[0]) for ym in year_months]
    months = [str(ym[1]) for ym in year_months]

    url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{deputy_id}/despesas"
    params = {
        "ano": years,
        "mes": months,
        "ordem": "DESC",
        "ordenarPor": "dataDocumento",
        "itens": 100,  
    }
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()["dados"]
    else:
        print(f"Erro ao buscar despesas para o deputado {deputy_id}: {response.status_code}")
        return []


def main():
    print("Iniciando Projeto Sentinela...")
    deputies = get_deputies_list()
    if not deputies:
        return

    sample_deputy = deputies[0]
    deputy_id = sample_deputy["id"]
    deputy_name = sample_deputy["nome"]

    print(f"\nBuscando despesas para: {deputy_name} (ID: {deputy_id})")
    expenses = get_deputy_expenses(deputy_id)

    if expenses:
        print(f"\nÚltimas despesas encontradas (até 100):")
        total_spent = 0
        for expense in expenses:
            total_spent += expense['valorLiquido']
            print(
                f"- Data: {expense['dataDocumento']} | "
                f"Tipo: {expense['tipoDespesa']} | "
                f"Valor: R$ {expense['valorLiquido']:.2f}"
            )
        
        print(f"\nTotal gasto nos últimos 3 meses (nos itens listados): R$ {total_spent:.2f}")
    else:
        print("Nenhuma despesa encontrada no período.")


if __name__ == "__main__":
    main()