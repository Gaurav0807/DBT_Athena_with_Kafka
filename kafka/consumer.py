from kafka import KafkaConsumer
import json
from datetime import datetime
import boto3
import os
import time
import signal
import sys
import logging

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CryptoDataConsumer:

    def __init__(self, bootstrap_servers, kafka_topic, s3_bucket_name, s3_folder_name,
                 batch_size=100):

        self.consumer = KafkaConsumer(
            kafka_topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            group_id='crypto_consumer',
            enable_auto_commit=False,   # manual commit for reliability
            max_poll_records=500,
            fetch_min_bytes=1048576,     # 1 MB
            fetch_max_wait_ms=500,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        self.s3_bucket_name = s3_bucket_name
        self.s3_folder_name = s3_folder_name
        self.batch_size = batch_size
        self.batch = []

        # Boto3 will automatically pick creds from env / IAM role
        self.s3_client = boto3.client("s3", region_name="us-east-1")

        self.running = True
        
        # Metrics tracking
        self.messages_consumed = 0
        self.batches_uploaded = 0
        self.upload_errors = 0
        self.start_time = datetime.utcnow()
        self.cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

    def consume_data(self):
        logger.info("🚀 Kafka consumer started...")

        try:
            for message in self.consumer:
                if not self.running:
                    break

                crypto_data = message.value
                self.batch.append(crypto_data)
                self.messages_consumed += 1

                if len(self.batch) >= self.batch_size:
                    self.flush_to_s3()
                    self.consumer.commit()
                    
                    # Log progress every batch
                    logger.info(f"Progress: {self.messages_consumed} messages consumed, "
                               f"{self.batches_uploaded} batches uploaded")

        except Exception as e:
            logger.error(f"❌ Error while consuming data: {e}")

        finally:
            self.shutdown()

    def flush_to_s3(self):
        if not self.batch:
            return

        now = datetime.utcnow()
        partition_path = (
            f"{self.s3_folder_name}/"
            f"year={now.year}/month={now.month:02d}/day={now.day:02d}"
        )

        object_key = f"{partition_path}/crypto_data_{now.strftime('%H-%M-%S')}.json"
        batch_size = len(self.batch)

        try:
            start_time = time.time()
            self.s3_client.put_object(
                Bucket=self.s3_bucket_name,
                Key=object_key,
                Body=json.dumps(self.batch)
            )
            upload_time = time.time() - start_time
            self.batches_uploaded += 1
            
            logger.info(f"✅ Uploaded {batch_size} records to s3://{self.s3_bucket_name}/{object_key} "
                       f"(took {upload_time:.2f}s)")
            self.batch.clear()
            
            # Publish metrics to CloudWatch
            self.publish_metrics(batch_size, upload_time)

        except Exception as e:
            logger.error(f"❌ Failed to upload batch to S3: {e}")
            self.upload_errors += 1
            # Do NOT clear batch on failure (retry possible)

    def shutdown(self):
        logger.info("🛑 Shutting down consumer...")

        try:
            self.flush_to_s3()
            self.consumer.commit()
        except Exception as e:
            logger.warning(f"⚠️ Error during shutdown: {e}")

        # Calculate and log final metrics
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        throughput = self.messages_consumed / uptime if uptime > 0 else 0
        
        logger.info(f"=== Consumer Statistics ===")
        logger.info(f"Total messages consumed: {self.messages_consumed}")
        logger.info(f"Total batches uploaded: {self.batches_uploaded}")
        logger.info(f"Upload errors: {self.upload_errors}")
        logger.info(f"Uptime: {uptime:.2f}s")
        logger.info(f"Throughput: {throughput:.2f} messages/sec")

        self.consumer.close()
        logger.info("✅ Consumer closed cleanly.")

    def stop(self, *args):
        self.running = False

    def publish_metrics(self, batch_size, upload_time):
        """Publish metrics to CloudWatch"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace='CryptoDataPipeline',
                MetricData=[
                    {
                        'MetricName': 'BatchSize',
                        'Value': batch_size,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'UploadDuration',
                        'Value': upload_time,
                        'Unit': 'Seconds',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
        except Exception as e:
            logger.warning(f"Failed to publish metrics to CloudWatch: {e}")


if __name__ == "__main__":

    bootstrap_servers = "localhost:9092"
    kafka_topic = "selected_crypto_data"
    s3_bucket_name = "gaurav-hudi-data"
    s3_folder_name = "crypto_data"

    consumer = CryptoDataConsumer(
        bootstrap_servers=bootstrap_servers,
        kafka_topic=kafka_topic,
        s3_bucket_name=s3_bucket_name,
        s3_folder_name=s3_folder_name,
        batch_size=100
    )

    # Graceful shutdown on Ctrl+C
    signal.signal(signal.SIGINT, consumer.stop)
    signal.signal(signal.SIGTERM, consumer.stop)

    consumer.consume_data()
