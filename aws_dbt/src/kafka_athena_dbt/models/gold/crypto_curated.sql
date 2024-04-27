{{
    config(
        materialized='view',
        alias='crypto_curated',
        unique_key='id',
        merge_behavior='upsert'

    )
}}

with ranked_data as (
    select 
        id,
        symbol,
        name,
        price,
        date_and_time,
        dense_rank() OVER (partition by id ORDER BY date_and_time DESC) AS ranking
    from crypto_analytics.crypto_stage
)

select 
    id,
    symbol,
    name,
    price,
    date_and_time
from ranked_data
where ranking = 1
