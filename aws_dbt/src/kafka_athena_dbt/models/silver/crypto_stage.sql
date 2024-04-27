{{
    config(
        materialized='incremental',
        alias='crypto_stage',
        format='parquet',
        unique_key='id'
    )
}}

select 
    id,
    symbol,
    name,
    price,
    date_and_time
from
    {{ ref('crypto_raw') }} t

{% if is_incremental() %}
where
    t.date_and_time > (select max(date_and_time) from {{this}} )
{% endif %}

