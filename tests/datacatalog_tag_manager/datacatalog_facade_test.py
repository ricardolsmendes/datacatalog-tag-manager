from unittest import TestCase
from unittest.mock import patch

from google.cloud.datacatalog import types

from datacatalog_tag_manager.datacatalog_facade import DataCatalogFacade

_PATCHED_DATACATALOG_CLIENT = 'datacatalog_tag_manager.datacatalog_facade.DataCatalogClient'


@patch(f'{_PATCHED_DATACATALOG_CLIENT}.__init__', lambda self: None)
class DataCatalogFacadeTest(TestCase):

    def test_constructor_should_set_instance_attributes(self):
        self.assertIsNotNone(DataCatalogFacade().__dict__['_DataCatalogFacade__datacatalog'])

    @patch(f'{_PATCHED_DATACATALOG_CLIENT}.create_tag')
    @patch(f'{_PATCHED_DATACATALOG_CLIENT}.list_tags')
    def test_create_or_update_tag_nonexistent_should_create(self, mock_list_tags, mock_create_tag):
        mock_list_tags.return_value = []

        DataCatalogFacade().create_or_update_tag(None, None)

        mock_list_tags.assert_called_once()
        mock_create_tag.assert_called_once()

    @patch(f'{_PATCHED_DATACATALOG_CLIENT}.update_tag')
    @patch(f'{_PATCHED_DATACATALOG_CLIENT}.list_tags')
    def test_create_or_update_tag_pre_existing_should_update(self, mock_list_tags, mock_update_tag):
        tag_1 = make_fake_tag()

        tag_2 = make_fake_tag()
        tag_2.fields['test-string-field'].string_value = '[UPDATED] Test String Value'

        mock_list_tags.return_value = [tag_1]

        DataCatalogFacade().create_or_update_tag(None, tag_2)

        mock_list_tags.assert_called_once()
        mock_update_tag.assert_called_once()
        mock_update_tag.assert_called_with(tag=tag_2)

    @patch(f'{_PATCHED_DATACATALOG_CLIENT}.get_tag_template')
    def test_get_tag_template_should_call_client_library_method(self, mock_get_tag_template):
        DataCatalogFacade().get_tag_template(None)
        mock_get_tag_template.assert_called_once()

    @patch(f'{_PATCHED_DATACATALOG_CLIENT}.lookup_entry')
    def test_lookup_entry_should_call_client_library_method(self, mock_lookup_entry):
        DataCatalogFacade().lookup_entry(None)
        mock_lookup_entry.assert_called_once()


def make_fake_tag():
    tag = types.Tag()
    tag.template = 'test-template'
    tag.fields['test-bool-field'].bool_value = True
    tag.fields['test-double-field'].double_value = 1
    tag.fields['test-string-field'].string_value = 'Test String Value'
    tag.fields['test-timestamp-field'].timestamp_value.FromJsonString('2019-10-15T01:00:00-03:00')
    tag.fields['test-enum-field'].enum_value.display_name = 'Test ENUM Value'

    return tag
