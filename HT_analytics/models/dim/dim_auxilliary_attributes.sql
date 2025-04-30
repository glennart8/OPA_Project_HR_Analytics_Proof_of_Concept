WITH aux as (SELECT * FROM {{ref ('src_auxilliary_attributes')}})

select 
    {{dbt_utils.generate_surrogate_key(['id'])}} as auxilliary_attributes_id,
    experience_required,
    driver_license,
    access_to_own_car
FROM aux