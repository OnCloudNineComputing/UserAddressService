from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService
from application_services.UsersResource.user_service import UserResource
from application_services.UsersResource.address_resource import AddressResource


class UserAddressResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data):
        pass

    @classmethod
    def get_data_resource_info(cls):
        return 'e6156', 'users'

    @classmethod
    def get_address_by_id(cls, id):
        user_db_name, user_table_name = UserResource.get_data_resource_info()
        address_db_name, address_table_name = AddressResource.get_data_resource_info()

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = f"SELECT b.* \
                FROM {user_db_name}.{user_table_name} as a, {address_db_name}.{address_table_name} as b \
                where a.id=%s and a.address_id=b.id"
        args = [id]
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def create_address_by_id(cls, id, data):
        res = AddressResource.get_by_template(data)
        if len(res) == 0:
            res = AddressResource.create(data)
            res = AddressResource.get_by_template(data)
        address_id = res[0]['id']
        res = UserResource.update_by_id(id, {'address_id': address_id})

        return res

    @classmethod
    def delete_address_by_id(cls, id):
        res = UserResource.update_by_id(id, {'address_id': None})
        return res

    @classmethod
    def update_address_by_id(cls, id, data):
        res = AddressResource.get_by_template(data)
        if len(res) == 0:
            res = AddressResource.create(data)
            res = AddressResource.get_by_template(data)
        address_id = res[0]['id']
        res = UserResource.update_by_id(id, {'address_id': address_id})
        return res




    @classmethod
    def get_user_by_id(cls, id):
        user_db_name, user_table_name = UserResource.get_data_resource_info()
        address_db_name, address_table_name = AddressResource.get_data_resource_info()

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = f"SELECT a.* \
                   FROM {user_db_name}.{user_table_name} as a, {address_db_name}.{address_table_name} as b \
                   where b.id=%s and a.address_id=b.id"
        args = [id]
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def create_user_by_id(cls, id, data):
        res = UserResource.get_by_template(data)
        if len(res) == 0:
            res = UserResource.create(data)
            res = UserResource.get_by_template(data)
        user_id = res[0]['id']
        res = UserResource.update_by_id(user_id, {'address_id': id})

        return res

    @classmethod
    def delete_user_by_id(cls, id):
        user_db_name, user_table_name = UserResource.get_data_resource_info()

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = f" UPDATE {user_db_name}.{user_table_name} \
                   SET address_id=NULL \
                   where {user_db_name}.{user_table_name}.address_id=%s"
        args = [id]
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()
        return res
