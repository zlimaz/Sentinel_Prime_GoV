import requests
import datetime
import json
from collections import defaultdict

STATE_FILE = 'estado.json'

def load_state():
    """Carrega o índice do último deputado processado."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Se o arquivo não existe, cria um no diretório do projeto
        project_dir = '/home/zlimaz/Documentos/Projeto-Sentinela/'
        with open(project_dir + STATE_FILE, 'w') as f:
            initial_state = {"last_processed_deputy_index": -1}
            json.dump(initial_state, f)
        return initial_state

def save_state(state):
    """Salva o novo estado (índice do deputado processado)."""
    project_dir = '/home/zlimaz/Documentos/Projeto-Sentinela/'
    with open(project_dir + STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_deputies_list():
    """Busca a lista de todos os deputados em exercício."""
    url = "https://dadosabertos.camara.leg.br/api/v2/deputados?ordem=ASC&ordenarPor=nome"
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()["dados"]
    except requests.RequestException as e:
        print(f"Erro ao buscar deputados: {e}")
        return []

def get_deputy_expenses(deputy_id, months=3):
    """Busca todas as despesas de um deputado, lidando com paginação."""
    today = datetime.date.today()
    # Para garantir que pegamos 3 meses completos, vamos para o primeiro dia do mês inicial
    end_date = today
    start_date = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1) # vai para o mes anterior
    for _ in range(months - 1):
        start_date = (start_date - datetime.timedelta(days=1)).replace(day=1)

    all_expenses = []
    # Itera por cada mês para garantir que a busca seja precisa
    current_month = start_date
    while current_month <= end_date:
        url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{deputy_id}/despesas"
        params = {
            "ano": current_month.year,
            "mes": current_month.month,
            "itens": 100,
            "pagina": 1
        }
        headers = {"Accept": "application/json"}
        
        while url:
            try:
                response = requests.get(url, headers=headers, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                all_expenses.extend(data["dados"])
                
                next_link = next((link["href"] for link in data["links"] if link["rel"] == "next"), None)
                url = next_link
                params = {} # Params só são necessários na primeira requisição da página
            except requests.RequestException as e:
                print(f"Erro ao buscar despesas para o deputado {deputy_id} no mês {current_month.month}/{current_month.year}: {e}")
                # Tenta continuar para o próximo mês mesmo se um falhar
                break 
        
        # Avança para o próximo mês
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            current_month = current_month.replace(month=current_month.month + 1)
            
    return all_expenses

def process_expenses(expenses):
    """Agrupa as despesas por tipo e calcula o total."""
    if not expenses:
        return 0, {}
    total_spent = 0
    grouped_expenses = defaultdict(float)
    for expense in expenses:
        total_spent += expense['valorLiquido']
        # Simplifica nomes de categorias para melhor visualização
        category_name = expense['tipoDespesa'].replace(".", "").strip().title()
        grouped_expenses[category_name] += expense['valorLiquido']
    
    sorted_grouped_expenses = sorted(grouped_expenses.items(), key=lambda item: item[1], reverse=True)
    return total_spent, dict(sorted_grouped_expenses)

def format_tweet(deputy_name, deputy_party, total_spent, grouped_expenses):
    """Formata os dados de despesa em um texto de tweet pronto para postar."""
    
    # Inicia o tweet com as informações principais
    tweet = f"📊 Gastos Parlamentares (Últimos 3 meses)\n\n"
    tweet += f"👤 Deputado(a): {deputy_name} ({deputy_party})\n"
    tweet += f"💰 Total Gasto: R$ {total_spent:,.2f}\n\n"
    tweet += "Principais Despesas:\n"

    # Adiciona as top 3-4 categorias para não exceder o limite de caracteres
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
        if count < 4:
            emoji = emoji_map.get(category, "▪️")
            line = f"{emoji} {category}: R$ {value:,.2f}\n"
            if len(tweet) + len(line) < 270: # Deixa uma margem para hashtags
                tweet += line
                count += 1
            else:
                break
    
    # Adiciona as hashtags
    hashtags = f"\n#ProjetoSentinela #TransparenciaBrasil #Fiscalize #CongressoNacional"
    tweet += hashtags
    
    return tweet

def main():
    print("Iniciando ciclo do Projeto Sentinela...")
    
    state = load_state()
    deputies = get_deputies_list()
    if not deputies:
        print("Não foi possível obter a lista de deputados. Encerrando.")
        return

    current_index = state["last_processed_deputy_index"]
    next_index = (current_index + 1) % len(deputies)
    
    selected_deputy = deputies[next_index]
    deputy_id = selected_deputy["id"]
    deputy_name = selected_deputy["nome"]
    deputy_party = f"{selected_deputy['siglaPartido']}-{selected_deputy['siglaUf']}"

    print(f"\nProcessando: [{next_index + 1}/{len(deputies)}] {deputy_name} ({deputy_party}) - ID: {deputy_id}")
    expenses = get_deputy_expenses(deputy_id)
    total_spent, grouped_expenses = process_expenses(expenses)

    # Gera o texto do tweet
    tweet_text = format_tweet(deputy_name, deputy_party, total_spent, grouped_expenses)

    print("\n" + "="*40)
    print("  Texto do Tweet Gerado (Pronto para Copiar)")
    print("="*40)
    print(tweet_text)
    print("="*40 + "\n")
            
    state["last_processed_deputy_index"] = next_index
    save_state(state)
    print(f"Estado atualizado. Próxima execução começará do deputado de índice: {next_index + 1}")

if __name__ == "__main__":
    main()
