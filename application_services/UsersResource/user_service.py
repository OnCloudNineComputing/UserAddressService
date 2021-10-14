from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService
from application_services.UsersResource.address_resource import AddressResource


class UserResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data):
        pass

    @classmethod
    def get_data_resource_info(cls):
        return 'e6156', 'users'