import json
import logging
import os
from datetime import datetime

from flask import Flask, Response, request, redirect, url_for
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google

import utils.rest_utils as rest_utils
from application_services.UsersResource.address_resource import AddressResource
from application_services.UsersResource.user_address_service import UserAddressResource
from application_services.UsersResource.user_service import UserResource
from integrity_services.AddressIntegrityResource import AddressIntegrity
from integrity_services.UserAddressIntegrityResource import UserAddressIntegrity
from integrity_services.UserIntegrityResource import UsersIntegrity

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = "supersekrit"
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
google_bp = make_google_blueprint(scope=["profile", "email"], redirect_url="/api/login")
app.register_blueprint(google_bp, url_prefix="/login")

CORS(app)


#########################################################################

@app.route("/api/login", methods=["GET"])
def authorization():
    if not google.authorized:
        return {'url': url_for("google.login")}
    resp = google.get("/oauth2/v1/userinfo")
    assert resp.ok, resp.text
    return redirect("http://localhost:4200/dashboard")


#########################################################################

# This path simply echoes to check that the app is working.
# The path is /health and the only method is GETs
@app.route("/api/health", methods=["GET"])
def health_check():
    rsp_data = {"status": "healthy", "time": str(datetime.now())}
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="app/json")
    return rsp


@app.route('/api')
def landing_page():
    return '<u>OH Application Users Microservice</u>'


