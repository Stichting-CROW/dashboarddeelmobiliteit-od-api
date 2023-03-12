from fastapi import FastAPI, Query, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import date
import query_od_parameters
import db
import h3
from acl import get_acl, acl
import accessible_h3
import accessible_geometry

app = FastAPI()

@app.middleware("http")
async def authorize(request: Request, call_next):
    result = get_acl.get_access(request=request)
    if not result:
        return JSONResponse(status_code=401, content={"reason": "user is not authorized"})
    request.state.acl = result
    response = await call_next(request)
    return response

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
destination_stat_refs_query = Query(
    default = ...,
    example = "cbs:WK059916,cbs:WK059917,cbs:WK059927,cbs:WK059901",
    title = "Destination stat_refs",
    description = "Specify destination stat_refs want to receive destinations from, currently only residential_areas (wijken) are supported."

)
origin_stat_refs_query = Query(
    default = ...,
    example = "cbs:WK059916,cbs:WK059917,cbs:WK059927,cbs:WK059901",
    title = "Origin cells",
    description = "Specify origin stat_refs want to receive destinations from, currently only residential_areas (wijken) are supported."
)

def serialize_od_h3_result(results):
    res = []
    for result in results:
        result["cell"] = h3.h3_to_string(result["cell"])
        res.append(result)
    return res

def serialize_od_geometry_result(results):
    res = []
    for result in results:
        result["cell"] = h3.h3_to_string(result["cell"])
        res.append(result)
    return res

@app.get("/origins/h3")
async def get_origins_h3(
    request: Request,
    start_date: date | None = start_date_query,
    end_date: date | None = end_date_query,
    days_of_week: str | None = days_of_week_query,
    time_periods: str | None = time_periods_query,
    h3_resolution: str | None = h3_resolution_query,
    modalities: str | None = modalities_query,
    destination_cells: str | None = destination_cells_query,
):
    h3_resolution = int(h3_resolution)
    query_destinations = query_od_parameters.convert_h3_cells(cells=destination_cells, h3_resolution=h3_resolution)
    if not accessible_h3.check_if_user_has_access_to_h3_cells(request.state.acl, query_destinations, h3_resolution):
        raise HTTPException(403, "this user is not authorized to receive information of these h3 cells")
    
    query_od_parameter = query_od_parameters.prepare_query(
        start_date = start_date,
        end_date = end_date,
        days_of_week = days_of_week,
        time_periods = time_periods,
        modalities = modalities
    )
    result = db.query_h3_origins(query_destinations, h3_resolution, query_od_parameter)
    return {
        "result": {
            "destinations": serialize_od_h3_result(result)
        } 
    }

@app.get("/destinations/h3")
async def get_destinations_h3(
    request: Request,
    start_date: date | None = start_date_query,
    end_date: date | None = end_date_query,
    days_of_week: str | None = days_of_week_query,
    time_periods: str | None = time_periods_query,
    h3_resolution: str | None = h3_resolution_query,
    modalities: str | None = modalities_query,
    origin_cells: str | None = origin_cells_query
):
    h3_resolution = int(h3_resolution)
    query_origins = query_od_parameters.convert_h3_cells(cells=origin_cells, h3_resolution=h3_resolution)
    if not accessible_h3.check_if_user_has_access_to_h3_cells(request.state.acl, query_origins, h3_resolution):
        raise HTTPException(403, "this user is not authorized to receive information of these h3 cells")
    
    query_od_parameter = query_od_parameters.prepare_query(
        start_date = start_date,
        end_date = end_date,
        days_of_week = days_of_week,
        time_periods = time_periods,
        modalities = modalities
    )

    result = db.query_h3_destinations(query_origins, h3_resolution, query_od_parameter)
    return {
        "result": {
            "destinations": serialize_od_h3_result(result)
        }  
    }

