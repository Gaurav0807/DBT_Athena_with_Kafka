{% test no_duplicate_ids(model, column_name) %}
    /*
    Specific test for dbt models
    */
    select {{ column_name }}, count(*) as count
    from {{ model }}
    where date_and_time >= current_date - interval '1' day
    group by {{ column_name }}
    having count(*) > 1
{% endtest %}