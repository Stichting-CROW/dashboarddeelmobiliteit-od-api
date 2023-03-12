import db
import h3
from acl.acl import ACL
from acl import get_acl

def get_accessible_h3_cells(municipalities: list[str], h3_level: int):
    result = db.get_accessible_h3_cells(municipalities, h3_level)
    result = list(map(lambda cell: h3.h3_to_string(cell["h3_cell"]), result))
    return result

def check_if_user_has_access_to_h3_cells(acl: ACL, requested_h3_cells: list[int], h3_level: int):
    if acl.is_admin:
        return True
    municipalities = get_acl.get_accessible_municipalities(acl)
    result = db.get_accessible_h3_cells(municipalities, h3_level)
    accessible_h3_cells = set(map(lambda cell: cell["h3_cell"], result))
    requested_h3_cells_set = set(requested_h3_cells)
    if requested_h3_cells_set.issubset(accessible_h3_cells):
        return True
    return False