@app.get("/origins/geometry")
async def get_origins(
    request: Request,
    start_date: date | None = start_date_query,
    end_date: date | None = end_date_query,
    days_of_week: str | None = days_of_week_query,
    time_periods: str | None = time_periods_query,
    modalities: str | None = modalities_query,
    destination_stat_refs: str | None = destination_stat_refs_query
):  
    destination_stat_refs = destination_stat_refs.split(",")
    if not accessible_geometry.check_if_user_has_access_to_geometries(request.state.acl, destination_stat_refs):
        raise HTTPException(403, "This user is not authorized to receive this information")
    
    query_od_parameter = query_od_parameters.prepare_query(
        start_date = start_date,
        end_date = end_date,
        days_of_week = days_of_week,
        time_periods = time_periods,
        modalities = modalities
    )
    
    result = db.query_geometry_origins(destination_stat_refs, query_od_parameter)
    return {
        "result": {
            "destinations": result
        } 
    }

@app.get("/destinations/geometry")
async def get_destinations(
    request: Request, 
    start_date: date | None = start_date_query,
    end_date: date | None = end_date_query,
    days_of_week: str | None = days_of_week_query,
    time_periods: str | None = time_periods_query,
    modalities: str | None = modalities_query,
    origin_stat_refs: str | None = origin_stat_refs_query
):
    origin_stat_refs = origin_stat_refs.split(",")
    if not accessible_geometry.check_if_user_has_access_to_geometries(request.state.acl, origin_stat_refs):
        raise HTTPException(403, "this user is not authorized to receive this information")
    
    query_od_parameter = query_od_parameters.prepare_query(
        start_date = start_date,
        end_date = end_date,
        days_of_week = days_of_week,
        time_periods = time_periods,
        modalities = modalities
    )
    result = db.query_geometry_destinations(origin_stat_refs, query_od_parameter)
    return {
        "result": {
            "destinations": result
        }  
    }

@app.get("/accessible/h3")
async def get_accessible_h3_cells(
    request: Request,
    filter_municipalities: str | None = "",
    h3_resolution: str | None = h3_resolution_query,
):
    filter_municipalities = set(filter_municipalities.split(","))
    filter_municipalities.discard("")
    if len(filter_municipalities) == 0 and request.state.acl.is_admin:
        return {
            "result": {
                "all_accessible": True,
                "accessible_h3_cells": []
            }  
        }

    accessible_municipalities = get_acl.get_accessible_municipalities(request.state.acl)
    if not request.state.acl.is_admin and not filter_municipalities.issubset(accessible_municipalities):
         raise HTTPException(403, "This user is not allowed to retreive information for all municipalities specified in filter")
    if len(filter_municipalities) == 0:
        filter_municipalities = accessible_municipalities
    
    h3_resolution = int(h3_resolution)
    result = accessible_h3.get_accessible_h3_cells(list(filter_municipalities), h3_resolution)  
    return {
        "result": {
            "all_accessible": request.state.acl.is_admin,
            "accessible_h3_cells": result
        }  
    }

@app.get("/accessible/geometry")
async def get_accessible_geometries(
    request: Request,
    filter_municipalities: str | None = ""
):
    filter_municipalities = set(filter_municipalities.split(","))
    filter_municipalities.discard("")
    if len(filter_municipalities) == 0 and request.state.acl.is_admin:
        return {
            "result": {
                "all_accessible": True,
                "accessible_geometries": []
            }  
        }

    accessible_municipalities = get_acl.get_accessible_municipalities(request.state.acl)
    if not request.state.acl.is_admin and not filter_municipalities.issubset(accessible_municipalities):
         raise HTTPException(403, "this user is not allowed to retrieve information for all municipalities specified in filter")
    if len(filter_municipalities) == 0:
        filter_municipalities = accessible_municipalities
    
    result = accessible_geometry.get_accessible_geometries(filter_municipalities)
    return {
        "result": {
            "all_accessible": request.state.acl.is_admin,
            "accessible_geometries": result
        }  
    }

@app.get("/matrix/h3")
async def get_matrix():
    return {"message": "Hello World"}