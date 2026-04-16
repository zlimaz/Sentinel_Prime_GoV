import datetime
import logging
from dotenv import load_dotenv
from src.api_client import SentinelAPIClient
from main_noticias import run_news_bot

load_dotenv()

def get_state(client, key):
    try:
        res = client.db.table("bot_state").select("value").eq("key", key).execute()
        return res.data[0]["value"] if res.data else None
    except Exception: return None

def save_state(client, key, value):
    try:
        client.db.table("bot_state").upsert({"key": key, "value": value}).execute()
    except Exception: pass

def generate_ranking(client):
    start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).date().isoformat()
    try:
        res = client.db.rpc("get_top_spenders", {"start_date": start_date, "limit_count": 10}).execute()
        if res.data:
            queue = res.data[::-1]
            save_state(client, "ranking_queue", queue)
            return queue
    except Exception: pass
    return []

def format_tweet(deputy, position):
    emojis = {1: "🥇", 2: "🥈", 3: "🥉", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"}
    emoji = emojis.get(position, "📊")
    return [
        f"{emoji} RANKING SEMANAL: {position}º Lugar\n\n"
        f"Parlamentar: {deputy['nome']} ({deputy['sigla_partido']}-{deputy['sigla_uf']})\n"
        f"Gastos na última semana: R$ {float(deputy['total_gasto']):,.2f}\n\n"
        f"Dados da cota parlamentar. #ProjetoSentinela #Transparencia",
        f"🔍 Fiscalize você também: Notas fiscais disponíveis no portal da Câmara.\n\n"
        f"A transparência é o primeiro passo para o voto consciente em 2026. 🇧🇷"
    ]

def main():
    client = SentinelAPIClient()
    if not client.db: return

    # 1. VERIFICAÇÃO DE NOTÍCIAS
    print("--- Verificando Notícias ---")
    postou_noticia = run_news_bot()
    
    if postou_noticia:
        print("Ciclo finalizado com postagem de notícia.")
        return
    else:
        print("Nenhuma notícia postada neste ciclo.")

    # 2. VERIFICAÇÃO DE RANKING
    print("\n--- Verificando Fila de Ranking ---")
    if datetime.datetime.now().weekday() == 0:
        queue = get_state(client, "ranking_queue")
        if not queue: generate_ranking(client)

    queue = get_state(client, "ranking_queue")
    if queue:
        deputy = queue.pop()
        pos = len(queue) + 1
        print(f"Tentando postar ranking: {deputy['nome']} ({pos}º lugar)")
        status = client.post_tweet_thread(format_tweet(deputy, pos))
        if status not in ["rate_limit", None]:
            save_state(client, "ranking_queue", queue)
            print("Postagem de ranking concluída com sucesso.")
    else:
        print("Fila de ranking vazia ou não é dia de gerar ranking.")

if __name__ == "__main__":
    main()
