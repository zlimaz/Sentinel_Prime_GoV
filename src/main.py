import datetime
from dotenv import load_dotenv
from src.api_client import SentinelAPIClient

load_dotenv()

def get_state(client, key):
    res = client.db.table("bot_state").select("value").eq("key", key).execute()
    return res.data[0]["value"] if res.data else None

def save_state(client, key, value):
    client.db.table("bot_state").upsert({"key": key, "value": value}).execute()

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

    if datetime.datetime.now().weekday() == 0:
        queue = get_state(client, "ranking_queue")
        if not queue: generate_ranking(client)

    queue = get_state(client, "ranking_queue")
    if queue:
        deputy = queue.pop()
        if client.post_tweet_thread(format_tweet(deputy, len(queue) + 1)) not in ["rate_limit", None]:
            save_state(client, "ranking_queue", queue)

if __name__ == "__main__":
    main()
