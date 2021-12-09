from application_services.BaseApplicationResource import BaseRDBApplicationResource
from application_services.UsersResource.address_resource import AddressResource
from application_services.UsersResource.user_service import UserResource
from database_services.RDBService import RDBService


class UserAddressResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data, inputs):
        links = []
        path_args = []
        next_path_args = []
        prev_path_args = []

        path = inputs.path
        next_path = inputs.path
        prev_path = inputs.path
        if inputs.args:
            input_args = inputs.args
            for k, v in input_args.items():
                input_args[k] = v.replace(" ", "%20")
            path_args.append("&".join(["=".join([k, str(v)]) for k, v in input_args.items()]))
            next_path_args.append("&".join(["=".join([k, str(v)]) for k, v in input_args.items()]))
            prev_path_args.append("&".join(["=".join([k, str(v)]) for k, v in input_args.items()]))
        if inputs.fields:
            path_args.append("fields=" + inputs.fields)
            next_path_args.append("fields=" + inputs.fields)
            prev_path_args.append("fields=" + inputs.fields)
        if inputs.order_by:
            path_args.append("order_by=" + inputs.order_by)
            next_path_args.append("order_by=" + inputs.order_by)
            prev_path_args.append("order_by=" + inputs.order_by)
        else:
            path_args.append("order_by=id")
            next_path_args.append("order_by=id")
            prev_path_args.append("order_by=id")
        limit = 5
        if inputs.limit:
            if int(inputs.limit) < limit:
                limit = int(inputs.limit)
        path_args.append("limit=" + str(limit))
        next_path_args.append("limit=" + str(limit))
        prev_path_args.append("limit=" + str(limit))
        offset = 0
        if inputs.offset:
            offset = int(inputs.offset)
        path_args.append("offset=" + str(offset))
        next_path_args.append("offset=" + str(offset + limit))
        if offset != 0:
            prev_path_args.append("offset=" + str(offset - limit))

        if path_args:
            path += "?" + "&".join(path_args)
        if next_path_args:
            next_path += "?" + "&".join(next_path_args)
        if prev_path_args:
            prev_path += "?" + "&".join(prev_path_args)

        self_link = {"rel": "self", "href": path}
        links.append(self_link)
        next_link = {"rel": "next", "href": next_path}
        links.append(next_link)
        if offset != 0:
            prev_link = {"rel": "prev", "href": prev_path}
            links.append(prev_link)

        links_dict = {"links": links}
        resource_data.append(links_dict)

        return resource_data

    @classmethod
    def get_data_resource_info(cls):
        return 'e6156', 'users'

    @classmethod
    def get_address_by_user_id(cls, user_id, order_by=None, limit=None, offset=None, field_list=None):
        user_db_name, user_table_name = UserResource.get_data_resource_info()
        address_db_name, address_table_name = AddressResource.get_data_resource_info()

        conn = RDBService.get_db_connection()
        cur = conn.cursor()

        sql = f"SELECT b.* \
                FROM {user_db_name}.{user_table_name} as a, {address_db_name}.{address_table_name} as b \
                where a.id=%s and a.address_id=b.id"

        if order_by is not None:
            sql += " ORDER BY " + order_by
        if limit is not None:
            sql += " LIMIT " + str(limit)
        if offset is not None:
            sql += " OFFSET " + str(offset)

        args = [user_id]
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def create_address_by_user_id(cls, user_id, data):
        res = AddressResource.get_by_template(data)
        if len(res) == 0:
            res = AddressResource.create(data)
            if res == 422:
                return res
            res = AddressResource.get_by_template(data)
        address_id = res[0]['id']
        res = UserResource.update_by_user_id(user_id, {'address_id': address_id})

        return res

    @classmethod
    def delete_address_by_user_id(cls, user_id):
        res = UserResource.update_by_user_id(user_id, {'address_id': None})
        return res

    @classmethod
    def update_address_by_user_id(cls, user_id, data):
        res = AddressResource.get_by_template(data)
        if len(res) == 0:
            res = AddressResource.create(data)
            res = AddressResource.get_by_template(data)
        address_id = res[0]['id']
        res = UserResource.update_by_user_id(user_id, {'address_id': address_id})
        return res

    @classmethod
    def get_user_by_address_id(cls, address_id, order_by=None, limit=None, offset=None, field_list=None):
        user_db_name, user_table_name = UserResource.get_data_resource_info()
        address_db_name, address_table_name = AddressResource.get_data_resource_info()

        conn = RDBService.get_db_connection()
        cur = conn.cursor()

        sql = f"SELECT a.* \
                   FROM {user_db_name}.{user_table_name} as a, {address_db_name}.{address_table_name} as b \
                   where b.id=%s and a.address_id=b.id"

        if order_by is not None:
            sql += " ORDER BY " + order_by
        if limit is not None:
            sql += " LIMIT " + str(limit)
        if offset is not None:
            sql += " OFFSET " + str(offset)

        args = [address_id]
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def create_user_by_address_id(cls, address_id, data):
        res = UserResource.get_by_template(data)
        if len(res) == 0:
            res = UserResource.create(data)
            if res == 422:
                return res
            res = UserResource.get_by_template(data)
        user_id = res[0]['id']
        res = UserResource.update_by_user_id(user_id, {'address_id': address_id})

        return res

    @classmethod
    def delete_user_by_address_id(cls, address_id):
        user_db_name, user_table_name = UserResource.get_data_resource_info()

        conn = RDBService.get_db_connection()
        cur = conn.cursor()

        sql = f" UPDATE {user_db_name}.{user_table_name} \
                   SET address_id=NULL \
                   where {user_db_name}.{user_table_name}.address_id=%s"
        args = [address_id]
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()
        return res
