import logging
import math
import re
from typing import Dict, List, Optional

from google.api_core import exceptions
from google.cloud.datacatalog import Entry, Tag
import pandas as pd

from . import constant, datacatalog_entity_factory, datacatalog_facade


class TagDatasourceProcessor:

    def __init__(self):
        self.__datacatalog_facade = datacatalog_facade.DataCatalogFacade()

    def upsert_tags_from_csv(self, file_path: str) -> List[Tag]:
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
        normalized_df.set_index(constant.TAGS_DS_LINKED_RESOURCE_ENTRY_NAME_COLUMN_LABEL,
                                inplace=True)

        results = []
        for entry_name_or_resource in normalized_df.index.unique().tolist():
            catalog_entry = self.__find_entry(entry_name_or_resource)
            if not catalog_entry:
                logging.warning(
                    'No Entry found for name or linked resource %s.'
                    ' The record will be skipped.', entry_name_or_resource)
                continue

            templates_subset = \
                normalized_df.loc[
                    [entry_name_or_resource], constant.TAGS_DS_TEMPLATE_NAME_COLUMN_LABEL:
                ]

            # Save memory by deleting data already copied to a subset.
            normalized_df.drop(entry_name_or_resource, inplace=True)

            tags = self.__make_tags_from_templates_dataframe(templates_subset)

            results.extend([processor(catalog_entry.name, tag) for tag in tags])

        return results

    def __find_entry(self, name_or_resource: str) -> Optional[Entry]:
        should_use_lookup = re.match(pattern=constant.BIGQUERY_LINKED_RESOURCE_PATTERN,
                                     string=name_or_resource)
        should_use_lookup = should_use_lookup or re.match(
            pattern=constant.PUBSUB_LINKED_RESOURCE_PATTERN, string=name_or_resource)

        if should_use_lookup:
            try:
                return self.__datacatalog_facade.lookup_entry(name_or_resource)
            except exceptions.InvalidArgument:
                logging.warning('Invalid argument when looking up Entry for %s.', name_or_resource)
            except exceptions.PermissionDenied:
                logging.warning('Permission denied when looking up Entry for %s.',
                                name_or_resource)
            return

        try:
            return self.__datacatalog_facade.get_entry(name_or_resource)
        except exceptions.PermissionDenied:
            logging.warning('Permission denied when getting Entry %s.', name_or_resource)

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
    def __convert_fields_dataframe_to_dict(cls, dataframe) -> Dict[str, object]:
        # Remove the rows with no field id since they're not valid from this point
        dataframe.dropna(subset=[constant.TAGS_DS_FIELD_ID_COLUMN_LABEL], inplace=True)
        records = dataframe.to_dict(orient='records')

        fields = {}
        for record in records:
            value = record[constant.TAGS_DS_FIELD_VALUE_COLUMN_LABEL]
            # Pandas is not aware of the field types and reads empty values as NaN;
            # hence NaN fields are skipped.
            if isinstance(value, float) and math.isnan(value):
                continue

            fields[record[constant.TAGS_DS_FIELD_ID_COLUMN_LABEL]] = value

        return fields
