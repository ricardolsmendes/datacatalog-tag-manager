from datetime import datetime
from unittest import TestCase

from google.cloud.datacatalog import enums, types

from datacatalog_tag_manager.datacatalog_entity_factory import DataCatalogEntityFactory


class DataCatalogEntityFactoryTest(TestCase):
    __BOOL_TYPE = enums.FieldType.PrimitiveType.BOOL
    __DOUBLE_TYPE = enums.FieldType.PrimitiveType.DOUBLE
    __STRING_TYPE = enums.FieldType.PrimitiveType.STRING
    __TIMESTAMP_TYPE = enums.FieldType.PrimitiveType.TIMESTAMP

    def test_make_tag_should_set_column(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test-template'

        tag = DataCatalogEntityFactory.make_tag(tag_template, None, 'test-column')

        self.assertEqual('test-column', tag.column)

    def test_make_tag_valid_boolean_values_should_set_fields(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test-template'
        tag_template.fields['test-bool-field'].type.primitive_type = self.__BOOL_TYPE
        tag_template.fields['test-bool-field-int'].type.primitive_type = self.__BOOL_TYPE
        tag_template.fields['test-bool-field-str'].type.primitive_type = self.__BOOL_TYPE

        tag_fields = {
            'test-bool-field': True,
            'test-bool-field-int': 1,
            'test-bool-field-str': 'T'
        }

        tag = DataCatalogEntityFactory.make_tag(tag_template, tag_fields, None)

        self.assertTrue(tag.fields['test-bool-field'].bool_value)
        self.assertTrue(tag.fields['test-bool-field-int'].bool_value)
        self.assertTrue(tag.fields['test-bool-field-str'].bool_value)

    def test_make_tag_valid_double_values_should_set_fields(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test-template'
        tag_template.fields['test-double-field'].type.primitive_type = self.__DOUBLE_TYPE
        tag_template.fields['test-double-field-str'].type.primitive_type = self.__DOUBLE_TYPE

        tag_fields = {
            'test-double-field': 2.5,
            'test-double-field-str': '3.1415'
        }

        tag = DataCatalogEntityFactory.make_tag(tag_template, tag_fields, None)

        self.assertEqual(2.5, tag.fields['test-double-field'].double_value)
        self.assertEqual(3.1415, tag.fields['test-double-field-str'].double_value)

    def test_make_tag_valid_string_value_should_set_field(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test-template'
        tag_template.fields['test-string-field'].type.primitive_type = self.__STRING_TYPE

        tag_fields = {
            'test-string-field': 'Test String Value'
        }

        tag = DataCatalogEntityFactory.make_tag(tag_template, tag_fields, None)

        self.assertEqual('Test String Value', tag.fields['test-string-field'].string_value)

    def test_make_tag_valid_timestamp_values_should_set_fields(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test-template'
        tag_template.fields['test-timestamp-field'].type.primitive_type = self.__TIMESTAMP_TYPE
        tag_template.fields['test-timestamp-field-str'].type.primitive_type = self.__TIMESTAMP_TYPE

        test_datetime = datetime.strptime('2019-10-15T21:30:00-0300', '%Y-%m-%dT%H:%M:%S%z')

        tag_fields = {
            'test-timestamp-field': test_datetime,
            'test-timestamp-field-str': '2019-10-15T21:30:00-0300'
        }

        tag = DataCatalogEntityFactory.make_tag(tag_template, tag_fields, None)

        self.assertEqual(test_datetime.timestamp(),
                         tag.fields['test-timestamp-field'].timestamp_value.seconds)
        self.assertEqual(test_datetime.timestamp(),
                         tag.fields['test-timestamp-field-str'].timestamp_value.seconds)

    def test_make_tag_valid_enum_value_should_set_field(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test-template'
        tag_template.fields['test-enum-field'].type.enum_type.allowed_values.add().display_name = 'VALUE_1'

        tag_fields = {
            'test-enum-field': 'VALUE_1'
        }

        tag = DataCatalogEntityFactory.make_tag(tag_template, tag_fields, None)

        self.assertEqual('VALUE_1', tag.fields['test-enum-field'].enum_value.display_name)

    def test_make_tag_should_ignore_invalid_field(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test-template'
        tag_template.fields['test-bool-field'].type.primitive_type = self.__BOOL_TYPE

        tag_fields = {
            'test-bool-field-invalid': True
        }

        tag = DataCatalogEntityFactory.make_tag(tag_template, tag_fields, None)

        self.assertFalse('test-bool-field' in tag.fields)
        self.assertFalse('test-bool-field-invalid' in tag.fields)
