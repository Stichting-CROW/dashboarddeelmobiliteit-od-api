from dataclasses import dataclass
from enum import Enum

class PrivilegesEnum(str, Enum):
    organisation_admin = 'ORGANISATION_ADMIN'
    microhub_edit = 'MICROHUB_EDIT'
    download_raw_data = 'DOWNLOAD_RAW_DATA'
    core_group = 'CORE_GROUP'

@dataclass
class ACL:
    user_id: str
    part_of_organisation: int
    privileges: list[PrivilegesEnum]
    is_admin: bool