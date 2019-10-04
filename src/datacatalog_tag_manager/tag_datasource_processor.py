import pandas as pd

from .constant import *
from .datacatalog_entity_factory import DataCatalogEntityFactory
from .datacatalog_facade import DataCatalogFacade


class TagDatasourceProcessor:

    def __init__(self):
        self.__datacatalog = DataCatalogFacade()

    def create_tags_from_csv(self, file_path):
        """
        Create Tags by reading information from a CSV file.

        :param file_path: The CSV file path.
        :return: A list with all Tags created.
        """
        return self.__create_tags_from_dataframe(pd.read_csv(file_path))

    def __create_tags_from_dataframe(self, dataframe):
        ordered_df = dataframe.reindex(columns=TAG_DS_COLUMNS_ORDER, copy=False)
        ordered_df.set_index(TAG_DS_LINKED_RESOURCE_COLUMN_LABEL, inplace=True)

        created_tags = []
        for linked_resource in ordered_df.index.unique().tolist():
            catalog_entry = self.__datacatalog.lookup_entry(linked_resource)

            # TODO Add Catalog Entry validation

            templates_subset = ordered_df.loc[linked_resource, TAG_DS_TEMPLATE_NAME_COLUMN_LABEL:]
            templates_subset.set_index(TAG_DS_TEMPLATE_NAME_COLUMN_LABEL, inplace=True)

            ordered_df.drop(linked_resource, inplace=True)  # Save memory by deleting data already copied to a subset.

            tags = self.__create_tags_from_templates_dataframe(templates_subset)

            created_tags.extend([self.__datacatalog.create_or_update_tag(catalog_entry.name, tag) for tag in tags])

        return created_tags

    def __create_tags_from_templates_dataframe(self, dataframe):
        tags = []
        for template_name in dataframe.index.unique().tolist():
            tag_template = self.__datacatalog.get_tag_template(template_name)

            # TODO Add Tag Template validation

            columns_subset = dataframe.loc[template_name, TAG_DS_SCHEMA_COLUMN_COLUMN_LABEL:]
            dataframe.drop(template_name, inplace=True)

            # (1) Add Tag to be attached to the resource

            # Get a subset with no schema/column information
            null_columns_index = columns_subset[TAG_DS_SCHEMA_COLUMN_COLUMN_LABEL].isnull()
            null_columns_subset = columns_subset.loc[null_columns_index, TAG_DS_FIELD_ID_COLUMN_LABEL:]

            if not null_columns_subset.empty:
                columns_subset.dropna(subset=[TAG_DS_SCHEMA_COLUMN_COLUMN_LABEL], inplace=True)
                tags.append(self.__create_tag_from_fields_dataframe(tag_template, null_columns_subset))

            # (2) Add Tags to be attached to resource's columns

            columns_subset.set_index(TAG_DS_SCHEMA_COLUMN_COLUMN_LABEL, inplace=True)

            tags.extend(self.__create_tags_from_columns_dataframe(tag_template, columns_subset))

        return tags

    @classmethod
    def __create_tags_from_columns_dataframe(cls, tag_template, dataframe):
        tags = []
        for column_name in dataframe.index.unique().tolist():  # NaN is not expected among index values at this point.
            column_subset = dataframe.loc[column_name, TAG_DS_FIELD_ID_COLUMN_LABEL:]
            dataframe.drop(column_name, inplace=True)

            tags.append(cls.__create_tag_from_fields_dataframe(tag_template, column_subset, column_name))

        return tags

    @classmethod
    def __create_tag_from_fields_dataframe(cls, tag_template, dataframe, column=None):
        return DataCatalogEntityFactory.make_tag(
            tag_template, cls.__convert_fields_dataframe_to_dict(dataframe), column)

    @classmethod
    def __convert_fields_dataframe_to_dict(cls, dataframe):
        base_dict = dataframe.to_dict(orient='records')

        id_to_value_map = {}
        for base_object in base_dict:
            id_to_value_map[base_object[TAG_DS_FIELD_ID_COLUMN_LABEL]] = base_object[TAG_DS_FIELD_VALUE_COLUMN_LABEL]

        return id_to_value_map
