from datetime import datetime
import logging
from typing import Dict

from google.cloud import datacatalog
from google.cloud.datacatalog import Tag, TagTemplate
from google.protobuf import timestamp_pb2


class DataCatalogEntityFactory:
    __DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    __TRUTHS = {1, '1', 't', 'T', 'true', 'True', 'TRUE'}

    @classmethod
    def make_tag(cls,
                 tag_template: TagTemplate,
                 fields: Dict[str, object],
                 column: str = None) -> Tag:

        tag = datacatalog.Tag()

        tag.template = tag_template.name
        if column:
            tag.column = column

        cls.__set_tag_fields(tag, tag_template, fields)

        return tag

    @classmethod
    def __set_tag_fields(cls, tag: Tag, tag_template: TagTemplate, fields: Dict[str, object]):
        valid_fields = cls.__get_valid_tag_fields(tag_template, fields)
        for field_id, field_value in valid_fields.items():
            field = datacatalog.TagField()
            field_type = tag_template.fields[field_id].type_
            cls.__set_field_value(field, field_type, field_value)
            tag.fields[field_id] = field

    @classmethod
    def __get_valid_tag_fields(cls, tag_template: TagTemplate,
                               fields: Dict[str, object]) -> Dict[str, object]:

        valid_fields = {}

        if not fields:
            return valid_fields

        for field_id, field_value in fields.items():
            if field_id in tag_template.fields:
                valid_fields[field_id] = field_value
            else:
                logging.warning(
                    'Field %s (%s) was not found in the Tag Template %s and will be ignored.',
                    field_id, str(field_value), tag_template.name)

        return valid_fields

    @classmethod
    def __set_field_value(cls, field, template_field_type, value):
        set_primitive_field_value_functions = {
            datacatalog.FieldType.PrimitiveType.BOOL: cls.__set_bool_field_value,
            datacatalog.FieldType.PrimitiveType.DOUBLE: cls.__set_double_field_value,
            datacatalog.FieldType.PrimitiveType.STRING: cls.__set_string_field_value,
            datacatalog.FieldType.PrimitiveType.TIMESTAMP: cls.__set_timestamp_field_value
        }

        primitive_type = template_field_type.primitive_type

        if cls.__is_primitive_type_specified(primitive_type):
            set_primitive_field_value_functions[primitive_type](field, value)
        else:
            cls.__set_enum_field_value(field, value)

    @classmethod
    def __is_primitive_type_specified(cls, primitive_type):
        return datacatalog.FieldType.PrimitiveType.PRIMITIVE_TYPE_UNSPECIFIED != primitive_type

    @classmethod
    def __set_bool_field_value(cls, field, value):
        """
        :param field: The field.
        :param value: A boolean or:
            - boolean-like string value {'0', 'f', 'false', '1', 't', 'true'};
            - boolean-like int value {0, 1}.
        """
        field.bool_value = value if isinstance(value, bool) else value in cls.__TRUTHS

    @classmethod
    def __set_double_field_value(cls, field, value):
        """
        :param field: The field.
        :param value: A number or number-like string value.
        """
        field.double_value = value if isinstance(value, (int, float, complex)) else float(value)

    @classmethod
    def __set_enum_field_value(cls, field, value):
        """
        :param field: The field.
        :param value: A string value.
        """
        field.enum_value.display_name = value

    @classmethod
    def __set_string_field_value(cls, field, value):
        """
        :param field: The field.
        :param value: A string value.
        """
        field.string_value = value

    @classmethod
    def __set_timestamp_field_value(cls, field, value):
        """
        :param field: The field.
        :param value: A datetime or datetime-like string value.
        """
        dt = datetime.strptime(value, cls.__DATETIME_FORMAT) if isinstance(value, str) else value
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(dt)
        field.timestamp_value = timestamp
