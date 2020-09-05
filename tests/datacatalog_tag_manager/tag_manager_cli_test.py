import unittest
from unittest import mock

import datacatalog_tag_manager
from datacatalog_tag_manager import tag_manager_cli


class TagManagerCLITest(unittest.TestCase):

    def test_parse_args_invalid_subcommand_should_raise_system_exit(self):
        self.assertRaises(SystemExit, tag_manager_cli.TagManagerCLI._parse_args,
                          ['invalid-subcommand'])

    def test_parse_args_create_tags_missing_mandatory_args_should_raise_system_exit(self):
        self.assertRaises(SystemExit, tag_manager_cli.TagManagerCLI._parse_args, ['create'])

    def test_parse_args_create_tags_should_parse_mandatory_args(self):
        args = tag_manager_cli.TagManagerCLI._parse_args(['create', '--csv-file', 'test.csv'])
        self.assertEqual('test.csv', args.csv_file)

    def test_run_no_args_should_raise_attribute_error(self):
        self.assertRaises(AttributeError, tag_manager_cli.TagManagerCLI.run, None)

    @mock.patch(
        'datacatalog_tag_manager.tag_manager_cli.tag_datasource_processor.TagDatasourceProcessor')
    def test_run_create_tags_should_call_tag_creator(self, mock_tag_datasource_processor):
        tag_manager_cli.TagManagerCLI.run(['create', '--csv-file', 'test.csv'])

        tag_datasource_processor = mock_tag_datasource_processor.return_value
        tag_datasource_processor.create_tags_from_csv.assert_called_once()
        tag_datasource_processor.create_tags_from_csv.assert_called_with(file_path='test.csv')

    @mock.patch(
        'datacatalog_tag_manager.tag_manager_cli.tag_datasource_processor.TagDatasourceProcessor')
    def test_run_delete_tags_should_call_tag_creator(self, mock_tag_datasource_processor):
        tag_manager_cli.TagManagerCLI.run(['delete', '--csv-file', 'test.csv'])

        tag_datasource_processor = mock_tag_datasource_processor.return_value
        tag_datasource_processor.delete_tags_from_csv.assert_called_once()
        tag_datasource_processor.delete_tags_from_csv.assert_called_with(file_path='test.csv')

    @mock.patch('datacatalog_tag_manager.tag_manager_cli.TagManagerCLI')
    def test_main_should_call_cli_run(self, mock_cli):
        datacatalog_tag_manager.main()
        mock_cli.run.assert_called_once()
