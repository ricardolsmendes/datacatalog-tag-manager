from google.cloud import datacatalog_v1beta1


class DataCatalogFacade:
    """Data Catalog API communication facade."""

    def __init__(self):
        # Initialize the API client.
        self.__datacatalog = datacatalog_v1beta1.DataCatalogClient()

    def create_tag(self, parent_entry_name, tag):
        return self.__datacatalog.create_tag(parent=parent_entry_name, tag=tag)

    def get_tag_template(self, name):
        return self.__datacatalog.get_tag_template(name)

    def lookup_entry(self, linked_resource):
        return self.__datacatalog.lookup_entry(linked_resource=linked_resource)
