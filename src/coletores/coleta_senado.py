import feedparser
import logging
import requests

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SENADO_NEWS_RSS_URL = "https://www12.senado.leg.br/noticias/rss/agencia"

# Cabeçalho para simular um navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_senado_news():
    """
    Busca as últimas notícias do feed RSS da Agência Senado.

    Retorna:
        list: Uma lista de dicionários, onde cada dicionário representa uma notícia
              com as chaves 'title', 'link' e 'summary'.
              Retorna uma lista vazia em caso de erro.
    """
    logging.info(f"Buscando notícias do feed: {SENADO_NEWS_RSS_URL}")
    try:
        # Usando requests para buscar o conteúdo com headers
        response = requests.get(SENADO_NEWS_RSS_URL, headers=HEADERS, timeout=15)
        response.raise_for_status() # Lança exceção para status de erro (4xx ou 5xx)

        # Passando o conteúdo para o feedparser
        feed = feedparser.parse(response.content)

        if feed.bozo:
            # feed.bozo é 1 se o feed estiver malformado
            logging.error(f"O feed RSS está malformado. Causa: {feed.bozo_exception}")
            return []

        news_list = []
        for entry in feed.entries:
            news_item = {
                'title': entry.title,
                'link': entry.link,
                'summary': entry.summary
            }
            news_list.append(news_item)
        
        logging.info(f"{len(news_list)} notícias encontradas no feed do Senado.")
        return news_list

    except requests.RequestException as e:
        logging.error(f"Falha ao fazer a requisição para o feed do Senado: {e}")
        return []
    except Exception as e:
        logging.error(f"Falha ao analisar o feed de notícias do Senado: {e}")
        return []

# Bloco para teste direto do script
if __name__ == '__main__':
    print("--- Testando o coletor de notícias do Senado ---")
    latest_news = fetch_senado_news()
    if latest_news:
        print(f"\nEncontradas {len(latest_news)} notícias.")
        print("\n--- Exemplo da primeira notícia encontrada ---")
        print(f"Título: {latest_news[0]['title']}")
        print(f"Link: {latest_news[0]['link']}")
        print(f"Resumo: {latest_news[0]['summary']}")
        print("-" * 50)
    else:
        print("Nenhuma notícia foi encontrada ou ocorreu um erro.")
