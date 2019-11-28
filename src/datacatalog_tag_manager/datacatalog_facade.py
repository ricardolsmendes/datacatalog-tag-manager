from google.cloud import datacatalog


class DataCatalogFacade:
    """Data Catalog API communication facade."""

    def __init__(self):
        # Initialize the API client.
        self.__datacatalog = datacatalog.DataCatalogClient()

    def create_or_update_tag(self, parent_entry_name, tag):
        entry_tags = self.__datacatalog.list_tags(parent=parent_entry_name)

        try:
            persisted_tag = next(
                entry_tag for entry_tag in entry_tags
                if entry_tag.template == tag.template and entry_tag.column == tag.column)
            tag.name = persisted_tag.name
            return self.__datacatalog.update_tag(tag=tag)
        except StopIteration:
            return self.__datacatalog.create_tag(parent=parent_entry_name, tag=tag)

    def get_tag_template(self, name):
        return self.__datacatalog.get_tag_template(name=name)

    def lookup_entry(self, linked_resource):
        return self.__datacatalog.lookup_entry(linked_resource=linked_resource)
