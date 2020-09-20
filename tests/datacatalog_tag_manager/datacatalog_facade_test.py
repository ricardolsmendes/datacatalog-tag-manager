import unittest
from unittest import mock

from google.cloud.datacatalog import types

from datacatalog_tag_manager import datacatalog_facade


class DataCatalogFacadeTest(unittest.TestCase):

    @mock.patch('datacatalog_tag_manager.datacatalog_facade.datacatalog.DataCatalogClient')
    def setUp(self, mock_datacatalog_client):
        self.__datacatalog_facade = datacatalog_facade.DataCatalogFacade()
        # Shortcut for the object assigned to self.__datacatalog_facade.__datacatalog
        self.__datacatalog_client = mock_datacatalog_client.return_value

    def test_constructor_should_set_instance_attributes(self):
        self.assertIsNotNone(self.__datacatalog_facade.__dict__['_DataCatalogFacade__datacatalog'])

    def test_upsert_tag_nonexistent_should_create(self):
        datacatalog = self.__datacatalog_client
        datacatalog.list_tags.return_value = []

        self.__datacatalog_facade.upsert_tag('entry_name', make_fake_tag())

        datacatalog.list_tags.assert_called_once()
        datacatalog.create_tag.assert_called_once()

    def test_upsert_tag_pre_existing_should_update(self):
        tag_1 = make_fake_tag()

        tag_2 = make_fake_tag()
        tag_2.fields['test_string_field'].string_value = '[UPDATED] Test String Value'

        datacatalog = self.__datacatalog_client
        datacatalog.list_tags.return_value = [tag_1]

        self.__datacatalog_facade.upsert_tag('entry_name', tag_2)

        datacatalog.list_tags.assert_called_once()
        datacatalog.update_tag.assert_called_once()
        datacatalog.update_tag.assert_called_with(tag=tag_2)

    def test_delete_tag_should_call_client_library_method(self):
        tag = make_fake_tag()

        tag_name = 'my_tag_name'
        existent_tag = make_fake_tag()
        existent_tag.name = tag_name

        datacatalog = self.__datacatalog_client
        datacatalog.list_tags.return_value = [existent_tag]

        self.__datacatalog_facade.delete_tag('entry_name', tag)

        datacatalog = self.__datacatalog_client
        datacatalog.list_tags.assert_called_once()
        datacatalog.delete_tag.assert_called_with(name=tag_name)

    def test_delete_tag_nonexistent_should_not_call_delete(self):
        tag = make_fake_tag()

        datacatalog = self.__datacatalog_client
        datacatalog.list_tags.return_value = []

        self.__datacatalog_facade.delete_tag('entry_name', tag)

        datacatalog = self.__datacatalog_client
        datacatalog.list_tags.assert_called_once()
        datacatalog.delete_tag.assert_not_called()

    def test_get_tag_template_should_call_client_library_method(self):
        self.__datacatalog_facade.get_tag_template('')

        datacatalog = self.__datacatalog_client
        datacatalog.get_tag_template.assert_called_once()

    def test_lookup_entry_should_call_client_library_method(self):
        self.__datacatalog_facade.lookup_entry('linked-resource')

        datacatalog = self.__datacatalog_client
        datacatalog.lookup_entry.assert_called_once()


def make_fake_tag():
    tag = types.Tag()
    tag.template = 'test_template'
    tag.fields['test_bool_field'].bool_value = True
    tag.fields['test_double_field'].double_value = 1
    tag.fields['test_string_field'].string_value = 'Test String Value'
    tag.fields['test_timestamp_field'].timestamp_value.FromJsonString('2019-10-15T01:00:00-03:00')
    tag.fields['test_enum_field'].enum_value.display_name = 'Test ENUM Value'

    return tag
