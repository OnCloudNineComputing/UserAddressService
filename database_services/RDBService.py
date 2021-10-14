import pymysql
import json
import logging

import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RDBService:

    def __init__(self):
        pass

    @classmethod
    def _get_db_connection(cls):

        db_connect_info = context.get_db_info()

        logger.info("RDBService._get_db_connection:")
        logger.info("\t HOST = " + db_connect_info['host'])

        db_info = context.get_db_info()

        db_connection = pymysql.connect(
           **db_info,
            autocommit=True
        )
        return db_connection

    @classmethod
    def run_sql(cls, sql_statement, args, fetch=False):

        conn = RDBService._get_db_connection()

        try:
            cur = conn.cursor()
            res = cur.execute(sql_statement, args=args)
            if fetch:
                res = cur.fetchall()
        except Exception as e:
            conn.close()
            raise e

        return res

    @classmethod
    def get_by_prefix(cls, db_schema, table_name, column_name, value_prefix):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name + " where " + \
            column_name + " like " + "'" + value_prefix + "%'"
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def get_where_clause_args(cls, template):

        terms = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k,v in template.items():
                terms.append(k + "=%s")
                args.append(v)

            clause = " where " +  " AND ".join(terms)


        return clause, args

    @classmethod
    def find_by_template(cls, db_schema, table_name, template, field_list):

        wc,args = RDBService.get_where_clause_args(template)

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name + " " + wc
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def find_by_id(cls, db_schema, table_name, id, field_list):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name + " where id=%s"
        args = [id]
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def delete_by_id(cls, db_schema, table_name, id, field_list):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "delete from " + db_schema + "." + table_name + " where id=%s"
        args = [id]
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res


    @classmethod
    def update_by_id(cls, db_schema, table_name, id, data, field_list):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        cols = []
        args = []
        sql = "update " + db_schema + "." + table_name + " set "

        for k, v in data.items():
            cols.append(k+"=%s")
            args.append(v)

        sql += ", ".join(cols)
        sql += " where id=%s"

        args.append(id)

        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def next_id(cls, db_schema, table_name):
        max_id = RDBService.run_sql("select max(id) from " + db_schema + "." + table_name, None, True)[0]['max(id)']
        return max_id+1 if max_id else 1

    @classmethod
    def create(cls, db_schema, table_name, create_data):

        cols = []
        vals = []
        args = []

        next_id = RDBService.next_id(db_schema, table_name)
        cols.append('id')
        vals.append('%s')
        args.append(next_id)

        for k,v in create_data.items():
            cols.append(k)
            vals.append('%s')
            args.append(v)

        cols_clause = "(" + ",".join(cols) + ")"
        vals_clause = "values (" + ",".join(vals) + ")"

        sql_stmt = "insert into " + db_schema + "." + table_name + " " + cols_clause + \
            " " + vals_clause

        res = RDBService.run_sql(sql_stmt, args)
        return res

