import unittest
from unittest import mock

from google.api_core import exceptions
from google.cloud import datacatalog
from google.cloud.datacatalog import FieldType
import pandas as pd

import datacatalog_tag_manager


@mock.patch('datacatalog_tag_manager.tag_datasource_processor.pd.read_csv')
class TagDatasourceProcessorTest(unittest.TestCase):
    __EMPTY_VALUE = float('NaN')

    @mock.patch(
        'datacatalog_tag_manager.tag_datasource_processor.datacatalog_facade.DataCatalogFacade')
    def setUp(self, mock_datacatalog_facade):
        self.__tag_datasource_processor = datacatalog_tag_manager.TagDatasourceProcessor()
        # Shortcut for the object assigned to self.__tag_datasource_processor.__datacatalog_facade
        self.__datacatalog_facade = mock_datacatalog_facade.return_value

    def test_constructor_should_set_instance_attributes(self, mock_read_csv):
        self.assertIsNotNone(self.__tag_datasource_processor.
                             __dict__['_TagDatasourceProcessor__datacatalog_facade'])

    def test_upsert_tags_from_csv_should_succeed(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(
            data={
                'linked_resource OR entry_name': ['//resource-link'],
                'template_name': ['test_template'],
                'field_id': ['string_field'],
                'field_value': ['Test value']
            })

        datacatalog_facade = self.__datacatalog_facade
        datacatalog_facade.lookup_entry.return_value = make_fake_entry()
        datacatalog_facade.get_tag_template.return_value = make_fake_tag_template()
        datacatalog_facade.upsert_tag.side_effect = lambda *args: args[1]

        upserted_tags = self.__tag_datasource_processor.upsert_tags_from_csv('file-path')

        datacatalog_facade.delete_tag.assert_not_called()
        datacatalog_facade.upsert_tag.assert_called_once()

        self.assertEqual(1, len(upserted_tags))

        upserted_tag = upserted_tags[0]
        self.assertEqual('test_template', upserted_tag.template)
        self.assertEqual('Test value', upserted_tag.fields['string_field'].string_value)

    def test_upsert_tags_from_csv_missing_auto_fill_values_should_succeed(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(
            data={
                'linked_resource OR entry_name': [
                    '//bigquery.googleapis.com/resource-name-1', self.__EMPTY_VALUE,
                    '//bigquery.googleapis.com/resource-name-2', self.__EMPTY_VALUE
                ],
                'template_name':
                ['test_template', self.__EMPTY_VALUE, 'test_template', self.__EMPTY_VALUE],
                'field_id': ['bool_field', 'string_field', 'bool_field', 'string_field'],
                'field_value': ['true', 'Test value 1', 'false', 'Test value 2']
            })

        datacatalog_facade = self.__datacatalog_facade
        datacatalog_facade.lookup_entry.return_value = make_fake_entry()
        datacatalog_facade.get_tag_template.return_value = make_fake_tag_template()
        datacatalog_facade.upsert_tag.side_effect = lambda *args: args[1]

        upserted_tags = self.__tag_datasource_processor.upsert_tags_from_csv('file-path')
        self.assertEqual(2, len(upserted_tags))

        upserted_tag_1 = upserted_tags[0]
        self.assertEqual('test_template', upserted_tag_1.template)
        self.assertTrue(upserted_tag_1.fields['bool_field'].bool_value)
        self.assertEqual('Test value 1', upserted_tag_1.fields['string_field'].string_value)

        upserted_tag_2 = upserted_tags[1]
        self.assertEqual('test_template', upserted_tag_2.template)
        self.assertFalse(upserted_tag_2.fields['bool_field'].bool_value)
        self.assertEqual('Test value 2', upserted_tag_2.fields['string_field'].string_value)

    def test_upsert_tags_from_csv_unordered_columns_should_succeed(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(
            data={
                'field_id': ['string_field'],
                'template_name': ['test_template'],
                'field_value': ['Test value'],
                'linked_resource OR entry_name': ['//bigquery.googleapis.com/resource-name']
            })

        datacatalog_facade = self.__datacatalog_facade
        datacatalog_facade.lookup_entry.return_value = make_fake_entry()
        datacatalog_facade.get_tag_template.return_value = make_fake_tag_template()
        datacatalog_facade.upsert_tag.side_effect = lambda *args: args[1]

        upserted_tags = self.__tag_datasource_processor.upsert_tags_from_csv('file-path')
        self.assertEqual(1, len(upserted_tags))

        upserted_tag = upserted_tags[0]
        self.assertEqual('test_template', upserted_tag.template)
        self.assertEqual('Test value', upserted_tag.fields['string_field'].string_value)

    def test_upsert_tags_from_csv_column_metadata_should_succeed(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(
            data={
                'linked_resource OR entry_name': [
                    '//bigquery.googleapis.com/resource-name',
                    '//bigquery.googleapis.com/resource-name'
                ],
                'template_name': ['test_template', 'test_template'],
                'column': ['test_column', self.__EMPTY_VALUE],
                'field_id': ['bool_field', 'string_field'],
                'field_value': ['true', 'Test value']
            })

        datacatalog_facade = self.__datacatalog_facade
        datacatalog_facade.lookup_entry.return_value = make_fake_entry()
        datacatalog_facade.get_tag_template.return_value = make_fake_tag_template()
        datacatalog_facade.upsert_tag.side_effect = lambda *args: args[1]

        upserted_tags = self.__tag_datasource_processor.upsert_tags_from_csv('file-path')
        self.assertEqual(2, len(upserted_tags))

        upserted_tag_1 = upserted_tags[0]  # Tags with no column information are created first.
        self.assertEqual('', upserted_tag_1.column)
        self.assertFalse('bool_field' in upserted_tag_1.fields)
        self.assertEqual('Test value', upserted_tag_1.fields['string_field'].string_value)

        upserted_tag_2 = upserted_tags[1]
        self.assertEqual('test_column', upserted_tag_2.column)
        self.assertTrue(upserted_tag_2.fields['bool_field'].bool_value)
        self.assertFalse('string_field' in upserted_tag_2.fields)

    def test_upsert_tags_from_csv_should_skip_nan_field_values(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(
            data={
                'linked_resource OR entry_name':
                ['//bigquery.googleapis.com/resource-name', self.__EMPTY_VALUE],
                'template_name': ['test_template', self.__EMPTY_VALUE],
                'field_id': ['bool_field', 'string_field'],
                'field_value': ['true', self.__EMPTY_VALUE]
            })

        datacatalog_facade = self.__datacatalog_facade
        datacatalog_facade.lookup_entry.return_value = make_fake_entry()
        datacatalog_facade.get_tag_template.return_value = make_fake_tag_template()
        datacatalog_facade.upsert_tag.side_effect = lambda *args: args[1]

        upserted_tags = self.__tag_datasource_processor.upsert_tags_from_csv('file-path')
        self.assertEqual(1, len(upserted_tags))

        upserted_tag = upserted_tags[0]
        self.assertTrue('bool_field' in upserted_tag.fields)
        self.assertFalse('string_field' in upserted_tag.fields)

    def test_upsert_tags_from_csv_invalid_argument_lookup_entry_should_skip_tag(
            self, mock_read_csv):

        mock_read_csv.return_value = pd.DataFrame(
            data={
                'linked_resource OR entry_name': [
                    '//bigquery.googleapis.com/invalid-resource-name',
                    '//bigquery.googleapis.com/resource-name'
                ],
                'template_name': [self.__EMPTY_VALUE, 'test_template'],
                'field_id': [self.__EMPTY_VALUE, 'string_field'],
                'field_value': [self.__EMPTY_VALUE, 'Test value']
            })

        datacatalog_facade = self.__datacatalog_facade
        datacatalog_facade.lookup_entry.side_effect = \
            (exceptions.InvalidArgument(message=''), make_fake_entry())
        datacatalog_facade.get_tag_template.return_value = make_fake_tag_template()
        datacatalog_facade.upsert_tag.side_effect = lambda *args: args[1]

        upserted_tags = self.__tag_datasource_processor.upsert_tags_from_csv('file-path')
        self.assertEqual(1, len(upserted_tags))

        upserted_tag = upserted_tags[0]
        self.assertEqual('test_template', upserted_tag.template)
        self.assertEqual('Test value', upserted_tag.fields['string_field'].string_value)

    def test_upsert_tags_from_csv_permission_denied_lookup_entry_should_skip_tag(
            self, mock_read_csv):

        mock_read_csv.return_value = pd.DataFrame(
            data={
                'linked_resource OR entry_name': [
                    '//bigquery.googleapis.com/unreachable-resource-name',
                    '//bigquery.googleapis.com/resource-name'
                ],
                'template_name': [self.__EMPTY_VALUE, 'test_template'],
                'field_id': [self.__EMPTY_VALUE, 'string_field'],
                'field_value': [self.__EMPTY_VALUE, 'Test value']
            })

        datacatalog_facade = self.__datacatalog_facade
        datacatalog_facade.lookup_entry.side_effect = \
            (exceptions.PermissionDenied(message=''), make_fake_entry())
        datacatalog_facade.get_tag_template.return_value = make_fake_tag_template()
        datacatalog_facade.upsert_tag.side_effect = lambda *args: args[1]

        upserted_tags = self.__tag_datasource_processor.upsert_tags_from_csv('file-path')
        self.assertEqual(1, len(upserted_tags))

        upserted_tag = upserted_tags[0]
        self.assertEqual('test_template', upserted_tag.template)
        self.assertEqual('Test value', upserted_tag.fields['string_field'].string_value)

    def test_upsert_tags_from_csv_permission_denied_get_entry_should_skip_tag(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(
            data={
                'linked_resource OR entry_name': ['invalid-entry-name', 'entry-name'],
                'template_name': [self.__EMPTY_VALUE, 'test_template'],
                'field_id': [self.__EMPTY_VALUE, 'string_field'],
                'field_value': [self.__EMPTY_VALUE, 'Test value']
            })

        datacatalog_facade = self.__datacatalog_facade
        datacatalog_facade.get_entry.side_effect = \
            (exceptions.PermissionDenied(message=''), make_fake_entry())
        datacatalog_facade.get_tag_template.return_value = make_fake_tag_template()
        datacatalog_facade.upsert_tag.side_effect = lambda *args: args[1]

        upserted_tags = self.__tag_datasource_processor.upsert_tags_from_csv('file-path')
        self.assertEqual(1, len(upserted_tags))

        upserted_tag = upserted_tags[0]
        self.assertEqual('test_template', upserted_tag.template)
        self.assertEqual('Test value', upserted_tag.fields['string_field'].string_value)

    def test_upsert_tags_from_csv_permission_denied_get_template_should_skip_tag(
            self, mock_read_csv):

        mock_read_csv.return_value = pd.DataFrame(
            data={
                'linked_resource OR entry_name': [
                    '//bigquery.googleapis.com/resource-name',
                    '//bigquery.googleapis.com/resource-name'
                ],
                'template_name': ['unreachable_test_template', 'test_template'],
                'field_id': [self.__EMPTY_VALUE, 'string_field'],
                'field_value': [self.__EMPTY_VALUE, 'Test value']
            })

        datacatalog_facade = self.__datacatalog_facade
        datacatalog_facade.lookup_entry.return_value = make_fake_entry()
        datacatalog_facade.get_tag_template.side_effect = \
            (exceptions.PermissionDenied(message=''), make_fake_tag_template())
        datacatalog_facade.upsert_tag.side_effect = lambda *args: args[1]

        upserted_tags = self.__tag_datasource_processor.upsert_tags_from_csv('file-path')
        self.assertEqual(1, len(upserted_tags))

        upserted_tag = upserted_tags[0]
        self.assertEqual('test_template', upserted_tag.template)
        self.assertEqual('Test value', upserted_tag.fields['string_field'].string_value)

    def test_delete_tags_from_csv_should_succeed(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(
            data={
                'linked_resource OR entry_name': ['//bigquery.googleapis.com/resource-name'],
                'template_name': ['test_template']
            })

        tag_name = 'my_tag_name'
        datacatalog_facade = self.__datacatalog_facade
        datacatalog_facade.lookup_entry.return_value = make_fake_entry()
        datacatalog_facade.get_tag_template.return_value = make_fake_tag_template()
        datacatalog_facade.delete_tag.return_value = tag_name

        deleted_tag_names = self.__tag_datasource_processor.delete_tags_from_csv('file-path')

        datacatalog_facade.delete_tag.assert_called_once()
        datacatalog_facade.upsert_tag.assert_not_called()

        self.assertEqual(1, len(deleted_tag_names))

        deleted_tag_name = deleted_tag_names[0]
        self.assertEqual(tag_name, deleted_tag_name)


def make_fake_entry():
    entry = datacatalog.Entry()
    entry.name = 'test_entry'

    return entry


def make_fake_tag_template():
    tag_template = datacatalog.TagTemplate()
    tag_template.name = 'test_template'
    tag_template.fields['bool_field'] = \
        make_primitive_type_template_field(datacatalog.FieldType.PrimitiveType.BOOL)
    tag_template.fields['string_field'] = \
        make_primitive_type_template_field(datacatalog.FieldType.PrimitiveType.STRING)

    return tag_template


def make_primitive_type_template_field(primitive_type: FieldType.PrimitiveType):
    field = datacatalog.TagTemplateField()
    field.type.primitive_type = primitive_type

    return field
