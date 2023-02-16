from fastapi import FastAPI, Query, Depends, HTTPException
from datetime import date
import query_od_parameters
import db
import h3
from authorization import access_control

app = FastAPI()

start_date_query = Query(
    default = ...,
    example = "2023-02-14",
    title = "Start date"
)
end_date_query = Query(
    default = ...,
    example = "2023-02-14",
    title = "End date"
)
days_of_week_query = Query(
    default = None, 
    regex = "^((mo|tu|we|th|fr|sa|su),?)*$",
    title = "Days of week",
    example = "mo,tu,we,th,fr",
    description = "The days of the week that should be included. "
    + "For example: mo,tu,we,th,fr to query only weekdays. " 
    + "Leaving empty will result in including all days of the week."
)
time_periods_query = Query(
    default = None, 
    regex = "^((2-6|6-10|10-14|14-18|18-22|22-2),?)*$",
    example = "2-6,6-10",
    title = "Time periods",
    description = "The time periods of the day that should be included. "
    + "For example: 2-6,6-10 will return all od's with trips starting between 2 and 10 o'clock. " 
    + "Leaving empty will result in including all time periods."
)
h3_resolution_query = Query(
    default = ...,
    regex = "^(7|8)$",
    example = 7,
    title = "h3 resolution",
    description = "h3 zoom level data should be received, 7 and 8 are allowed values.",
)
modalities_query = Query(
    default = None, 
    regex = "^((bicycle|moped|car|scooter|cargo_bicycle|unknown),?)*$",
    example = "bicycle,moped",
    title = "Modalities that should be included",
    description = "The modalities that should be included. "
    + "For example: bicycle,moped will return all od's for trips with bicycle or moped." 
    + "Leaving empty will result in including all modalities."
)
destination_cells_query = Query(
    default = ...,
    regex = "^(([a-z,0-9]{15}),?)*$",
    example = "87196bb56ffffff,87196bb57ffffff",
    title = "Destination cells",
    description = "Specify destination cells you want to receive origin from."
)
origin_cells_query = Query(
    default = ...,
    regex = "^(([a-z,0-9]{15}),?)*$",
    example = "87196bb56ffffff,87196bb57ffffff",
    title = "Origin cells",
    description = "Specify origin cells you want to receive destinations from."
)

def serialize_od_h3_result(results):
    res = []
    for result in results:
        result["cell"] = h3.h3_to_string(result["cell"])
        res.append(result)
    return res

@app.get("/origins/h3")
async def get_origins(
    start_date: date | None = start_date_query,
    end_date: date | None = end_date_query,
    days_of_week: str | None = days_of_week_query,
    time_periods: str | None = time_periods_query,
    h3_resolution: str | None = h3_resolution_query,
    modalities: str | None = modalities_query,
    destination_cells: str | None = destination_cells_query,
    current_user: access_control.User = Depends(access_control.get_current_user)
):    
    if not current_user.acl.is_admin:
        raise HTTPException(403, "This user is not authorized to receive this information")
    query_od_parameter = query_od_parameters.prepare_query(
        start_date = start_date,
        end_date = end_date,
        days_of_week = days_of_week,
        time_periods = time_periods,
        h3_resolution = h3_resolution,
        modalities = modalities,
        destination_cells = destination_cells
    )
    result = db.query_origins(query_od_parameter)
    return {
        "result": {
            "destinations": serialize_od_h3_result(result)
        } 
    }

@app.get("/destinations/h3")
async def get_destinations( 
    start_date: date | None = start_date_query,
    end_date: date | None = end_date_query,
    days_of_week: str | None = days_of_week_query,
    time_periods: str | None = time_periods_query,
    h3_resolution: str | None = h3_resolution_query,
    modalities: str | None = modalities_query,
    origin_cells: str | None = origin_cells_query,
    current_user: access_control.User = Depends(access_control.get_current_user)
):
    if not current_user.acl.is_admin:
        raise HTTPException(403, "This user is not authorized to receive this information")
    query_od_parameter = query_od_parameters.prepare_query(
        start_date = start_date,
        end_date = end_date,
        days_of_week = days_of_week,
        time_periods = time_periods,
        h3_resolution = h3_resolution,
        modalities = modalities,
        origin_cells = origin_cells,
    )
    result = db.query_destinations(query_od_parameter)
    return {
        "result": {
            "destinations": serialize_od_h3_result(result)
        }  
    }

@app.get("/matrix/h3")
async def get_matrix():
    return {"message": "Hello World"}