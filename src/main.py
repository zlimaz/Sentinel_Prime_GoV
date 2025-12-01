"""Módulo principal para o Projeto Sentinela."""
import json
import time
from collections import defaultdict
from dotenv import load_dotenv

from src.api_client import get_deputy_expenses, post_tweet

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

STATE_FILE = 'estado.json'
RANKING_FILE = 'ranking_gastos.json'


def load_json(file_path):
    """Carrega um arquivo JSON."""
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def save_json(data, file_path):
    """Salva dados em um arquivo JSON."""
    with open(file_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def process_expenses(expenses):
    """
    Processa uma lista de despesas para calcular o total gasto,
    agrupar despesas por categoria e identificar a maior despesa única.
    """
    if not expenses:
        return 0, {}, None

    total_spent = 0
    grouped_expenses = defaultdict(float)
    largest_single_expense = {"valorLiquido": 0}

    for expense in expenses:
        total_spent += expense['valorLiquido']
        category_name = expense['tipoDespesa'].replace(".", "").strip().title()
        grouped_expenses[category_name] += expense['valorLiquido']

        if expense['valorLiquido'] > largest_single_expense['valorLiquido']:
            largest_single_expense = expense

    sorted_grouped_expenses = sorted(grouped_expenses.items(),
                                     key=lambda item: item[1],
                                     reverse=True)
    return total_spent, dict(sorted_grouped_expenses), largest_single_expense


def generate_thread_content(deputy_id, deputy_name, deputy_party,
                            total_spent, grouped_expenses, largest_expense):
    """
    Gera o conteúdo da thread para postagem no X (Twitter)
    com base nos dados de gastos do deputado.
    """
    tweet1 = (f"📊 Gastos Parlamentares: R$ {total_spent:,.2f}\n\n"
              f"Deputado(a): {deputy_name} ({deputy_party}) utilizou este valor "
              "da cota parlamentar nos últimos 3 meses.\n\n"
              "👇 Siga o fio para ver os detalhes e as fontes.\n\n"
              "#ProjetoSentinela #TransparenciaBrasil #Fiscalize #Governo #GastosPúblicos")

    tweet2 = "🧵 Detalhes dos Gastos:\n\n"
    emoji_map = {
        "Divulgação Da Atividade Parlamentar": "📢",
        "Combustíveis E Lubrificantes": "⛽",
        "Passagem Aérea - Sigepa": "✈️",
        "Manutenção De Escritório De Apoio À Atividade Parlamentar": "🏢",
        "Locação Ou Fretamento De Veículos Automotores": "🚗",
        "Telefonia": "📱",
        "Serviços Postais": "✉️"
    }
    count = 0
    for category, value in grouped_expenses.items():
        if count < 5:
            emoji = emoji_map.get(category, "▪️")
            line = f"{emoji} {category}: R$ {value:,.2f}\n"
            if len(tweet2) + len(line) < 280:
                tweet2 += line
                count += 1

    tweet3 = ""
    if largest_expense and largest_expense['valorLiquido'] > 0:
        valor = largest_expense['valorLiquido']
        fornecedor = largest_expense['nomeFornecedor'].title()
        tweet3 += (f"✨ Destaque: O maior gasto único foi de R$ {valor:,.2f} "
                   f"com \"{fornecedor}\".\n\n")

    deputy_page_url = f"https://www.camara.leg.br/deputados/{deputy_id}"
    tweet3 += (f"🔍 Fonte Oficial: Confira todos os gastos e notas fiscais no "
               f"portal da Câmara:\n{deputy_page_url}")

    return [tweet1, tweet2, tweet3]


def main():
    """Função principal que orquestra a execução do bot."""
    print("Iniciando ciclo do Projeto Sentinela...")

    state = load_json(STATE_FILE) or {"last_processed_deputy_index": -1}
    ranking = load_json(RANKING_FILE)

    if not ranking:
        print("Arquivo de ranking não encontrado. "
              "Por favor, execute o gerador_de_ranking.py primeiro.")
        return

    current_index = state["last_processed_deputy_index"]
    next_index = (current_index + 1) % len(ranking)

    selected_deputy = ranking[next_index]
    deputy_id = selected_deputy["id"]
    deputy_name = selected_deputy["nome"]
    deputy_party = f"{selected_deputy['siglaPartido']}-{selected_deputy['siglaUf']}"

    print(f"\nProcessando do Ranking: [Posição {next_index + 1}/{len(ranking)}] "
          f"{deputy_name} ({deputy_party})")
    expenses = get_deputy_expenses(deputy_id)
    total_spent, grouped_expenses, largest_expense = process_expenses(expenses)

    thread_content = generate_thread_content(deputy_id, deputy_name,
                                             deputy_party, total_spent,
                                             grouped_expenses, largest_expense)

    print("\n" + "="*50)
    print("  Conteúdo da Thread Gerado para Postagem")
    print("="*50)
    for i, tweet in enumerate(thread_content):
        print(f"\n--- TWEET {i+1}/3 ---\n{tweet}")
    print("\n" + "="*50 + "\n")

    print("Postando no X...")
    last_tweet_id = None
    post_result = "success"  # "success", "duplicate", ou "failure"

    for i, tweet in enumerate(thread_content):
        response = post_tweet(tweet, reply_to_id=last_tweet_id)

        if response == "duplicate":
            post_result = "duplicate"
            break  # Interrompe a postagem desta thread

        if not response:
            post_result = "failure"
            break  # Interrompe em caso de outra falha

        last_tweet_id = response
        print(f"Tweet {i+1}/{len(thread_content)} postado: {last_tweet_id}")
        time.sleep(5)  # Pausa para evitar limite de taxa

    # Lógica de atualização de estado
    if post_result == "failure":
        print(f"Postagem falhou para {deputy_name}. "
              "O estado não será atualizado para tentar novamente.")
    else:
        if post_result == "success":
            print(f"Postagem concluída para {deputy_name}.")
        elif post_result == "duplicate":
            print("Postagem pulada: conteúdo duplicado.")

        state["last_processed_deputy_index"] = next_index
        save_json(state, STATE_FILE)
        print("Estado atualizado. Próxima execução começará da posição: "
              f"{next_index + 1}")


if __name__ == "__main__":
    main()

