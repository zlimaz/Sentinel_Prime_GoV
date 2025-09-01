import logging
from datetime import datetime, timezone

# Importando nossas funções dos módulos que criamos
from src.coletores.coleta_senado import fetch_senado_news
from src.coletores.coleta_camara import fetch_camara_news
from src.analisador.analisador_noticias import prune_old_posted_articles, filter_new_articles
from src.formatadores.formatador_noticias import format_news_thread

# Importando funções do código já existente
from src.api_client import post_tweet
from src.main import load_json, save_json # Reutilizando as funções de carregar/salvar estado

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

STATE_FILE = 'estado.json'

def main():
    logging.info("--- Iniciando ciclo do Bot de Notícias ---")

    # 1. Carregar e limpar o estado
    state = load_json(STATE_FILE) or {}
    posted_news_list = state.get('posted_news', [])
    pruned_posted_news = prune_old_posted_articles(posted_news_list)
    state['posted_news'] = pruned_posted_news

    # 2. Buscar notícias de todas as fontes
    logging.info("Buscando notícias das fontes...")
    all_news = fetch_senado_news() + fetch_camara_news()
    # Ordena por garantia, embora feeds RSS já costumem ser cronológicos
    # (Assumindo que o feedparser popula uma data que pode ser usada para ordenar, ex: entry.published_parsed)
    # Para simplificar, vamos confiar na ordem do feed por enquanto.

    # 3. Filtrar apenas as notícias novas
    new_articles = filter_new_articles(all_news, state['posted_news'])

    # 4. Verificar se há algo para postar
    if not new_articles:
        logging.info("Nenhuma notícia nova para postar. Encerrando o ciclo.")
        return

    # 5. Selecionar a notícia mais recente e formatar
    # A primeira da lista é a mais recente
    article_to_post = new_articles[0]
    logging.info(f"Notícia selecionada para postagem: {article_to_post['title']}")
    
    thread_content = format_news_thread(article_to_post)

    # 6. Postar a thread no X
    logging.info("Postando a thread de notícia no X...")
    last_tweet_id = None
    post_successful = True
    for tweet in thread_content:
        last_tweet_id = post_tweet(tweet, reply_to_id=last_tweet_id)
        if not last_tweet_id:
            logging.error("Falha ao postar um dos tweets da notícia. Abortando.")
            post_successful = False
            break

    # 7. Atualizar e salvar o estado se a postagem foi bem-sucedida
    if post_successful:
        logging.info("Postagem da notícia concluída com sucesso.")
        newly_posted_item = {
            'link': article_to_post['link'],
            'posted_at': datetime.now(timezone.utc).isoformat()
        }
        state['posted_news'].append(newly_posted_item)
        save_json(state, STATE_FILE)
        logging.info("Estado atualizado com a nova notícia postada.")
    else:
        logging.error("A postagem da thread de notícia falhou. O estado não foi alterado.")

    logging.info("--- Ciclo do Bot de Notícias finalizado ---")

if __name__ == "__main__":
    main()
