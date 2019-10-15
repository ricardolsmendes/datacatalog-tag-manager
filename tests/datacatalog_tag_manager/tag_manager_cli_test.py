from unittest import TestCase
from unittest.mock import patch

from datacatalog_tag_manager import TagManagerCLI

_PATCHED_TAG_DATASOURCE_PROCESSOR = 'datacatalog_tag_manager.tag_manager_cli.TagDatasourceProcessor'


@patch(f'{_PATCHED_TAG_DATASOURCE_PROCESSOR}.__init__', lambda self: None)
class TagManagerCLITest(TestCase):

    def test_parse_args_with_invalid_subcommand_should_throw_system_exit(self):
        self.assertRaises(SystemExit, TagManagerCLI.parse_args, ['invalid-subcommand'])

    def test_parse_args_create_tags_missing_mandatory_args_should_throw_system_exit(self):
        self.assertRaises(SystemExit, TagManagerCLI.parse_args, ['create-tags'])

    def test_parse_args_create_tags_should_parse_mandatory_args(self):
        args = TagManagerCLI.parse_args(['create-tags', '--csv-file', 'test.csv'])
        self.assertEqual('test.csv', args.csv_file)

    def test_run_with_no_args_should_throw_attribute_error(self):
        self.assertRaises(AttributeError, TagManagerCLI.run, None)

    @patch(f'{_PATCHED_TAG_DATASOURCE_PROCESSOR}.create_tags_from_csv')
    def test_run_create_tags_should_call_tag_creator(self, mock_create_tags_from_csv):
        TagManagerCLI.run(['create-tags', '--csv-file', 'test.csv'])

        mock_create_tags_from_csv.assert_called_once()
        mock_create_tags_from_csv.assert_called_with(file_path='test.csv')
