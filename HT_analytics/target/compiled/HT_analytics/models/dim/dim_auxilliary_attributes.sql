WITH  __dbt__cte__src_auxilliary_attributes as (
with stg_auxilliary_attributes as (select * from "job_ads"."staging"."job_ads")

select  
        id, -- hittar på ett id
        experience_required,
        driving_license_required as driver_license,
        access_to_own_car

from stg_auxilliary_attributes
), aux as (SELECT * FROM __dbt__cte__src_auxilliary_attributes)

select 
    md5(cast(coalesce(cast(id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as auxilliary_attributes_id,
    experience_required,
    driver_license,
    access_to_own_car
FROM aux