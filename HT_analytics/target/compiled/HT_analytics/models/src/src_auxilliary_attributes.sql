with stg_job_ads as (select * from "job_ads"."staging"."job_ads")

select
    id, -- För att övrig info
    experience_required,
    driving_license_required as driving_license,
    access_to_own_car

from stg_job_ads