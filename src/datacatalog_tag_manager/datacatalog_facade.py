import logging
from functools import lru_cache

from google.cloud import datacatalog


class DataCatalogFacade:
    """Data Catalog API communication facade."""

    __NESTED_LOG_PREFIX = ' ' * 5

    def __init__(self):
        # Initialize the API client.
        self.__datacatalog = datacatalog.DataCatalogClient()

    def create_or_update_tag(self, parent_entry_name, tag):
        entry_tags = self.__datacatalog.list_tags(parent=parent_entry_name)

        try:
            persisted_tag = next(
                entry_tag for entry_tag in entry_tags
                if entry_tag.template == tag.template and entry_tag.column == tag.column)
            tag.name = persisted_tag.name
            self.__log_operation_start('UPDATE Tag: %s', tag.name)
            return self.__datacatalog.update_tag(tag=tag)
        except StopIteration:
            self.__log_operation_start('CREATE Tag for: %s', parent_entry_name)
            logging.info('%sUsing Tag Template: %s', self.__NESTED_LOG_PREFIX, tag.template)
            created_tag = self.__datacatalog.create_tag(parent=parent_entry_name, tag=tag)
            logging.info('%sCreated: %s', self.__NESTED_LOG_PREFIX, created_tag.name)
            return created_tag

    @lru_cache(maxsize=16)
    def get_tag_template(self, name):
        self.__log_operation_start('GET Tag Template: %s', name)
        tag_template = self.__datacatalog.get_tag_template(name=name)
        self.__log_single_object_read_result(tag_template)
        return tag_template

    @lru_cache(maxsize=64)
    def lookup_entry(self, linked_resource):
        self.__log_operation_start('LOOKUP Entry: %s', linked_resource)
        entry = self.__datacatalog.lookup_entry(linked_resource=linked_resource)
        self.__log_single_object_read_result(entry)
        return entry

    @classmethod
    def __log_operation_start(cls, message, *args):
        logging.info('')
        logging.info(message, *args)
        logging.info('--------------------------------------------------')

    @classmethod
    def __log_single_object_read_result(cls, the_object):
        logging.info('%sFound!' if the_object else '%sNOT found!', cls.__NESTED_LOG_PREFIX)
