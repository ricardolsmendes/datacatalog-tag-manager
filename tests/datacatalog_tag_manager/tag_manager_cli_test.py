import unittest
from unittest import mock

import datacatalog_tag_manager
from datacatalog_tag_manager import tag_manager_cli


class TagManagerCLITest(unittest.TestCase):
    __CLI_MODULE = 'datacatalog_tag_manager.tag_manager_cli'
    __CLI_CLASS = f'{__CLI_MODULE}.TagManagerCLI'

    @mock.patch(f'{__CLI_CLASS}._parse_args')
    def test_run_should_parse_args(self, mock_parse_args):
        tag_manager_cli.TagManagerCLI.run([])
        mock_parse_args.assert_called_once()

    @mock.patch(f'{__CLI_CLASS}._TagManagerCLI__upsert_tags')
    @mock.patch(f'{__CLI_CLASS}._parse_args')
    def test_run_upsert_tags_should_call_upsert_tags(self, mock_parse_args, mock_upsert_tags):
        mock_parse_args.return_value.func = mock_upsert_tags
        tag_manager_cli.TagManagerCLI.run([])
        mock_upsert_tags.assert_called_once_with(mock_parse_args.return_value)

    @mock.patch(f'{__CLI_CLASS}._TagManagerCLI__delete_tags')
    @mock.patch(f'{__CLI_CLASS}._parse_args')
    def test_run_delete_tags_should_call_delete_tags(self, mock_parse_args, mock_delete_tags):
        mock_parse_args.return_value.func = mock_delete_tags
        tag_manager_cli.TagManagerCLI.run([])
        mock_delete_tags.assert_called_once_with(mock_parse_args.return_value)

    def test_parse_args_no_subcommand_should_raise_system_exit(self):
        self.assertRaises(SystemExit, tag_manager_cli.TagManagerCLI._parse_args,
                          ['--csv-file', 'test.csv'])

    def test_parse_args_invalid_subcommand_should_raise_system_exit(self):
        self.assertRaises(SystemExit, tag_manager_cli.TagManagerCLI._parse_args, ['create'])

    def test_parse_args_upsert_tags_missing_mandatory_args_should_raise_system_exit(self):
        self.assertRaises(SystemExit, tag_manager_cli.TagManagerCLI._parse_args, ['upsert'])

    def test_parse_args_upsert_tags_should_parse_mandatory_args(self):
        args = tag_manager_cli.TagManagerCLI._parse_args(['upsert', '--csv-file', 'test.csv'])
        self.assertEqual('test.csv', args.csv_file)

    @mock.patch(f'{__CLI_CLASS}._TagManagerCLI__upsert_tags')
    def test_parse_args_upsert_tags_should_set_default_function(self, mock_upsert_tags):
        args = tag_manager_cli.TagManagerCLI._parse_args(['upsert', '--csv-file', 'test.csv'])
        self.assertEqual(mock_upsert_tags, args.func)

    def test_parse_args_delete_tags_missing_mandatory_args_should_raise_system_exit(self):
        self.assertRaises(SystemExit, tag_manager_cli.TagManagerCLI._parse_args, ['delete'])

    def test_parse_args_delete_tags_should_parse_mandatory_args(self):
        args = tag_manager_cli.TagManagerCLI._parse_args(['delete', '--csv-file', 'test.csv'])
        self.assertEqual('test.csv', args.csv_file)

    @mock.patch(f'{__CLI_CLASS}._TagManagerCLI__delete_tags')
    def test_parse_args_delete_tags_should_set_default_function(self, mock_delete_tags):
        args = tag_manager_cli.TagManagerCLI._parse_args(['delete', '--csv-file', 'test.csv'])
        self.assertEqual(mock_delete_tags, args.func)

    @mock.patch(f'{__CLI_MODULE}.tag_datasource_processor.TagDatasourceProcessor')
    def test_upsert_tags_should_upsert_tags_from_csv(self, mock_tag_datasource_processor):
        tag_manager_cli.TagManagerCLI.run(['upsert', '--csv-file', 'test.csv'])
        mock_tag_datasource_processor.assert_called_with()
        mock_tag_datasource_processor.return_value.upsert_tags_from_csv.assert_called_with(
            file_path='test.csv')

    @mock.patch(f'{__CLI_MODULE}.tag_datasource_processor.TagDatasourceProcessor')
    def test_delete_tags_should_delete_tags_from_csv(self, mock_tag_datasource_processor):
        tag_manager_cli.TagManagerCLI.run(['delete', '--csv-file', 'test.csv'])
        mock_tag_datasource_processor.assert_called_with()
        mock_tag_datasource_processor.return_value.delete_tags_from_csv.assert_called_with(
            file_path='test.csv')

    @mock.patch(f'{__CLI_CLASS}.run')
    def test_main_should_call_cli_run(self, mock_run):
        datacatalog_tag_manager.main()
        mock_run.assert_called_once()
