with stg_auxilliary_attributes as (select * from "job_ads"."staging"."job_ads")

select  
        -- id_aux, -- hittar på ett id
        -- id,
        experience_required,
        driving_license_required as driver_license,
        access_to_own_car

from stg_auxilliary_attributes