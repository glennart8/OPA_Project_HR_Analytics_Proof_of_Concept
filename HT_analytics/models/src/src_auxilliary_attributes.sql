with stg_auxilliary_attributes as (select * from {{ source('job_ads', 'stg_ads') }})

select  
        id, -- hittar på ett id
        experience_required,
        driving_license_required as driver_license,
        access_to_own_car

from stg_auxilliary_attributes
