{% test price_in_range(model, column_name, min_value=0, max_value=1000000) %}
    /*
    Generic test related to specific dbt models
    */
    select *
    from {{ model }}
    where {{ column_name }} < {{ min_value }} or {{ column_name }} > {{ max_value }}
{% endtest %}
