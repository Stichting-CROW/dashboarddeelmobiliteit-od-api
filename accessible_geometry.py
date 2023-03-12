import db
import h3
from acl.acl import ACL
from acl import get_acl
import json

def serialize_geometry(row):
    return {
        "zone_id": row["zone_id"],
        "geojson": json.loads(row["area"]),
        "municipality_code": row["municipality"],
        "stats_ref": row["stats_ref"]
    }

def get_accessible_geometries(municipalities: list[str]):
    result = db.get_accessible_geometries_with_geojson(municipalities)
    result = list(map(serialize_geometry, result))
    return result

def check_if_user_has_access_to_geometries(acl: ACL, requested_geometries: list[str]):
    if acl.is_admin:
        return True
    municipalities = get_acl.get_accessible_municipalities(acl)
    result = db.get_accessible_geometries(municipalities=municipalities)
    accessible_stats_refs = set(map(lambda row: row["stats_ref"], result))
    requested_geometries_set = set(requested_geometries)
    print(accessible_stats_refs)
    print(requested_geometries)
    if requested_geometries_set.issubset(accessible_stats_refs):
        return True
    return False