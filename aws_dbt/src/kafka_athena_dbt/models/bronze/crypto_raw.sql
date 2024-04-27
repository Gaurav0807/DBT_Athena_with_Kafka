{{
    config(
        materialized='incremental',
        alias='crypto_raw',
        format='parquet',
        unique_key='id'
    )
}}

select 
    id,
    symbol,
    name,
    price,
   DATE_FORMAT(DATE_PARSE(last_updated, '%Y-%m-%dT%H:%i:%S.%fZ'), '%Y-%m-%d %H:%i:%S') AS date_and_time
from
    {{ var('external_schema')}}.crypto_raw_data