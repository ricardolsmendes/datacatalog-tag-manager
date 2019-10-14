from unittest import TestCase
from unittest.mock import patch

from datacatalog_tag_manager.datacatalog_facade import DataCatalogFacade

_PATCHED_DATACATALOG_CLIENT = 'datacatalog_tag_manager.datacatalog_facade.datacatalog_v1beta1.DataCatalogClient'


@patch(f'{_PATCHED_DATACATALOG_CLIENT}.__init__', lambda self: None)
class DataCatalogFacadeTest(TestCase):

    def test_constructor_should_set_instance_attributes(self):
        self.assertIsNotNone(DataCatalogFacade().__dict__['_DataCatalogFacade__datacatalog'])
