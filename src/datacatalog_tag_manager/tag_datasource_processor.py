import logging
import math
from typing import List

from google.api_core import exceptions
from google.cloud.datacatalog import types
import pandas as pd

from . import constant, datacatalog_entity_factory, datacatalog_facade


class TagDatasourceProcessor:

    def __init__(self):
        self.__datacatalog_facade = datacatalog_facade.DataCatalogFacade()

    def upsert_tags_from_csv(self, file_path: str) -> List[types.Tag]:
        """
        Upsert Tags by reading information from a CSV file.

        :param file_path: The CSV file path.
        :return: A list with all upserted Tags.
        """
        logging.info('')
        logging.info('===> Upsert Tags from CSV [STARTED]')

        logging.info('')
        logging.info('Reading CSV file: %s...', file_path)
        dataframe = pd.read_csv(file_path)

        logging.info('')
        logging.info('Upserting the Tags...')
        upserted_tags = self.__process_tags_from_dataframe(
            dataframe, processor=self.__datacatalog_facade.upsert_tag)

        logging.info('')
        logging.info('==== Upsert Tags from CSV [FINISHED] =============')

        return upserted_tags

    def delete_tags_from_csv(self, file_path: str) -> List[str]:
        """
        Delete Tags by reading information from a CSV file.

        :param file_path: The CSV file path.
        :return: A list with all Tags deleted.
        """
        logging.info('')
        logging.info('===> Delete Tags from CSV [STARTED]')

        logging.info('')
        logging.info('Reading CSV file: %s...', file_path)
        dataframe = pd.read_csv(file_path)

        logging.info('')
        logging.info('Deleting the Tags...')
        deleted_tag_names = self.__process_tags_from_dataframe(
            dataframe, processor=self.__datacatalog_facade.delete_tag)

        logging.info('')
        logging.info('==== Delete Tags from CSV [FINISHED] =============')

        return deleted_tag_names

    def __process_tags_from_dataframe(self, dataframe, processor):
        normalized_df = self.__normalize_dataframe(dataframe)
        normalized_df.set_index(constant.TAGS_DS_LINKED_RESOURCE_COLUMN_LABEL, inplace=True)

        results = []
        for linked_resource in normalized_df.index.unique().tolist():
            try:
                catalog_entry = self.__datacatalog_facade.lookup_entry(linked_resource)
            except exceptions.PermissionDenied:
                logging.warning(
                    'Permission denied when looking up Entry for %s.'
                    ' The resource will be skipped.', linked_resource)
                continue

            templates_subset = \
                normalized_df.loc[[linked_resource], constant.TAGS_DS_TEMPLATE_NAME_COLUMN_LABEL:]

            # Save memory by deleting data already copied to a subset.
            normalized_df.drop(linked_resource, inplace=True)

            tags = self.__make_tags_from_templates_dataframe(templates_subset)

            results.extend([processor(catalog_entry.name, tag) for tag in tags])

        return results

    @classmethod
    def __normalize_dataframe(cls, dataframe):
        # Reorder dataframe columns.
        ordered_df = dataframe.reindex(columns=constant.TAGS_DS_COLUMNS_ORDER, copy=False)

        # Fill NA/NaN values by propagating the last valid observation forward to next valid.
        filled_subset = ordered_df[constant.TAGS_DS_FILLABLE_COLUMNS].fillna(method='pad')

        # Rebuild the dataframe by concatenating the fillable and non-fillable columns.
        rebuilt_df = pd.concat([filled_subset, ordered_df[constant.TAGS_DS_NON_FILLABLE_COLUMNS]],
                               axis=1)

        return rebuilt_df

    def __make_tags_from_templates_dataframe(self, dataframe):
        dataframe.set_index(constant.TAGS_DS_TEMPLATE_NAME_COLUMN_LABEL, inplace=True)

        tags = []
        for template_name in dataframe.index.unique().tolist():
            try:
                tag_template = self.__datacatalog_facade.get_tag_template(template_name)
            except exceptions.PermissionDenied:
                logging.warning(
                    'Permission denied when getting Tag Template %s.'
                    ' Unable to manage Tags using it.', template_name)
                continue

            columns_subset = \
                dataframe.loc[[template_name], constant.TAGS_DS_SCHEMA_COLUMN_COLUMN_LABEL:]
            dataframe.drop(template_name, inplace=True)

            # (1) Make Tags to be attached/deleted to/from the resource

            # Get a subset with no schema/column information
            null_columns_index = \
                columns_subset[constant.TAGS_DS_SCHEMA_COLUMN_COLUMN_LABEL].isnull()
            null_columns_subset = \
                columns_subset.loc[null_columns_index, constant.TAGS_DS_FIELD_ID_COLUMN_LABEL:]

            if not null_columns_subset.empty:
                columns_subset.dropna(subset=[constant.TAGS_DS_SCHEMA_COLUMN_COLUMN_LABEL],
                                      inplace=True)
                tags.append(
                    self.__make_tag_from_fields_dataframe(tag_template, null_columns_subset))

            # (2) Make Tags to be attached/deleted to/from the resource's columns
            tags.extend(self.__make_tags_from_columns_dataframe(tag_template, columns_subset))

        return tags

    @classmethod
    def __make_tags_from_columns_dataframe(cls, tag_template, dataframe):
        dataframe.set_index(constant.TAGS_DS_SCHEMA_COLUMN_COLUMN_LABEL, inplace=True)

        tags = []
        # NaN not expected among index values at this point.
        for column_name in dataframe.index.unique().tolist():
            column_subset = dataframe.loc[[column_name], constant.TAGS_DS_FIELD_ID_COLUMN_LABEL:]
            dataframe.drop(column_name, inplace=True)

            tags.append(
                cls.__make_tag_from_fields_dataframe(tag_template, column_subset, column_name))

        return tags

    @classmethod
    def __make_tag_from_fields_dataframe(cls, tag_template, dataframe, column=None):
        return datacatalog_entity_factory.DataCatalogEntityFactory.make_tag(
            tag_template, cls.__convert_fields_dataframe_to_dict(dataframe), column)

    @classmethod
    def __convert_fields_dataframe_to_dict(cls, dataframe):
        # Remove the rows with no field id since they're not valid from this point
        dataframe.dropna(subset=[constant.TAGS_DS_FIELD_ID_COLUMN_LABEL], inplace=True)
        records = dataframe.to_dict(orient='records')

        id_to_value_map = {}
        for record in records:
            value = record[constant.TAGS_DS_FIELD_VALUE_COLUMN_LABEL]
            if isinstance(value, float) and math.isnan(value):
                continue

            id_to_value_map[record[constant.TAGS_DS_FIELD_ID_COLUMN_LABEL]] = value

        return id_to_value_map
