from datetime import datetime

from google.cloud import datacatalog_v1beta1


class DataCatalogEntityFactory:
    __TRUTHS = {1, '1', 't', 'T', 'true', 'True', 'TRUE'}

    @classmethod
    def make_tag(cls, tag_template, fields_map, column=None):
        tag = datacatalog_v1beta1.types.Tag()

        tag.template = tag_template.name
        if column:
            tag.column = column

        # TODO Add Template vs. Tag fields validation

        cls.__set_tag_fields(tag, tag_template, fields_map)

        return tag

    @classmethod
    def __set_tag_fields(cls, tag, tag_template, fields_map):
        for field_id, field_value in fields_map.items():
            field = tag.fields[field_id]
            field_type = tag_template.fields[field_id].type
            cls.__set_field_value(field, field_type, field_value)

    @classmethod
    def __set_field_value(cls, field, template_field_type, value):
        set_primitive_field_value_functions = {
            cls.__get_primitive_field_type_for('BOOL'): cls.__set_bool_field_value,
            cls.__get_primitive_field_type_for('DOUBLE'): cls.__set_double_field_value,
            cls.__get_primitive_field_type_for('STRING'): cls.__set_string_field_value,
            cls.__get_primitive_field_type_for('TIMESTAMP'): cls.__set_timestamp_field_value
        }

        primitive_type = template_field_type.primitive_type

        if cls.__is_primitive_type_specified(primitive_type):
            set_primitive_field_value_functions[primitive_type](field, value)
        else:
            cls.__set_enum_field_value(field, value)

    @classmethod
    def __get_primitive_field_type_for(cls, string):
        try:
            return datacatalog_v1beta1.enums.FieldType.PrimitiveType[string.upper()]
        except KeyError:
            return None

    @classmethod
    def __is_primitive_type_specified(cls, primitive_type):
        return datacatalog_v1beta1.enums.FieldType.PrimitiveType.PRIMITIVE_TYPE_UNSPECIFIED != primitive_type

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
        :param value: A number of number-like string value.
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
        :param value: A datetime of datetime-like string value.
        """
        dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z') if isinstance(value, str) else value
        field.timestamp_value.FromDatetime(dt)
