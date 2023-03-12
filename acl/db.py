from db_helper import db_helper

def get_organisation_and_privileges(username):
    stmt = """
        SELECT user_id, organisation_id, privileges, type_of_organisation
        FROM user_account
        JOIN organisation
        USING (organisation_id)
        WHERE user_id = %(user_id)s;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {"user_id": username})
            return cur.fetchone()
        except Exception as e:
            conn.rollback()
            print(e)

def get_accessible_municipalities(username):
    stmt = """
    SELECT DISTINCT(UNNEST(data_owner_of_municipalities)) as municipality_code
    FROM organisation
    WHERE 
    organisation_id IN 
    (
        (SELECT owner_organisation_id
        FROM user_account
        JOIN organisation
        USING(organisation_id)
        JOIN view_data_access
        ON organisation.organisation_id = granted_organisation_id
        WHERE user_id = %(user_id)s)
        UNION
        (SELECT owner_organisation_id
        FROM user_account
        JOIN organisation
        USING(organisation_id)
        JOIN view_data_access
        ON user_account.user_id = granted_user
        WHERE user_id = %(user_id)s)
    )
    OR 
    organisation_id IN 
    (
        SELECT organisation_id
        FROM user_account
        JOIN organisation
        USING(organisation_id)
        WHERE user_id = %(user_id)s
    );    
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {"user_id": username})
            return cur.fetchall()
        except Exception as e:
            conn.rollback()
            print(e)