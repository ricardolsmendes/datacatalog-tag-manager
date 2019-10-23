import pandas as pd

from unittest import TestCase
from unittest.mock import patch

from google.api_core.exceptions import PermissionDenied
from google.cloud.datacatalog import enums, types

from datacatalog_tag_manager import TagDatasourceProcessor


_PATCHED_DATACATALOG_FACADE = 'datacatalog_tag_manager.tag_datasource_processor.DataCatalogFacade'


@patch(f'{_PATCHED_DATACATALOG_FACADE}.__init__', lambda self: None)
class TagDatasourceProcessorTest(TestCase):
    __PATCHED_PANDAS = 'datacatalog_tag_manager.tag_datasource_processor.pd'

    def test_constructor_should_set_instance_attributes(self):
        self.assertIsNotNone(TagDatasourceProcessor().__dict__['_TagDatasourceProcessor__datacatalog_facade'])

    @patch(f'{_PATCHED_DATACATALOG_FACADE}.create_or_update_tag', lambda self, *args: args[1])
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.get_tag_template', lambda self, *args: make_fake_tag_template())
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.lookup_entry', lambda self, *args: make_fake_entry())
    @patch(f'{__PATCHED_PANDAS}.read_csv')
    def test_create_tags_from_csv_should_succeed(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(data={
            'linked_resource': ['//resource-link'],
            'template_name': ['test_template'],
            'field_id': ['string_field'],
            'field_value': ['Test value']
        })

        created_tags = TagDatasourceProcessor().create_tags_from_csv(None)
        self.assertEqual(1, len(created_tags))

        created_tag = created_tags[0]
        self.assertEqual('test_template', created_tag.template)
        self.assertEqual('Test value', created_tag.fields['string_field'].string_value)

    @patch(f'{_PATCHED_DATACATALOG_FACADE}.create_or_update_tag', lambda self, *args: args[1])
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.get_tag_template', lambda self, *args: make_fake_tag_template())
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.lookup_entry', lambda self, *args: make_fake_entry())
    @patch(f'{__PATCHED_PANDAS}.read_csv')
    def test_create_tags_from_csv_missing_values_should_succeed(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(data={
            'linked_resource': ['//resource-link-1', None, '//resource-link-2', None],
            'template_name': ['test_template', None, 'test_template', None],
            'field_id': ['bool_field', 'string_field', 'bool_field', 'string_field'],
            'field_value': ['true', 'Test value 1', 'false', 'Test value 2']
        })

        created_tags = TagDatasourceProcessor().create_tags_from_csv(None)
        self.assertEqual(2, len(created_tags))

        created_tag_1 = created_tags[0]
        self.assertEqual('test_template', created_tag_1.template)
        self.assertTrue(created_tag_1.fields['bool_field'].bool_value)
        self.assertEqual('Test value 1', created_tag_1.fields['string_field'].string_value)

        created_tag_2 = created_tags[1]
        self.assertEqual('test_template', created_tag_2.template)
        self.assertFalse(created_tag_2.fields['bool_field'].bool_value)
        self.assertEqual('Test value 2', created_tag_2.fields['string_field'].string_value)

    @patch(f'{_PATCHED_DATACATALOG_FACADE}.create_or_update_tag', lambda self, *args: args[1])
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.get_tag_template', lambda self, *args: make_fake_tag_template())
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.lookup_entry', lambda self, *args: make_fake_entry())
    @patch(f'{__PATCHED_PANDAS}.read_csv')
    def test_create_tags_from_csv_unordered_columns_should_succeed(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(data={
            'field_id': ['string_field'],
            'template_name': ['test_template'],
            'field_value': ['Test value'],
            'linked_resource': ['//resource-link']
        })

        created_tags = TagDatasourceProcessor().create_tags_from_csv(None)
        self.assertEqual(1, len(created_tags))

        created_tag = created_tags[0]
        self.assertEqual('test_template', created_tag.template)
        self.assertEqual('Test value', created_tag.fields['string_field'].string_value)

    @patch(f'{_PATCHED_DATACATALOG_FACADE}.create_or_update_tag', lambda self, *args: args[1])
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.get_tag_template', lambda self, *args: make_fake_tag_template())
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.lookup_entry', lambda self, *args: make_fake_entry())
    @patch(f'{__PATCHED_PANDAS}.read_csv')
    def test_create_tags_from_csv_column_metadata_should_succeed(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(data={
            'linked_resource': ['//resource-link', '//resource-link'],
            'template_name': ['test_template', 'test_template'],
            'column': ['test_column', None],
            'field_id': ['bool_field', 'string_field'],
            'field_value': ['true', 'Test value']
        })

        created_tags = TagDatasourceProcessor().create_tags_from_csv(None)
        self.assertEqual(2, len(created_tags))

        created_tag_1 = created_tags[0]  # Tags with no column information are created first.
        self.assertEqual('', created_tag_1.column)
        self.assertFalse('bool_field' in created_tag_1.fields)
        self.assertEqual('Test value', created_tag_1.fields['string_field'].string_value)

        created_tag_2 = created_tags[1]
        self.assertEqual('test_column', created_tag_2.column)
        self.assertTrue(created_tag_2.fields['bool_field'].bool_value)
        self.assertFalse('string_field' in created_tag_2.fields)

    @patch(f'{_PATCHED_DATACATALOG_FACADE}.create_or_update_tag', lambda self, *args: args[1])
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.get_tag_template', lambda self, *args: make_fake_tag_template())
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.lookup_entry')
    @patch(f'{__PATCHED_PANDAS}.read_csv')
    def test_create_tags_from_csv_permission_denied_lookup_entry_should_skip_resource(
            self, mock_read_csv, mock_lookup_entry):

        mock_read_csv.return_value = pd.DataFrame(data={
            'linked_resource': ['//unreachable-resource-link', '//resource-link'],
            'template_name': [None, 'test_template'],
            'field_id': [None, 'string_field'],
            'field_value': [None, 'Test value']
        })

        mock_lookup_entry.side_effect = [PermissionDenied(message=''), make_fake_entry()]

        created_tags = TagDatasourceProcessor().create_tags_from_csv(None)
        self.assertEqual(1, len(created_tags))

        created_tag = created_tags[0]
        self.assertEqual('test_template', created_tag.template)
        self.assertEqual('Test value', created_tag.fields['string_field'].string_value)

    @patch(f'{_PATCHED_DATACATALOG_FACADE}.create_or_update_tag', lambda self, *args: args[1])
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.get_tag_template')
    @patch(f'{_PATCHED_DATACATALOG_FACADE}.lookup_entry', lambda self, *args: make_fake_entry())
    @patch(f'{__PATCHED_PANDAS}.read_csv')
    def test_create_tags_from_csv_permission_denied_get_template_should_skip_template(
            self, mock_read_csv, mock_get_tag_template):

        mock_read_csv.return_value = pd.DataFrame(data={
            'linked_resource': ['//resource-link', '//resource-link'],
            'template_name': ['unreachable_test_template', 'test_template'],
            'field_id': [None, 'string_field'],
            'field_value': [None, 'Test value']
        })

        mock_get_tag_template.side_effect = [PermissionDenied(message=''), make_fake_tag_template()]

        created_tags = TagDatasourceProcessor().create_tags_from_csv(None)
        self.assertEqual(1, len(created_tags))

        created_tag = created_tags[0]
        self.assertEqual('test_template', created_tag.template)
        self.assertEqual('Test value', created_tag.fields['string_field'].string_value)


def make_fake_entry():
    entry = types.Entry()
    entry.name = 'test_entry'

    return entry


def make_fake_tag_template():
    tag_template = types.TagTemplate()
    tag_template.name = 'test_template'
    tag_template.fields['bool_field'].type.primitive_type = enums.FieldType.PrimitiveType.BOOL
    tag_template.fields['string_field'].type.primitive_type = enums.FieldType.PrimitiveType.STRING

    return tag_template
