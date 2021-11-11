import json

from flask import Response
from integrity_services.BaseIntegrityResource import BaseIntegrityResource


class UserAddressIntegrity(BaseIntegrityResource):

    def __init__(self):
        super(CoursesIntegrity, self).__init__()

    # field_list = ["course_name", "course_year", "course_sem", "dept", "course_number", "section", "professor",
    #               "TA", "credits", "course_days", "start_time", "end_time", "location", "enrollment"]
    required_fields = ["first_name", "last_name", "uni", "email", "role"]

    @classmethod
    def get_responses(cls, res):
        if res:
            return 200
        else:
            return 404

    @classmethod
    def type_validation(cls, data):
        return 200, "Data Types Validated"

    @classmethod
    def input_validation(cls, data):
        input_fields = list(data.keys())
        errors = {}

        try:
            for r in UserAddressIntegrity.required_fields:
                if r not in input_fields:
                    raise ValueError(
                        'Missing required data fields; "first_name", "last_name", "uni", "email", "role" are required.')
        except ValueError as v:
            errors["required_fields"] = str(v)

        type_errors = UserAddressIntegrity.type_validation(data)

        if type_errors[0] == 400:
            errors.update(type_errors[1])

        if errors:
            return 400, errors

        return 200, "Input Validated"

    @classmethod
    def post_responses(cls, res):
        rsp = ""
        if res == 422:
            rsp = Response("User already exists!", status=422,
                           content_type="text/plain")
        elif type(res) == tuple:
            if res[0] == 400:
                rsp = Response(json.dumps(res[1], default=str), status=res[0], content_type="application/json")
        elif res is not None:
            rsp = Response("Success! Created User with the given " +
                           "information.", status=201,
                           content_type="text/plain")
        else:
            rsp = Response("Failed! Unprocessable entity.",
                           status=422, content_type="text/plain")

        return rsp

    @classmethod
    def put_responses(cls, res):
        if res == 422:
            return 422
        elif type(res) == tuple and len(res) == 2:
            if res[0] == 400:
                return res[0]
        elif res:
            return 200

    @classmethod
    def user_collection_get_responses(cls, res):
        status = UserAddressIntegrity.get_responses(res)
        if status == 200:
            rsp = Response(json.dumps(res, default=str), status=status, content_type="application/json")
        else:
            rsp = Response("No data found!", status=status, content_type="text/plain")

        return rsp

    @classmethod
    def user_collection_put_responses(cls, res):
        status = UserAddressIntegrity.put_responses(res)
        rsp = ""
        if status == 422:
            rsp = Response("Update violates data integrity!", status=status,
                           content_type="text/plain")
        elif status == 400:
            rsp = Response(json.dumps(res[1], default=str), status=status, content_type="application/json")
        elif status == 200:
            rsp = Response("Success! The given data for the users " +
                           "that matched was updated as requested.", status=status,
                           content_type="text/plain")
        else:
            rsp = Response("Failed! Matching users not found or unexpected error.",
                           status=422, content_type="text/plain")

        return rsp

    @classmethod
    def delete_responses(cls, res):
        if res is not None:
            return 204
        else:
            return 422

    @classmethod
    def user_collection_delete_responses(cls, res):
        status = UserAddressIntegrity.delete_responses(res)
        if status == 204:
            rsp = Response("Success! Deleted all users.",
                           status=status, content_type="text/plain")
        else:
            rsp = Response("Failed! Could not delete all users.",
                           status=status, content_type="text/plain")

        return rsp

    @classmethod
    def address_by_user_id_get_responses(cls, res):
        status = UserAddressIntegrity.get_responses(res)
        if status == 200:
            rsp = Response(json.dumps(res, default=str), status=status, content_type="application/json")
        else:
            rsp = Response("Failed! User ID not found or User does not have address.", status=status,
                           content_type="text/plain")

        return rsp

    @classmethod
    def address_by_user_id_put_responses(cls, res, user_id):
        status = UserAddressIntegrity.put_responses(res)
        rsp = ""
        if status == 422:
            rsp = Response("Update violates data integrity!", status=status,
                           content_type="text/plain")
        elif status == 400:
            rsp = Response(json.dumps(res[1], default=str), status=status, content_type="application/json")
        elif status == 200:
            rsp = Response("Success! The given data for the user with ID " +
                           str(user_id) + " was updated as requested.", status=status,
                           content_type="text/plain")
        else:
            rsp = Response("Failed! Either nothing was updated or User ID not found or unexpected error.",
                           status=422, content_type="text/plain")

        return rsp

    @classmethod
    def address_by_user_id_delete_responses(cls, res, user_id):
        status = UserAddressIntegrity.delete_responses(res)
        if status == 204:
            rsp = Response("Success! Deleted address from user with ID " + str(user_id) + ".",
                           status=status, content_type="text/plain")
        else:
            rsp = Response("Failed! Address not found under user with ID " + str(user_id) + ".",
                           status=status, content_type="text/plain")

        return rsp

    @classmethod
    def user_by_address_id_get_responses(cls, res):
        status = UserAddressIntegrity.get_responses(res)
        if status == 200:
            rsp = Response(json.dumps(res, default=str), status=status, content_type="application/json")
        else:
            rsp = Response("Failed! Address ID not found or no users have this address.", status=status,
                           content_type="text/plain")

        return rsp

    @classmethod
    def user_by_address_delete_responses(cls, res, address_id):
        status = UserAddressIntegrity.delete_responses(res)
        if status == 204:
            rsp = Response("Success! Deleted user from address with ID " + str(address_id) + ".",
                           status=status, content_type="text/plain")
        else:
            rsp = Response("Failed! Address ID not found or no users have this address.",
                           status=status, content_type="text/plain")

        return rsp
