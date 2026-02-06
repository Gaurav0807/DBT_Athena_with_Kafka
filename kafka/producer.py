from kafka import KafkaProducer
import requests
import json
import time

class CryptoDataProducer:
    def __init__(self, bootstrap_servers, kafka_topic):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.api_url_list = 'https://api.coingecko.com/api/v3/coins/list'
        self.api_url_info = 'https://api.coingecko.com/api/v3/coins'
        self.kafka_topic = kafka_topic

    def fetch_crypto_ids(self):
        response = requests.get(self.api_url_list)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch crypto IDs. Status Code: {response.status_code}")
            return None

    def fetch_crypto_data(self, crypto_info):
        crypto_id = crypto_info['id']
        url = f"{self.api_url_info}/{crypto_id}"
        params = {'localization': 'false', 'tickers': 'false', 'market_data': 'true', 'community_data': 'true', 'developer_data': 'false'}
        
        # Retry logic for rate limits
        retries = 5
        for attempt in range(retries):
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                symbol = data.get('symbol', '')
                name = data.get('name', '')
                price = data.get('market_data', {}).get('current_price', {}).get('usd', 0)
                last_updated = data.get('market_data', {}).get('last_updated', '')
                commits = data.get('developer_data', {}).get('forks', 0)  # Assuming forks represent commits
                return {'id': crypto_id, 'symbol': symbol, 'name': name, 'price': price, 'last_updated': last_updated, 'commits': commits}
            elif response.status_code == 429:
                print(f"Rate limit exceeded. Waiting for {response.headers.get('Retry-After')} seconds.")
                time.sleep(int(response.headers.get('Retry-After', 10)))  # Wait for the suggested duration
            else:
                print(f"Failed to fetch data for {crypto_id}. Status Code: {response.status_code}")
                return None

    def produce_crypto_data(self):
        crypto_infos = self.fetch_crypto_ids()
        
        if crypto_infos:
            for crypto_info in crypto_infos:
                crypto_data = self.fetch_crypto_data(crypto_info)
                if crypto_data:
                    self.producer.send(self.kafka_topic, value=crypto_data)
                    print(f"Sent crypto data to Kafka: {crypto_info['id']}")

                time.sleep(1)  # Add a small delay to avoid rate limiting

if __name__ == "__main__":
    # Define your Kafka configuration
    bootstrap_servers = 'localhost:9092'
    kafka_topic = 'selected_crypto_data'

    # Create an instance of CryptoDataProducer
    crypto_producer = CryptoDataProducer(bootstrap_servers, kafka_topic)

    # Start producing crypto data to Kafka
    crypto_producer.produce_crypto_data()

    