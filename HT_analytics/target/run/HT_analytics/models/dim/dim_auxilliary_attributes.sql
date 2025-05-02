
  
  create view "job_ads"."refined"."dim_auxilliary_attributes__dbt_tmp" as (
    WITH  __dbt__cte__src_auxilliary_attributes as (
with stg_auxilliary_attributes as (select * from "job_ads"."staging"."job_ads")

select  
        -- id_aux, -- hittar på ett id
        id,
        experience_required,
        driving_license_required as driver_license,
        access_to_own_car

from stg_auxilliary_attributes
), aux as (SELECT * FROM __dbt__cte__src_auxilliary_attributes)

select 
    -- md5(cast(coalesce(cast(id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as auxilliary_attributes_id,
    md5(cast(coalesce(cast(experience_required as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(driver_license as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(access_to_own_car as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as id_aux,
    experience_required,
    driver_license,
    access_to_own_car
FROM aux
  );
