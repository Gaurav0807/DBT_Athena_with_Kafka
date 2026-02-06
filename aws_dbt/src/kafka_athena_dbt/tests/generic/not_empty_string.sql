{% test not_empty_string(model, column_name) %}
    /*
    Generic test related to specific dbt models
    */
    select *
    from {{ model }}
    where {{ column_name }} = '' or {{ column_name }} is null
{% endtest %}
