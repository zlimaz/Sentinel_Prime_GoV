import os
import datetime
import random
import time
import requests
import tweepy
from tweepy.errors import TooManyRequests, TweepyException
from supabase import create_client, Client

class SentinelAPIClient:
    def __init__(self):
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "SentinelPrimeGov/1.0 (Bot; OpenSource; Transparencia Publica)"
        }
        
        sb_url = os.environ.get("SUPABASE_URL")
        sb_key = os.environ.get("SUPABASE_SERVICE_KEY")
        self.db: Client = create_client(sb_url, sb_key) if sb_url and sb_key else None
        self.x_client = self._init_x_client()

    def _init_x_client(self):
        try:
            return tweepy.Client(
                consumer_key=os.environ.get("X_API_KEY"),
                consumer_secret=os.environ.get("X_API_SECRET"),
                access_token=os.environ.get("X_ACCESS_TOKEN"),
                access_token_secret=os.environ.get("X_ACCESS_TOKEN_SECRET"),
                wait_on_rate_limit=True
            )
        except Exception as e:
            print(f"Erro X Client: {e}")
            return None

    def get_deputies_list(self):
        all_deputies = []
        url = "https://dadosabertos.camara.leg.br/api/v2/deputados?ordem=ASC&ordenarPor=nome&itens=100"
        
        while url:
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                all_deputies.extend(data["dados"])
                url = next((link["href"] for link in data["links"] if link["rel"] == "next"), None)
            except Exception:
                break
        return all_deputies

    def get_deputy_expenses(self, deputy_id, year=None, month=None):
        now = datetime.datetime.now()
        url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{deputy_id}/despesas"
        params = {"ano": year or now.year, "mes": month or now.month, "itens": 100}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            return response.json().get("dados", []) if response.status_code == 200 else []
        except Exception:
            return []

    def post_tweet_thread(self, tweets):
        if not self.x_client:
            return None

        last_id = None
        for i, text in enumerate(tweets):
            try:
                if i > 0:
                    time.sleep(random.uniform(10, 30))

                response = self.x_client.create_tweet(text=text, in_reply_to_tweet_id=last_id)
                last_id = response.data['id']
                print(f"Postado: {last_id}")
            
            except TooManyRequests:
                return "rate_limit"
            except TweepyException as e:
                if "duplicate content" in str(e).lower():
                    return "duplicate"
                return None
        return last_id
