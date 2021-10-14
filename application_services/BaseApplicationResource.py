from abc import ABC, abstractmethod
from database_services.RDBService import RDBService


class BaseApplicationException(Exception):

    def __init__(self):
        pass


class BaseApplicationResource(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_by_template(cls, template):
        pass

    @classmethod
    @abstractmethod
    def get_links(self, resource_data):
        pass

    @classmethod
    @abstractmethod
    def get_data_resource_info(self):
        pass


class BaseRDBApplicationResource(BaseApplicationResource):

    def __init__(self):
        pass

    @classmethod
    def get_by_template(cls, template):
        db_name, table_name = cls.get_data_resource_info()
        res = RDBService.find_by_template(db_name, table_name,
                                          template, None)
        return res

    @classmethod
    def get_by_id(cls, id):
        db_name, table_name = cls.get_data_resource_info()
        res = RDBService.find_by_id(db_name, table_name,
                                          id, None)
        return res

    @classmethod
    def update_by_id(cls, id, data):
        db_name, table_name = cls.get_data_resource_info()
        res = RDBService.update_by_id(db_name, table_name,
                                          id, data, None)
        return res

    @classmethod
    def delete_by_id(cls, id):
        db_name, table_name = cls.get_data_resource_info()
        res = RDBService.delete_by_id(db_name, table_name,
                                          id, None)
        return res

    @classmethod
    def create(cls, data):
        db_name, table_name = cls.get_data_resource_info()
        res = RDBService.create(db_name, table_name, data)
        return res

    @classmethod
    @abstractmethod
    def get_links(self, resource_data):
        pass

    @classmethod
    @abstractmethod
    def get_data_resource_info(self):
        pass
