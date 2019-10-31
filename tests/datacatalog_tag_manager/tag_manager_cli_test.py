import unittest
from unittest import mock

import datacatalog_tag_manager


class TagManagerCLITest(unittest.TestCase):
    __PATCHED_TAG_DATASOURCE_PROCESSOR = 'datacatalog_tag_manager.tag_manager_cli' \
                                         '.tag_datasource_processor.TagDatasourceProcessor'

    def test_parse_args_invalid_subcommand_should_raise_system_exit(self):
        self.assertRaises(SystemExit, datacatalog_tag_manager.TagManagerCLI._parse_args, ['invalid-subcommand'])

    def test_parse_args_create_tags_missing_mandatory_args_should_raise_system_exit(self):
        self.assertRaises(SystemExit, datacatalog_tag_manager.TagManagerCLI._parse_args, ['create-tags'])

    def test_parse_args_create_tags_should_parse_mandatory_args(self):
        args = datacatalog_tag_manager.TagManagerCLI._parse_args(['create-tags', '--csv-file', 'test.csv'])
        self.assertEqual('test.csv', args.csv_file)

    def test_run_no_args_should_raise_attribute_error(self):
        self.assertRaises(AttributeError, datacatalog_tag_manager.TagManagerCLI.run, None)

    @mock.patch(f'{__PATCHED_TAG_DATASOURCE_PROCESSOR}.__init__', lambda self: None)
    @mock.patch(f'{__PATCHED_TAG_DATASOURCE_PROCESSOR}.create_tags_from_csv')
    def test_run_create_tags_should_call_tag_creator(self, mock_create_tags_from_csv):
        datacatalog_tag_manager.TagManagerCLI.run(['create-tags', '--csv-file', 'test.csv'])

        mock_create_tags_from_csv.assert_called_once()
        mock_create_tags_from_csv.assert_called_with(file_path='test.csv')
