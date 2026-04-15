import logging
import sys
import datetime
from src.coletores.coleta_senado import fetch_senado_news
from src.coletores.coleta_camara import fetch_camara_news
from src.coletores.coleta_stf import fetch_stf_news
from src.coletores.coleta_tse import fetch_tse_news
from src.coletores.coleta_agenciabrasil import fetch_agenciabrasil_news
from src.analisador.analisador_noticias import prune_old_posted_articles, filter_new_articles
from src.formatadores.formatador_noticias import format_news_thread
from src.api_client import SentinelAPIClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_posted(client):
    res = client.db.table("bot_state").select("value").eq("key", "posted_news").execute()
    return res.data[0]["value"] if res.data else []

def run_news_bot():
    """Executa o fluxo de notícias. Retorna True se postou algo."""
    client = SentinelAPIClient()
    if not client.db: return False

    history = prune_old_posted_articles(get_posted(client))
    news = (fetch_senado_news() + fetch_camara_news() + fetch_stf_news() + 
            fetch_tse_news() + fetch_agenciabrasil_news())

    new_items = filter_new_articles(news, history)
    if not new_items:
        client.db.table("bot_state").upsert({"key": "posted_news", "value": history}).execute()
        return False

    target = new_items[0]
    logging.info(f"Postando notícia: {target['title']}")
    status = client.post_tweet_thread(format_news_thread(target))
    
    if status not in ["rate_limit", "duplicate", None]:
        history.append({
            'link': target['link'],
            'posted_at': datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        client.db.table("bot_state").upsert({"key": "posted_news", "value": history}).execute()
        return True
    
    return False

def main():
    run_news_bot()

if __name__ == "__main__":
    main()