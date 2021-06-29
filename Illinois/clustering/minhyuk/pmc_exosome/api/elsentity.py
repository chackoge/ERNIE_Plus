"""The (abstract) base entity module for elsapy. Used by elsprofile, elsdoc.
    Additional resources:
    * https://github.com/ElsevierDev/elsapy
    * https://dev.elsevier.com
    * https://api.elsevier.com"""

import requests, json, urllib
from abc import ABCMeta, abstractmethod


class ElsEntity(metaclass=ABCMeta):
    """An abstract class representing an entity in Elsevier's data model"""

    # constructors
    @abstractmethod
    def __init__(self, uri, doi=None):
        """Initializes a data entity with its URI"""
        self._uri = uri
        self._doi = doi
        self._data = None
        self._client = None

    # properties
    @property
    def uri(self):
        """Get the URI of the entity instance"""
        return self._uri

    @property
    def doi(self):
        """Get the doi of the entity instance"""
        return self._doi

    @uri.setter
    def uri(self, uri):
        """Set the URI of the entity instance"""
        self._uri = uri
    
    @property
    def id(self):
        """Get the dc:identifier of the entity instance"""
        return self.data["coredata"]["dc:identifier"]
    
    @property
    def int_id(self):
        """Get the (non-URI, numbers only) ID of the entity instance"""
        dc_id = self.data["coredata"]["dc:identifier"]
        return dc_id[dc_id.find(':') + 1:]

    @property
    def data(self):
        """Get the full JSON data for the entity instance"""
        return self._data

    @property
    def client(self):
        """Get the elsClient instance currently used by this entity instance"""
        return self._client

    @client.setter
    def client(self, elsClient):
        """Set the elsClient instance to be used by thisentity instance"""
        self._client = elsClient

    @doi.setter
    def doi(self, doi):
        """Set the doi to be used by thisentity instance"""
        self._doi = doi

    # modifier functions
    @abstractmethod
    def read(self, payloadType, elsClient, query_parameters):
        """Fetches the latest data for this entity from api.elsevier.com.
            Returns True if successful; else, False."""
        if elsClient:
            self._client = elsClient;
        elif not self.client:
            raise ValueError('''Entity object not currently bound to elsClient instance. Call .read() with elsClient argument or set .client attribute.''')
        try:
            api_response = self.client.exec_request(self.uri, query_parameters)
            if isinstance(api_response[payloadType], list):
                self._data = api_response[payloadType][0]
            else:
                self._data = api_response[payloadType]
            ## TODO: check if URI is the same, if necessary update and log warning.
            self._client.logger.info("Data loaded for " + self.uri)
            return True
        except (requests.HTTPError, requests.RequestException) as e:
            for elm in e.args:
                self._client.logger.warning(elm)
            return False

    @abstractmethod
    def read_json(self, payloadType, elsClient, filepath):
        """Fetches the latest data for this entity from api.elsevier.com.
            Returns True if successful; else, False."""
        if elsClient:
            self._client = elsClient;
        elif not self.client:
            raise ValueError('''Entity object not currently bound to elsClient instance. Call .read() with elsClient argument or set .client attribute.''')
        try:
            with open(filepath) as f:
                self._data= json.load(f)
            ## TODO: check if URI is the same, if necessary update and log warning.
            self._client.logger.info("Data loaded for " + self.uri)
            return True
        except Exception as e:
            self._client.logger.warning(e)
            return False

    def get_datapath(self):
        return self.client.output_dir / str("elsentity-" + self.id +'.json')
        # return self.client.output_dir / (urllib.parse.quote_plus(self.uri)+'.json')

    def write(self):
        """If data exists for the entity, writes it to disk as a .JSON file with
             the url-encoded URI as the filename and returns True. Else, returns
             False."""
        if (self.data):
            dataPath = self.get_datapath()
            with dataPath.open(mode='w') as dump_file:
                json.dump(self.data, dump_file)
                dump_file.close()
            self._client.logger.info('Wrote ' + self.uri + ' to file')
            return True
        else:
            self._client.logger.warning('No data to write for ' + self.uri)
            return False
