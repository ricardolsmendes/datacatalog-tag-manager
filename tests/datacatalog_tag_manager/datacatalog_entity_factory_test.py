from datetime import datetime
import unittest

from google.cloud.datacatalog import enums, types

from datacatalog_tag_manager import datacatalog_entity_factory


class DataCatalogEntityFactoryTest(unittest.TestCase):
    __BOOL_TYPE = enums.FieldType.PrimitiveType.BOOL
    __DOUBLE_TYPE = enums.FieldType.PrimitiveType.DOUBLE
    __STRING_TYPE = enums.FieldType.PrimitiveType.STRING
    __TIMESTAMP_TYPE = enums.FieldType.PrimitiveType.TIMESTAMP

    def test_make_tag_should_set_column(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test_template'

        tag = datacatalog_entity_factory.DataCatalogEntityFactory.make_tag(tag_template, {}, 'test_column')

        self.assertEqual('test_column', tag.column)

    def test_make_tag_valid_boolean_values_should_set_fields(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test_template'
        tag_template.fields['test_bool_field'].type.primitive_type = self.__BOOL_TYPE
        tag_template.fields['test_bool_field_int'].type.primitive_type = self.__BOOL_TYPE
        tag_template.fields['test_bool_field_str'].type.primitive_type = self.__BOOL_TYPE

        tag_fields = {
            'test_bool_field': True,
            'test_bool_field_int': 1,
            'test_bool_field_str': 'T'
        }

        tag = datacatalog_entity_factory.DataCatalogEntityFactory.make_tag(tag_template, tag_fields)

        self.assertTrue(tag.fields['test_bool_field'].bool_value)
        self.assertTrue(tag.fields['test_bool_field_int'].bool_value)
        self.assertTrue(tag.fields['test_bool_field_str'].bool_value)

    def test_make_tag_valid_double_values_should_set_fields(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test_template'
        tag_template.fields['test_double_field'].type.primitive_type = self.__DOUBLE_TYPE
        tag_template.fields['test_double_field_str'].type.primitive_type = self.__DOUBLE_TYPE

        tag_fields = {
            'test_double_field': 2.5,
            'test_double_field_str': '3.1415'
        }

        tag = datacatalog_entity_factory.DataCatalogEntityFactory.make_tag(tag_template, tag_fields)

        self.assertEqual(2.5, tag.fields['test_double_field'].double_value)
        self.assertEqual(3.1415, tag.fields['test_double_field_str'].double_value)

    def test_make_tag_valid_string_value_should_set_field(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test_template'
        tag_template.fields['test_string_field'].type.primitive_type = self.__STRING_TYPE

        tag_fields = {
            'test_string_field': 'Test String Value'
        }

        tag = datacatalog_entity_factory.DataCatalogEntityFactory.make_tag(tag_template, tag_fields)

        self.assertEqual('Test String Value', tag.fields['test_string_field'].string_value)

    def test_make_tag_valid_timestamp_values_should_set_fields(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test_template'
        tag_template.fields['test_timestamp_field'].type.primitive_type = self.__TIMESTAMP_TYPE
        tag_template.fields['test_timestamp_field_str'].type.primitive_type = self.__TIMESTAMP_TYPE

        test_datetime = datetime.strptime('2019-10-15T21:30:00-0300', '%Y-%m-%dT%H:%M:%S%z')

        tag_fields = {
            'test_timestamp_field': test_datetime,
            'test_timestamp_field_str': '2019-10-15T21:30:00-0300'
        }

        tag = datacatalog_entity_factory.DataCatalogEntityFactory.make_tag(tag_template, tag_fields)

        self.assertEqual(test_datetime.timestamp(),
                         tag.fields['test_timestamp_field'].timestamp_value.seconds)
        self.assertEqual(test_datetime.timestamp(),
                         tag.fields['test_timestamp_field_str'].timestamp_value.seconds)

    def test_make_tag_valid_enum_value_should_set_field(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test_template'
        tag_template.fields['test_enum_field'].type.enum_type.allowed_values.add().display_name = 'VALUE_1'

        tag_fields = {
            'test_enum_field': 'VALUE_1'
        }

        tag = datacatalog_entity_factory.DataCatalogEntityFactory.make_tag(tag_template, tag_fields)

        self.assertEqual('VALUE_1', tag.fields['test_enum_field'].enum_value.display_name)

    def test_make_tag_should_ignore_invalid_field(self):
        tag_template = types.TagTemplate()
        tag_template.name = 'test_template'
        tag_template.fields['test_bool_field'].type.primitive_type = self.__BOOL_TYPE

        tag_fields = {
            'test_bool_field_invalid': True
        }

        tag = datacatalog_entity_factory.DataCatalogEntityFactory.make_tag(tag_template, tag_fields)

        self.assertFalse('test_bool_field' in tag.fields)
        self.assertFalse('test_bool_field_invalid' in tag.fields)
