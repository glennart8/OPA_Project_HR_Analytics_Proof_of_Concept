
  
  create view "job_ads"."refined"."dim_employer__dbt_tmp" as (
    with  __dbt__cte__src_employer as (
with stg_employer as (select * from "job_ads"."staging"."job_ads")

select
    employer__name as employer_name,
    employer__workplace as employer_workplace,
    employer__organization_number as employer_organization_number,
    workplace_address__street_address as workplace_street_address,
    workplace_address__region as workplace_region,
    workplace_address__postcode as workplace_postcode,
    workplace_address__city as workplace_city,
    workplace_address__country as workplace_country,
    workplace_address__municipality as workplace_municipality,
from stg_employer
), employer as (select * from __dbt__cte__src_employer)

select 
    md5(cast(coalesce(cast(employer_workplace as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(workplace_municipality as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as employer_id,
    coalesce(employer_name, 'namn ej angiven') as employer_name,
    coalesce(employer_workplace, 'plats ej angiven') as employer_workplace,
    coalesce(employer_organization_number, 'saknar organisationsnummer') as employer_organization_number,
    coalesce(workplace_municipality, 'kommun ej angiven') as workplace_municipality,
    coalesce(workplace_region, 'region ej angiven') as workplace_region,
    coalesce(workplace_country, 'land ej angiven') as workplace_country,
    coalesce(workplace_city, 'stad ej angiven') as workplace_city
from employer
  );
