from database_services.RDBService import RDBService


class UsersRDBService(RDBService):

    def __init__(self):
        super().__init__()

    @classmethod
    def create(cls, db_schema, table_name, create_data):

        id_keys = ["first_name", "last_name", "uni", "email", "role"]
        course_id = {key: value for key, value in create_data.items() if key in id_keys}
        course_matches = cls.find_by_template(db_schema, table_name, course_id)
        if not course_matches:
            cols = []
            vals = []
            args = []

            for k, v in create_data.items():
                cols.append(k)
                vals.append('%s')
                args.append(v)

            cols_clause = "(" + ",".join(cols) + ")"
            vals_clause = "VALUES (" + ",".join(vals) + ")"

            sql_stmt = "INSERT INTO " + db_schema + "." + table_name + " " + cols_clause + \
                       " " + vals_clause

            res = cls.run_sql(sql_stmt, args)

            return res
        else:
            return 422

    @classmethod
    def find_by_user_id(cls, db_schema, table_name, user_id, order_by=None, limit=None, offset=None, field_list=None):

        template = {"id": user_id}

        return cls.find_by_template(db_schema, table_name, template, order_by, limit, offset, field_list)

    @classmethod
    def update_by_user_id(cls, db_schema, table_name, user_id, data):

        template = {"id": user_id}

        return cls.update_by_template(db_schema, table_name, data, template)

    @classmethod
    def delete_by_user_id(cls, db_schema, table_name, user_id):

        template = {"id": user_id}

        return cls.delete_by_template(db_schema, table_name, template)
