{% snapshot crypto_price_snapshot %}
    {{
        config(
            target_schema='crypto_snapshots',
            unique_key='id',
            strategy='timestamp',
            updated_at='date_and_time'
        )
    }}

    select
        id,
        symbol,
        name,
        price,
        date_and_time
    from {{ ref('crypto_stage') }}

{% endsnapshot %}
