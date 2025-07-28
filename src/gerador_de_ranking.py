import json
import time
from src.api_client import get_deputies_list, get_deputy_expenses

RANKING_FILE = 'ranking_gastos.json'

def calculate_total_spent(expenses):
    """Calcula o valor líquido total de uma lista de despesas."""
    return sum(expense['valorLiquido'] for expense in expenses)

def main():
    """Gera e salva um ranking de deputados por gastos totais."""
    print("Iniciando a geração do ranking de gastos. Este processo pode levar vários minutos...")
    
    deputies = get_deputies_list()
    if not deputies:
        print("Não foi possível obter a lista de deputados. Encerrando.")
        return

    ranked_list = []
    total_deputies = len(deputies)
    start_time = time.time()

    for i, deputy in enumerate(deputies):
        deputy_id = deputy['id']
        deputy_name = deputy['nome']
        
        # Imprime o progresso para o usuário
        print(f"Processando [{i+1}/{total_deputies}]: {deputy_name}...", end="", flush=True)
        
        expenses = get_deputy_expenses(deputy_id)
        total_spent = calculate_total_spent(expenses)
        
        if total_spent > 0:
            ranked_list.append({
                "id": deputy_id,
                "nome": deputy_name,
                "siglaPartido": deputy['siglaPartido'],
                "siglaUf": deputy['siglaUf'],
                "total_gasto": total_spent
            })
        print(f" Total: R$ {total_spent:,.2f}")

    # Ordena a lista final do maior para o menor gasto
    ranked_list.sort(key=lambda x: x['total_gasto'], reverse=True)

    # Salva o ranking no arquivo
    project_dir = '/home/zlimaz/Documentos/Projeto-Sentinela/'
    with open(project_dir + RANKING_FILE, 'w') as f:
        json.dump(ranked_list, f, indent=2, ensure_ascii=False)

    end_time = time.time()
    duration = end_time - start_time
    print("\nRanking gerado e salvo com sucesso!")
    print(f"Foram processados {len(ranked_list)} deputados com gastos no período.")
    print(f"Duração total: {duration:.2f} segundos.")

if __name__ == "__main__":
    main()
