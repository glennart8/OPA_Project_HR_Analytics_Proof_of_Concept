with stg_auxilliary_attributes as (select * from "job_ads"."staging"."job_ads")

select  
<<<<<<< HEAD
=======
        -- id_aux, -- hittar på ett id
        -- id,
>>>>>>> 06b84b6770a2b987bd1fe052c4f1d270650950ba
        experience_required,
        driving_license_required as driver_license,
        access_to_own_car

from stg_auxilliary_attributes