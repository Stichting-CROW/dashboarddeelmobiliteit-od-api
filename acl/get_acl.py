import jwt
from acl import acl, db
from acl.acl import ACL

def get_access(request):
    if not request.headers.get('Authorization'):
        return None
    encoded_token = request.headers.get('Authorization')
    encoded_token = encoded_token.split(" ")[1]
    # Verification is performed by kong (reverse proxy), 
    # therefore token is not verified for a second time so that the secret is only stored there.
    result = jwt.decode(encoded_token, options={"verify_signature": False})

    # Get ACL and return result
    return get_acl_for_user_id(result["email"])
    
def get_acl_for_user_id(user_id: str):
    result = db.get_organisation_and_privileges(user_id)
    if result == None:
        return None
    return create_acl(result)

def get_accessible_municipalities(acl_user: ACL):
    result = map(lambda row: row["municipality_code"], db.get_accessible_municipalities(acl_user.user_id))
    return set(result)

def create_acl(row):
    privileges = []
    if row["privileges"]:
        privileges = map(lambda x: PrivilegesEnum(x), row["privileges"])
    return acl.ACL(
        user_id=row["user_id"],
        part_of_organisation=row["organisation_id"],
        privileges=privileges,
        is_admin=(row["type_of_organisation"] == "ADMIN")
    )
