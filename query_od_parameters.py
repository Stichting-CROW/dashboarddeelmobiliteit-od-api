from datetime import date
import h3
from fastapi import HTTPException
from dataclasses import dataclass

@dataclass
class QueryODParameters:
    start_date: date
    end_date: date
    modalities: list[str]
    dont_filter_on_modality: bool
    days_of_week: list[int]
    dont_filter_on_days_of_week: bool
    time_periods: list[int]
    dont_filter_on_time_periods: bool

def prepare_query(
        start_date,
        end_date,
        days_of_week,
        time_periods,
        modalities
        ):
    if start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date is after end_date")

    query_days_of_week = [-1]
    dont_filter_on_days_of_week = True
    if days_of_week:
        query_days_of_week = convert_days_of_week(days_of_week=days_of_week)
        dont_filter_on_days_of_week = False

    query_time_periods = [-1]
    don_filter_on_time_periods = True
    if time_periods:
        query_time_periods = convert_time_periods(time_periods=time_periods)
        don_filter_on_time_periods = False

    query_modalities = ["undefined"]
    dont_filter_on_modalities = True
    if modalities:
        query_modalities = modalities.split(",")
        dont_filter_on_modalities = False
    
    return QueryODParameters(
        start_date = start_date,
        end_date = end_date,
        dont_filter_on_time_periods = don_filter_on_time_periods,
        time_periods = query_time_periods,
        dont_filter_on_days_of_week = dont_filter_on_days_of_week,
        days_of_week = query_days_of_week,
        dont_filter_on_modality = dont_filter_on_modalities,
        modalities = query_modalities
    )

def convert_days_of_week(days_of_week): 
    days_of_week = days_of_week.split(",")
    api_to_db_value = {
        "mo": 1,
        "tu": 2,
        "we": 3,
        "th": 4,
        "fr": 5,
        "sa": 6,
        "su": 7
    }
    return [api_to_db_value[param] for param in days_of_week]

def convert_time_periods(time_periods):
    time_periods = time_periods.split(",")
    api_to_db_value = {
        "2-6": 2,
        "6-10": 6,
        "10-14": 10,
        "14-18": 14,
        "18-22": 18,
        "22-2": 22
    }
    return [api_to_db_value[param] for param in time_periods]

def convert_h3_cells(cells, h3_resolution):
    if cells == None:
        return []
    
    cells = cells.split(",")
    result = []
    for cell in cells:
        h3_cell = h3.string_to_h3(cell)
        if h3.h3_get_resolution(cell) != h3_resolution:
            raise HTTPException(status_code=422, detail="h3_level doesn't match with origin and destination cells.")
        result.append(h3_cell)
    return result
