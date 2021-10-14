from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService


class AddressResource(BaseRDBApplicationResource):
    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data):
        pass

    @classmethod
    def get_data_resource_info(cls):
        return 'e6156', 'addresses'


