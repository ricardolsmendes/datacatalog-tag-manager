import logging
import pandas as pd

from google.api_core.exceptions import PermissionDenied

from .constant import TAGS_DS_FIELD_ID_COLUMN_LABEL, TAGS_DS_FIELD_VALUE_COLUMN_LABEL,\
    TAGS_DS_LINKED_RESOURCE_COLUMN_LABEL, TAGS_DS_SCHEMA_COLUMN_COLUMN_LABEL, TAGS_DS_TEMPLATE_NAME_COLUMN_LABEL,\
    TAGS_DS_COLUMNS_ORDER, TAGS_DS_FILLABLE_COLUMNS, TAGS_DS_NON_FILLABLE_COLUMNS
from .datacatalog_entity_factory import DataCatalogEntityFactory
from .datacatalog_facade import DataCatalogFacade


class TagDatasourceProcessor:

    def __init__(self):
        self.__datacatalog_facade = DataCatalogFacade()

    def create_tags_from_csv(self, file_path):
        """
        Create Tags by reading information from a CSV file.

        :param file_path: The CSV file path.
        :return: A list with all Tags created.
        """
        return self.__create_tags_from_dataframe(pd.read_csv(file_path))

    def __create_tags_from_dataframe(self, dataframe):
        normalized_df = self.__normalize_dataframe(dataframe)
        normalized_df.set_index(TAGS_DS_LINKED_RESOURCE_COLUMN_LABEL, inplace=True)

        created_tags = []
        for linked_resource in normalized_df.index.unique().tolist():
            try:
                catalog_entry = self.__datacatalog_facade.lookup_entry(linked_resource)
            except PermissionDenied:
                logging.warning('Permission denied when looking up Entry for %s.'
                                ' The resource will be skipped.', linked_resource)
                continue

            templates_subset = normalized_df.loc[[linked_resource], TAGS_DS_TEMPLATE_NAME_COLUMN_LABEL:]
            templates_subset.set_index(TAGS_DS_TEMPLATE_NAME_COLUMN_LABEL, inplace=True)

            # Save memory by deleting data already copied to a subset.
            normalized_df.drop(linked_resource, inplace=True)

            tags = self.__create_tags_from_templates_dataframe(templates_subset)

            created_tags.extend([self.__datacatalog_facade.create_or_update_tag(catalog_entry.name, tag)
                                 for tag in tags])

        return created_tags

    @classmethod
    def __normalize_dataframe(cls, dataframe):
        # Reorder dataframe columns.
        ordered_df = dataframe.reindex(columns=TAGS_DS_COLUMNS_ORDER, copy=False)

        # Fill NA/NaN values by propagating the last valid observation forward to next valid.
        filled_subset = ordered_df[TAGS_DS_FILLABLE_COLUMNS].fillna(method='pad')

        # Rebuild the dataframe by concatenating the fillable and non-fillable columns.
        rebuilt_df = pd.concat([filled_subset, ordered_df[TAGS_DS_NON_FILLABLE_COLUMNS]], axis=1)

        return rebuilt_df

    def __create_tags_from_templates_dataframe(self, dataframe):
        tags = []
        for template_name in dataframe.index.unique().tolist():
            try:
                tag_template = self.__datacatalog_facade.get_tag_template(template_name)
            except PermissionDenied:
                logging.warning('Permission denied when getting Tag Template %s.'
                                ' Unable to create Tags using it.', template_name)
                continue

            columns_subset = dataframe.loc[[template_name], TAGS_DS_SCHEMA_COLUMN_COLUMN_LABEL:]
            dataframe.drop(template_name, inplace=True)

            # (1) Add Tag to be attached to the resource

            # Get a subset with no schema/column information
            null_columns_index = columns_subset[TAGS_DS_SCHEMA_COLUMN_COLUMN_LABEL].isnull()
            null_columns_subset = columns_subset.loc[null_columns_index, TAGS_DS_FIELD_ID_COLUMN_LABEL:]

            if not null_columns_subset.empty:
                columns_subset.dropna(subset=[TAGS_DS_SCHEMA_COLUMN_COLUMN_LABEL], inplace=True)
                tags.append(self.__create_tag_from_fields_dataframe(tag_template, null_columns_subset))

            # (2) Add Tags to be attached to resource's columns

            columns_subset.set_index(TAGS_DS_SCHEMA_COLUMN_COLUMN_LABEL, inplace=True)

            tags.extend(self.__create_tags_from_columns_dataframe(tag_template, columns_subset))

        return tags

    @classmethod
    def __create_tags_from_columns_dataframe(cls, tag_template, dataframe):
        tags = []
        for column_name in dataframe.index.unique().tolist():  # NaN not expected among index values at this point.
            column_subset = dataframe.loc[[column_name], TAGS_DS_FIELD_ID_COLUMN_LABEL:]
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
            id_to_value_map[base_object[TAGS_DS_FIELD_ID_COLUMN_LABEL]] = base_object[TAGS_DS_FIELD_VALUE_COLUMN_LABEL]

        return id_to_value_map
