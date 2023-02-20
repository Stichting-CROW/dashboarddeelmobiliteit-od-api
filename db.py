from db_helper import db_helper
from datetime import timedelta
import query_od_parameters

def query_h3_destinations(
    origin_cells: list[int], 
    h3_resolution: int, 
    data: query_od_parameters.QueryODParameters):
    stmt = """
        SELECT * 
        FROM (
            SELECT destination_cell as cell, sum(number_of_trips) as number_of_trips
            FROM od_h3
            WHERE origin_cell IN %(origin_cells)s
            AND h3_level = %(h3_resolution)s
            AND (%(dont_filter_on_modality)s = true OR modality = %(modalities)s)
            AND aggregation_period_id IN (
                SELECT aggregation_period_id 
                FROM od_aggregation_period
                WHERE (%(dont_filter_on_days_of_week)s = true OR extract(isodow from start_time_period) IN %(days_of_week)s)
                AND (%(dont_filter_on_time_periods)s = true OR extract(hour from start_time_period) IN %(time_periods)s)
                AND start_time_period >= %(start_period)s AND start_time_period <= (%(end_period)s + 1)
            ) GROUP by destination_cell order by sum(number_of_trips) DESC
        ) as q1
        WHERE number_of_trips >= 4
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute("SET TIME ZONE 'Europe/Amsterdam'")
            cur.execute(stmt, {
                "origin_cells": tuple(origin_cells),
                "h3_resolution": h3_resolution,
                "dont_filter_on_modality": data.dont_filter_on_modality,
                "modalities": tuple(data.modalities),
                "dont_filter_on_days_of_week": data.dont_filter_on_days_of_week,
                "days_of_week": tuple(data.days_of_week),
                "dont_filter_on_time_periods": data.dont_filter_on_time_periods,
                "time_periods": tuple(data.time_periods),
                "start_period": data.start_date,
                "end_period": data.end_date
                })
            return cur.fetchall()
        except Exception as e:
            conn.rollback()
            print(e)

def query_h3_origins(
    destination_cells: list[int], 
    h3_resolution: int, 
    data: query_od_parameters.QueryODParameters):
    stmt = """
        SELECT * 
        FROM (
            SELECT origin_cell as cell, sum(number_of_trips) as number_of_trips
            FROM od_h3
            WHERE destination_cell IN %(destination_cells)s
            AND h3_level = %(h3_resolution)s
            AND (%(dont_filter_on_modality)s = true or modality = %(modalities)s)
            AND aggregation_period_id IN (
                SELECT aggregation_period_id 
                FROM od_aggregation_period
                WHERE (%(dont_filter_on_days_of_week)s = true OR extract(isodow from start_time_period) IN %(days_of_week)s)
                AND (%(dont_filter_on_time_periods)s = true OR extract(hour from start_time_period) IN %(time_periods)s)
                AND start_time_period >= %(start_period)s and start_time_period <= %(end_period)s
            ) GROUP by origin_cell order by sum(number_of_trips) DESC    
        ) as q1
        WHERE number_of_trips >= 4
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute("SET TIME ZONE 'Europe/Amsterdam'")
            cur.execute(stmt, {
                "destination_cells": tuple(destination_cells),
                "h3_resolution": h3_resolution,
                "dont_filter_on_modality": data.dont_filter_on_modality,
                "modalities": tuple(data.modalities),
                "dont_filter_on_days_of_week": data.dont_filter_on_days_of_week,
                "days_of_week": tuple(data.days_of_week),
                "dont_filter_on_time_periods": data.dont_filter_on_time_periods,
                "time_periods": tuple(data.time_periods),
                "start_period": data.start_date,
                "end_period": data.end_date
                })
            return cur.fetchall()
        except Exception as e:
            conn.rollback()
            print(e)

def query_geometry_destinations(
    origin_stat_refs: list[str], 
    data: query_od_parameters.QueryODParameters):
    stmt = """
        SELECT * 
        FROM (
            SELECT destination_stats_ref as destination_stat_ref, sum(number_of_trips) as number_of_trips
            FROM od_geometry
            WHERE origin_stats_ref IN %(origin_stat_refs)s
            AND (%(dont_filter_on_modality)s = true OR modality = %(modalities)s)
            AND aggregation_period_id IN (
                SELECT aggregation_period_id 
                FROM od_aggregation_period
                WHERE (%(dont_filter_on_days_of_week)s = true OR extract(isodow from start_time_period) IN %(days_of_week)s)
                AND (%(dont_filter_on_time_periods)s = true OR extract(hour from start_time_period) IN %(time_periods)s)
                AND start_time_period >= %(start_period)s AND start_time_period <= (%(end_period)s + 1)
            ) GROUP by destination_stats_ref order by sum(number_of_trips) DESC
        ) as q1
        WHERE number_of_trips >= 4
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute("SET TIME ZONE 'Europe/Amsterdam'")
            cur.execute(stmt, {
                "origin_stat_refs": tuple(origin_stat_refs),
                "dont_filter_on_modality": data.dont_filter_on_modality,
                "modalities": tuple(data.modalities),
                "dont_filter_on_days_of_week": data.dont_filter_on_days_of_week,
                "days_of_week": tuple(data.days_of_week),
                "dont_filter_on_time_periods": data.dont_filter_on_time_periods,
                "time_periods": tuple(data.time_periods),
                "start_period": data.start_date,
                "end_period": data.end_date
                })
            return cur.fetchall()
        except Exception as e:
            conn.rollback()
            print(e)

def query_geometry_origins(
    destination_stat_refs: list[str], 
    data: query_od_parameters.QueryODParameters):
    stmt = """
        SELECT * 
        FROM (
            SELECT origin_stats_ref as origin_stat_ref, sum(number_of_trips) as number_of_trips
            FROM od_geometry
            WHERE destination_stats_ref IN %(destination_stat_refs)s
            AND (%(dont_filter_on_modality)s = true or modality = %(modalities)s)
            AND aggregation_period_id IN (
                SELECT aggregation_period_id 
                FROM od_aggregation_period
                WHERE (%(dont_filter_on_days_of_week)s = true OR extract(isodow from start_time_period) IN %(days_of_week)s)
                AND (%(dont_filter_on_time_periods)s = true OR extract(hour from start_time_period) IN %(time_periods)s)
                AND start_time_period >= %(start_period)s and start_time_period <= %(end_period)s
            ) GROUP by origin_stats_ref order by sum(number_of_trips) DESC    
        ) as q1
        WHERE number_of_trips >= 4
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute("SET TIME ZONE 'Europe/Amsterdam'")
            cur.execute(stmt, {
                "destination_stat_refs": tuple(destination_stat_refs),
                "dont_filter_on_modality": data.dont_filter_on_modality,
                "modalities": tuple(data.modalities),
                "dont_filter_on_days_of_week": data.dont_filter_on_days_of_week,
                "days_of_week": tuple(data.days_of_week),
                "dont_filter_on_time_periods": data.dont_filter_on_time_periods,
                "time_periods": tuple(data.time_periods),
                "start_period": data.start_date,
                "end_period": data.end_date
                })
            return cur.fetchall()
        except Exception as e:
            conn.rollback()
            print(e)