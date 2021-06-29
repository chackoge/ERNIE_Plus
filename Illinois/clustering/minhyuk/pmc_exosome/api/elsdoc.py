"""The document module of elsapy.
    Additional resources:
    * https://github.com/ElsevierDev/elsapy
    * https://dev.elsevier.com
    * https://api.elsevier.com"""

from . import elsentity


class FullDoc(elsentity.ElsEntity):
    """A document in ScienceDirect. Initialize with PII or DOI."""

    # static variables
    __payload_type = u'full-text-retrieval-response'
    __uri_base = u'https://api.elsevier.com/content/article/'

    @property
    def title(self):
        """Gets the document's title"""
        return self.data["coredata"]["dc:title"];

    @property
    def uri(self):
        """Gets the document's uri"""
        return self._uri

    # constructors
    def __init__(self, uri = '', sd_pii = '', doi = ''):
        """Initializes a document given a ScienceDirect PII or DOI."""
        if uri and not sd_pii and not doi:
            super().__init__(uri)
        elif sd_pii and not uri and not doi:
            super().__init__(self.__uri_base + 'pii/' + str(sd_pii))
        elif doi and not uri and not sd_pii:
            super().__init__(self.__uri_base + 'doi/' + str(doi))
        elif not uri and not doi:
            raise ValueError('No URI, ScienceDirect PII or DOI specified')
        else:
            raise ValueError('Multiple identifiers specified; just need one.')

    # modifier functions
    def read(self, els_client = None):
        """Reads the JSON representation of the document from ELSAPI.
             Returns True if successful; else, False."""
        if super().read(self.__payload_type, els_client):
            return True
        else:
            return False

class AbsDoc(elsentity.ElsEntity):
    """A document in Scopus. Initialize with URI or Scopus ID."""

    # static variables
    __payload_type = u'abstracts-retrieval-response'
    __uri_base = u'https://api.elsevier.com/content/abstract/'

    @property
    def title(self):
        """Gets the document's title"""
        return self.data["coredata"]["dc:title"];

    @property
    def uri(self):
        """Gets the document's uri"""
        return self._uri

    # constructors
    def __init__(self, uri="", scp_id="", doi=""):
        """Initializes a document given a Scopus document URI, Scopus ID, or DOI."""
        if uri and not scp_id and not doi:
            super().__init__(uri)
        elif scp_id and not uri and not doi:
            super().__init__(self.__uri_base + 'scopus_id/' + str(scp_id))
        elif doi and not uri and not scp_id:
            super().__init__(self.__uri_base + 'doi/' + str(doi))
        elif not uri and not scp_i and not dio:
            raise ValueError('No URI, Scopus ID, or DOI specified')
        else:
            raise ValueError('Multiple identifiers specified; just need one.')

    # modifier functions
    def read(self, els_client=None, query_parameters=None):
        """Reads the JSON representation of the document from ELSAPI.
             Returns True if successful; else, False."""
        if super().read(self.__payload_type, els_client, query_parameters):
            return True
        else:
            return False


class ExtendedAbsDoc(elsentity.ElsEntity):
    """A document in Scopus. Initialize with URI or Scopus ID."""

    # static variables
    __payload_type = u'abstracts-retrieval-response'
    __uri_base = u'https://api.elsevier.com/content/abstract/'

    @property
    def title(self):
        """Gets the document's title"""
        return self.data["coredata"]["dc:title"];

    @property
    def uri(self):
        """Gets the document's uri"""
        return self._uri

    @property
    def doi(self):
        """Gets the document's doi"""
        return self._doi

    # constructors
    def __init__(self, uri="", scp_id="", doi=""):
        """Initializes a document given a Scopus document URI, Scopus ID, or DOI."""
        if uri and not scp_id and not doi:
            super().__init__(uri)
        elif scp_id and not uri and not doi:
            super().__init__(self.__uri_base + 'scopus_id/' + str(scp_id))
        elif doi and not uri and not scp_id:
            super().__init__(self.__uri_base + 'doi/' + str(doi), doi)
        elif not uri and not scp_i and not dio:
            raise ValueError('No URI, Scopus ID, or DOI specified')
        else:
            raise ValueError('Multiple identifiers specified; just need one.')

    # modifier functions
    def read(self, els_client=None, query_parameters=None):
        """Reads the JSON representation of the document from ELSAPI.
             Returns True if successful; else, False."""
        if super().read(self.__payload_type, els_client, query_parameters):
            return True
        else:
            return False

    def read_json(self, els_client=None, filepath=None):
        """Reads the JSON representation of the document from disk.
             Returns True if successful; else, False."""
        if super().read_json(self.__payload_type, els_client, filepath):
            return True
        else:
            return False

    def write(self):
        super().write()

        # if (self.data):
        #     dataPath = self.client.output_dir / (urllib.parse.quote_plus(self.)+'.json')
        #     with dataPath.open(mode='w') as dump_file:
        #         json.dump(self.data, dump_file)
        #         dump_file.close()
        #     self._client.logger.info('Wrote ' + self.uri + ' to file')
        #     return True
        # else:
        #     self._client.logger.warning('No data to write for ' + self.uri)
        #     return False

    def get_bibliography(self):
        bibliography = []
        tail_list = self.data["item"]["bibrecord"]["tail"]
        if(tail_list is not None):
            raw_list = tail_list["bibliography"]["reference"]
            for reference in raw_list:
                current_item_list = reference["ref-info"]["refd-itemidlist"]["itemid"]
                current_item = None
                if isinstance(current_item_list, list):
                    for item in current_item_list:
                        if(item["@idtype"] == "SGR"):
                            current_item = item
                else:
                    current_item = current_item_list
                bibliography.append((current_item["@idtype"], current_item["$"]))
        return bibliography
