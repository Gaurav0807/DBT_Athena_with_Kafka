drop table crypto_analytics.crypto_raw_data;

CREATE EXTERNAL TABLE IF NOT EXISTS crypto_analytics.crypto_raw_data (
  id STRING,
  symbol STRING,
  name STRING,
  price DOUBLE,
  last_updated STRING,
  commits INT
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
)
LOCATION 's3://aws-dbt-kafka-demo-bucket/crypto_data/';