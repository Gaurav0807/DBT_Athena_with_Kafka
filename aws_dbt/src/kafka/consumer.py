from kafka import KafkaConsumer
import json
from datetime import datetime
import boto3


class CryptoDataConsumer:

    def __init__(self, bootstrap_servers, kafka_topic, s3_bucket_name, s3_folder_name ):

        self.consumer = KafkaConsumer(
            kafka_topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            group_id='crypto_consumer',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.s3_bucket_name = s3_bucket_name
        self.s3_folder_name = s3_folder_name

    
    
    def consume_data(self):
        s3_client = boto3.client('s3')
        for message in self.consumer:
            crypto_data = message.value
            self.store_data_to_s3_bucket(s3_client, crypto_data)

    
    def store_data_to_s3_bucket(self, s3_client, data):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        object_key = f"{self.s3_folder_name}/crypto_data_{timestamp}.json"
        s3_client.put_object(Bucket=self.s3_bucket_name, Key=object_key, Body=json.dumps(data))





if __name__ == "__main__":

    bootstrap_servers = 'localhost:9092'
    kafka_topic = 'selected_crypto_data'
    s3_bucket_name = 'aws-dbt-kafka-demo-bucket'
    s3_folder_name = 'crypto_data'

    crypto_consumer = CryptoDataConsumer(bootstrap_servers=bootstrap_servers,kafka_topic=kafka_topic,
                                         s3_bucket_name=s3_bucket_name,s3_folder_name=s3_folder_name)

    crypto_consumer.consume_data()

