"""Módulo para interagir com as APIs da Câmara dos Deputados e do X (Twitter)."""
import os
import datetime
import requests
import tweepy


def get_deputies_list():
    """
    Busca a lista de todos os deputados em exercício.

    Retorna:
        list: Uma lista de dicionários, onde cada dicionário representa um deputado.
              Retorna uma lista vazia em caso de erro.
    """
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
    """
    Busca todas as despesas de um deputado nos últimos X meses.

    Args:
        deputy_id (int): O ID do deputado.
        months (int): O número de meses para buscar as despesas (padrão: 3).

    Retorna:
        list: Uma lista de dicionários, onde cada dicionário representa uma despesa.
              Retorna uma lista vazia em caso de erro.
    """
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
                response = requests.get(page_url, headers=headers,
                                        params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                all_expenses.extend(data["dados"])

                next_link = next((link["href"] for link in data["links"]
                                  if link["rel"] == "next"), None)
                page_url = next_link
                params = {}  # Params só são necessários na primeira requisição
            except requests.RequestException:
                break
    return all_expenses


def post_tweet(text, reply_to_id=None):
    """
    Posta um tweet no X (Twitter).

    Args:
        text (str): O texto do tweet.
        reply_to_id (str, optional): O ID do tweet ao qual este tweet está respondendo.
                                     Padrão é None.

    Retorna:
        str: O ID do tweet postado, "duplicate" se o conteúdo for duplicado, ou None em caso de outro erro.
    """
    try:
        api_key = os.environ.get("X_API_KEY")
        api_secret = os.environ.get("X_API_SECRET")
        access_token = os.environ.get("X_ACCESS_TOKEN")
        access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")

        if not all([api_key, api_secret, access_token, access_token_secret]):
            print("Erro: As credenciais da API do X não foram encontradas "
                  "nas variáveis de ambiente.")
            return None

        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        response = client.create_tweet(text=text, in_reply_to_tweet_id=reply_to_id)
        tweet_id = response.data['id']
        print(f"Tweet postado com sucesso: {tweet_id}")
        return tweet_id
    except tweepy.TweepyException as e:
        if "duplicate content" in str(e):
            print("Aviso: Conteúdo de tweet duplicado. Marcando como tratado para não repetir.")
            return "duplicate"
        
        print(f"Erro ao postar tweet: {e}")
        return None