@app.route('/api/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_collection():
    """
    1. HTTP GET return all courses.
    2. HTTP POST with body --> create a course, i.e --> Machine Learning
    3. HTTP PUT update all courses that match the provided where clause
    with the updated data
    --> JSON must be nested as follows
    {
        "update_fields": {
            "field1": "value",
            "field2": "value",
            ...
            "last_field": "value"
        },
        "where_fields": {
            "field1": "value",
            "field2": "value",
            ...
            "last_field": "value"
        }
    4. HTTP DELETE delete all courses from the database
    :return: response from desired action
    """
    try:
        inputs = rest_utils.RESTContext(request)
        rest_utils.log_request("user_collection", inputs)

        if inputs.method == "GET":
            limit = 5
            if inputs.limit:
                if int(inputs.limit) < limit:
                    limit = int(inputs.limit)
            offset = 0
            if inputs.offset:
                offset = int(inputs.offset)
            order_by = inputs.order_by
            res = UserResource.get_by_template(inputs.args, order_by=order_by,
                                               limit=limit, offset=offset,
                                               field_list=inputs.fields)
            if res:
                res = UserResource.get_links(res, inputs)
            rsp = UsersIntegrity.user_collection_get_responses(res)
        elif inputs.method == "POST":
            validation = UsersIntegrity.input_validation(inputs.data)
            if validation[0] == 200:
                res = UserResource.create(inputs.data)
            else:
                res = validation
            rsp = UsersIntegrity.post_responses(res)
        elif inputs.method == "PUT":
            data_template = inputs.data['update_fields']
            where_template = inputs.data['where_fields']
            update_fields_val = UsersIntegrity.type_validation(data_template)
            where_fields_val = UsersIntegrity.type_validation(where_template)
            if update_fields_val[0] == 200 and where_fields_val[0] == 200:
                res = UserResource.update_by_template(data_template, where_template)
            else:
                error_code = 0
                errors = {}
                if update_fields_val[0] != 200:
                    error_code = update_fields_val[0]
                    errors["Errors in update_fields"] = update_fields_val[1]
                if where_fields_val[0] != 200:
                    error_code = where_fields_val[0]
                    errors["Errors in where_fields"] = where_fields_val[1]
                res = (error_code, errors)
            rsp = UsersIntegrity.user_collection_put_responses(res)
        elif inputs.method == "DELETE":
            res = UserResource.delete_by_template(inputs.args)
            rsp = UsersIntegrity.user_collection_delete_responses(res)
        else:
            rsp = Response("NOT IMPLEMENTED", status=501)

    except Exception as e:
        # HTTP status code.
        print("/api/courses, e = ", str(e))
        rsp = Response("INTERNAL ERROR", status=500,
                       content_type="text/plain")

    return rsp


@app.route('/api/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def user_by_id(user_id):
    """
    1. HTTP GET return a specific course by ID.
    2. HTTP PUT match course by ID and update specific fields
    --> JSON must be nested as follows for update
    {
        "field1": "value",
        "field2": "value",
        ...
        "last_field": "value"
    }
    3. HTTP DELETE match course by ID and delete it
    :param course_id: course ID number, autogenerated in data table, or course code as a string in this format -
    "year_sem_dept_number_section" e.g. "2021_Fall_COMS_E6156_001"
    :return: response from desired action
    """
    try:
        test_id = int(user_id)
        id_type = "id"

        inputs = rest_utils.RESTContext(request)
        rest_utils.log_request("user_by_id", inputs)

        if inputs.method == "GET":
            limit = 5
            if inputs.limit:
                if int(inputs.limit) < limit:
                    limit = int(inputs.limit)
            offset = 0
            if inputs.offset:
                offset = int(inputs.offset)
            order_by = inputs.order_by
            if id_type == "id":
                res = UserResource.get_by_user_id(user_id, order_by=order_by, limit=limit, offset=offset,
                                                  field_list=inputs.fields)
            else:
                pass
            if res:
                res = UserResource.get_links(res, inputs)
            if id_type == "id":
                rsp = UsersIntegrity.user_by_id_get_responses(res)
            else:
                pass
        elif inputs.method == "PUT":
            validation = UsersIntegrity.type_validation(inputs.data)
            if validation[0] == 200:
                if id_type == "id":
                    res = UserResource.update_by_user_id(user_id, inputs.data)
                else:
                    pass
            else:
                res = validation
            if id_type == "id":
                rsp = UsersIntegrity.user_by_id_put_responses(res, user_id)
            else:
                pass
        elif inputs.method == "DELETE":
            if id_type == "id":
                test = UserResource.get_by_user_id(user_id)
                if test:
                    res = UserResource.delete_by_user_id(user_id)
                else:
                    res = None
            else:
                pass
            if id_type == "id":
                rsp = UsersIntegrity.user_by_id_delete_responses(res, user_id)
            else:
                pass
        else:
            rsp = Response("NOT IMPLEMENTED", status=501)

    except ValueError as v:
        print("/api/users/" + str(user_id))
        if type(v) == str:
            rsp = Response(str(v), status=400, content_type="text/plain")
        else:
            rsp = Response(json.dumps(v, default=str), status=400, content_type="application/json")

    except Exception as e:
        # HTTP status code.
        print("/api/users/" + str(user_id) + ", e = ", str(e))
        rsp = Response("INTERNAL ERROR", status=500,
                       content_type="text/plain")
    #
    return rsp


@app.route('/api/users/<user_id>/addresses', methods=['GET', 'POST', 'PUT', 'DELETE'])
def address_by_user_id(user_id):
    """
    1. HTTP GET return a specific course by ID.
    2. HTTP PUT match course by ID and update specific fields
    --> JSON must be nested as follows for update
    {
        "field1": "value",
        "field2": "value",
        ...
        "last_field": "value"
    }
    3. HTTP DELETE match course by ID and delete it
    :param course_id: course ID number, autogenerated in data table, or course code as a string in this format -
    "year_sem_dept_number_section" e.g. "2021_Fall_COMS_E6156_001"
    :return: response from desired action
    """
    try:
        test_id = int(user_id)
        id_type = "id"

        inputs = rest_utils.RESTContext(request)
        rest_utils.log_request("address_user_by_id", inputs)

        if inputs.method == "GET":
            limit = 5
            if inputs.limit:
                if int(inputs.limit) < limit:
                    limit = int(inputs.limit)
            offset = 0
            if inputs.offset:
                offset = int(inputs.offset)
            order_by = inputs.order_by
            if id_type == "id":
                res = UserAddressResource.get_address_by_user_id(user_id, order_by=order_by,
                                                                 limit=limit, offset=offset,
                                                                 field_list=inputs.fields)
            else:
                pass
            if res:
                res = UserAddressResource.get_links(res, inputs)
            if id_type == "id":
                rsp = UserAddressIntegrity.address_by_user_id_get_responses(res)
            else:
                pass

        elif inputs.method == "POST":
            validation = AddressIntegrity.input_validation(inputs.data)
            if validation[0] == 200:
                if id_type == "id":
                    res = UserAddressResource.create_address_by_user_id(user_id, inputs.data)
                else:
                    pass
            else:
                res = validation
            if id_type == "id":
                rsp = UserAddressIntegrity.address_by_user_id_put_responses(res, user_id)
            else:
                pass
        elif inputs.method == "PUT":
            validation = UserAddressIntegrity.type_validation(inputs.data)
            if validation[0] == 200:
                if id_type == "id":
                    res = UserAddressResource.update_address_by_user_id(user_id, inputs.data)
                else:
                    pass
            else:
                res = validation
            if id_type == "id":
                rsp = UserAddressIntegrity.address_by_user_id_put_responses(res, user_id)
            else:
                pass
        elif inputs.method == "DELETE":
            if id_type == "id":
                test = UserAddressResource.get_address_by_user_id(user_id)
                if test:
                    res = UserAddressResource.delete_address_by_user_id(user_id)
                else:
                    res = None
            else:
                pass
            if id_type == "id":
                rsp = UserAddressIntegrity.address_by_user_id_delete_responses(res, user_id)
            else:
                pass
        else:
            rsp = Response("NOT IMPLEMENTED", status=501)

    except ValueError as v:
        print("/api/users/" + str(user_id))
        if type(v) == str:
            rsp = Response(str(v), status=400, content_type="text/plain")
        else:
            rsp = Response(json.dumps(v, default=str), status=400, content_type="application/json")

    except Exception as e:
        # HTTP status code.
        print("/api/users/" + str(user_id) + ", e = ", str(e))
        rsp = Response("INTERNAL ERROR", status=500,
                       content_type="text/plain")
    #
    return rsp


@app.route('/api/addresses', methods=['GET', 'POST', 'PUT', 'DELETE'])
def address_collection():
    """
    1. HTTP GET return all courses.
    2. HTTP POST with body --> create a course, i.e --> Machine Learning
    3. HTTP PUT update all courses that match the provided where clause
    with the updated data
    --> JSON must be nested as follows
    {
        "update_fields": {
            "field1": "value",
            "field2": "value",
            ...
            "last_field": "value"
        },
        "where_fields": {
            "field1": "value",
            "field2": "value",
            ...
            "last_field": "value"
        }
    4. HTTP DELETE delete all courses from the database
    :return: response from desired action
    """
    try:
        inputs = rest_utils.RESTContext(request)
        rest_utils.log_request("address_collection", inputs)

        if inputs.method == "GET":
            limit = 5
            if inputs.limit:
                if int(inputs.limit) < limit:
                    limit = int(inputs.limit)
            offset = 0
            if inputs.offset:
                offset = int(inputs.offset)
            order_by = inputs.order_by
            res = AddressResource.get_by_template(inputs.args, order_by=order_by,
                                                  limit=limit, offset=offset,
                                                  field_list=inputs.fields)
            if res:
                res = AddressResource.get_links(res, inputs)
            rsp = AddressIntegrity.address_collection_get_responses(res)
        elif inputs.method == "POST":
            validation = AddressIntegrity.input_validation(inputs.data)
            if validation[0] == 200:
                res = AddressResource.create(inputs.data)
            else:
                res = validation
            rsp = AddressIntegrity.post_responses(res)
        elif inputs.method == "PUT":
            data_template = inputs.data['update_fields']
            where_template = inputs.data['where_fields']
            update_fields_val = AddressIntegrity.type_validation(data_template)
            where_fields_val = AddressIntegrity.type_validation(where_template)
            if update_fields_val[0] == 200 and where_fields_val[0] == 200:
                res = AddressResource.update_by_template(data_template, where_template)
            else:
                error_code = 0
                errors = {}
                if update_fields_val[0] != 200:
                    error_code = update_fields_val[0]
                    errors["Errors in update_fields"] = update_fields_val[1]
                if where_fields_val[0] != 200:
                    error_code = where_fields_val[0]
                    errors["Errors in where_fields"] = where_fields_val[1]
                res = (error_code, errors)
            rsp = AddressIntegrity.address_collection_put_responses(res)
        elif inputs.method == "DELETE":
            res = AddressResource.delete_by_template(inputs.args)
            rsp = AddressIntegrity.address_collection_delete_responses(res)
        else:
            rsp = Response("NOT IMPLEMENTED", status=501)

    except Exception as e:
        # HTTP status code.
        print("/api/courses, e = ", str(e))
        rsp = Response("INTERNAL ERROR", status=500,
                       content_type="text/plain")

    return rsp


@app.route('/api/addresses/<address_id>', methods=['GET', 'PUT', 'DELETE'])
def address_by_id(address_id):
    """
    1. HTTP GET return a specific course by ID.
    2. HTTP PUT match course by ID and update specific fields
    --> JSON must be nested as follows for update
    {
        "field1": "value",
        "field2": "value",
        ...
        "last_field": "value"
    }
    3. HTTP DELETE match course by ID and delete it
    :param course_id: course ID number, autogenerated in data table, or course code as a string in this format -
    "year_sem_dept_number_section" e.g. "2021_Fall_COMS_E6156_001"
    :return: response from desired action
    """
    try:
        test_id = int(address_id)
        id_type = "id"

        inputs = rest_utils.RESTContext(request)
        rest_utils.log_request("address_by_id", inputs)

        if inputs.method == "GET":
            limit = 5
            if inputs.limit:
                if int(inputs.limit) < limit:
                    limit = int(inputs.limit)
            offset = 0
            if inputs.offset:
                offset = int(inputs.offset)
            order_by = inputs.order_by
            if id_type == "id":
                res = AddressResource.get_by_address_id(address_id, order_by=order_by,
                                                        limit=limit, offset=offset,
                                                        field_list=inputs.fields)
            else:
                pass
            if res:
                res = AddressResource.get_links(res, inputs)
            if id_type == "id":
                rsp = AddressIntegrity.address_by_id_get_responses(res)
            else:
                pass
        elif inputs.method == "PUT":
            validation = AddressIntegrity.type_validation(inputs.data)
            if validation[0] == 200:
                if id_type == "id":
                    res = AddressResource.update_by_address_id(address_id, inputs.data)
                else:
                    pass
            else:
                res = validation
            if id_type == "id":
                rsp = AddressIntegrity.address_by_id_put_responses(res, address_id)
            else:
                pass
                # rsp = CoursesIntegrity.course_by_code_put_responses(res, user_id)
        elif inputs.method == "DELETE":
            if id_type == "id":
                test = AddressResource.get_by_address_id(address_id)
                if test:
                    res = AddressResource.delete_by_address_id(address_id)
                else:
                    res = None
            else:
                pass
            if id_type == "id":
                rsp = AddressIntegrity.address_by_id_delete_responses(res, address_id)
            else:
                pass
        else:
            rsp = Response("NOT IMPLEMENTED", status=501)

    except ValueError as v:
        print("/api/users/" + str(address_id))
        if type(v) == str:
            rsp = Response(str(v), status=400, content_type="text/plain")
        else:
            rsp = Response(json.dumps(v, default=str), status=400, content_type="application/json")

    except Exception as e:
        # HTTP status code.
        print("/api/users/" + str(address_id) + ", e = ", str(e))
        rsp = Response("INTERNAL ERROR", status=500,
                       content_type="text/plain")
    #
    return rsp


@app.route('/api/addresses/<address_id>/users', methods=['GET', 'POST', 'DELETE'])
def user_by_address_id(address_id):
    """
    1. HTTP GET return a specific course by ID.
    2. HTTP PUT match course by ID and update specific fields
    --> JSON must be nested as follows for update
    {
        "field1": "value",
        "field2": "value",
        ...
        "last_field": "value"
    }
    3. HTTP DELETE match course by ID and delete it
    :param course_id: course ID number, autogenerated in data table, or course code as a string in this format -
    "year_sem_dept_number_section" e.g. "2021_Fall_COMS_E6156_001"
    :return: response from desired action
    """
    try:
        test_id = int(address_id)
        id_type = "id"

        inputs = rest_utils.RESTContext(request)
        rest_utils.log_request("user_by_address_id", inputs)

        if inputs.method == "GET":
            limit = 5
            if inputs.limit:
                if int(inputs.limit) < limit:
                    limit = int(inputs.limit)
            offset = 0
            if inputs.offset:
                offset = int(inputs.offset)
            order_by = inputs.order_by
            if id_type == "id":
                res = UserAddressResource.get_user_by_address_id(address_id, order_by=order_by,
                                                                 limit=limit, offset=offset,
                                                                 field_list=inputs.fields)
            else:
                pass
            if res:
                res = UserAddressResource.get_links(res, inputs)
            if id_type == "id":
                rsp = UserAddressIntegrity.user_by_address_id_get_responses(res)
            else:
                pass
        elif inputs.method == "POST":
            validation = UsersIntegrity.input_validation(inputs.data)
            if validation[0] == 200:
                if id_type == "id":
                    res = UserAddressResource.create_user_by_address_id(address_id, inputs.data)
                else:
                    pass
            else:
                res = validation
            if id_type == "id":
                rsp = UserAddressIntegrity.post_responses(res)
            else:
                pass
        elif inputs.method == "DELETE":
            if id_type == "id":
                test = UserAddressResource.get_user_by_address_id(address_id)
                if test:
                    res = UserAddressResource.delete_user_by_address_id(address_id)
                else:
                    res = None
            else:
                pass
            if id_type == "id":
                rsp = UserAddressIntegrity.user_by_address_delete_responses(res, address_id)
            else:
                pass
        else:
            rsp = Response("NOT IMPLEMENTED", status=501)

    except ValueError as v:
        print("/api/users/" + str(address_id))
        if type(v) == str:
            rsp = Response(str(v), status=400, content_type="text/plain")
        else:
            rsp = Response(json.dumps(v, default=str), status=400, content_type="application/json")

    except Exception as e:
        # HTTP status code.
        print("/api/users/" + str(address_id) + ", e = ", str(e))
        rsp = Response("INTERNAL ERROR", status=500,
                       content_type="text/plain")
    #
    return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
