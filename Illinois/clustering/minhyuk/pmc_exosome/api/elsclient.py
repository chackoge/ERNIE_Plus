"""A Python module that provides the API client component for the elsapy package.
    Additional resources:
    * https://github.com/ElsevierDev/elsapy
    * https://dev.elsevier.com
    * https://api.elsevier.com"""

import pprint
import requests, json, time
from . import log_util

from . import version

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

pp = pprint.PrettyPrinter(width=80, compact=True)


class ElsClient:
    """A class that implements a Python interface to api.elsevier.com"""

    # class variables
    __url_base = "https://api.elsevier.com/"    ## Base URL for later use
    __user_agent = "elsapy-v%s" % version       ## Helps track library use
    __min_req_interval = 1                      ## Min. request interval in sec
    __ts_last_req = time.time()                 ## Tracker for throttling
 
    # constructors
    def __init__(self, api_key, inst_token=None, num_res=500, output_dir = None, log_dir=None):
        # TODO: make num_res configurable for searches and documents/authors view
        #   - see https://github.com/ElsevierDev/elsapy/issues/32
        """Initializes a client with a given API Key and, optionally, institutional
            token, number of results per request, and local data path."""
        self.output_dir = pathlib.Path(output_dir)
        self.log_dir = pathlib.Path(log_dir)
        self.api_key = api_key
        self.inst_token = inst_token
        self.num_res = num_res
        self.logger = log_util.get_logger(self.log_dir)

    # properties
    @property
    def api_key(self):
        """Get the apiKey for the client instance"""
        return self._api_key
    @api_key.setter
    def api_key(self, api_key):
        """Set the apiKey for the client instance"""
        self._api_key = api_key

    @property
    def inst_token(self):
        """Get the instToken for the client instance"""
        return self._inst_token
    @inst_token.setter
    def inst_token(self, inst_token):
        """Set the instToken for the client instance"""
        self._inst_token = inst_token

    @property
    def num_res(self):
        """Gets the max. number of results to be used by the client instance"""
        return self._num_res
    
    @num_res.setter
    def num_res(self, numRes):
        """Sets the max. number of results to be used by the client instance"""
        self._num_res = numRes

    @property
    def output_dir(self):
        """Gets the currently configured output path to write data to."""
        return self._output_dir

    @property
    def log_dir(self):
        """Gets the currently configured log path to write data to."""
        return self._log_dir

    @property
    def req_status(self):
    	'''Return the status of the request response, '''
    	return {'status_code': self._status_code, 'status_msg': self._status_msg}

    @output_dir.setter
    def output_dir(self, path_str):
        """Sets the output path to write data to."""
        self._output_dir = pathlib.Path(path_str)

    @log_dir.setter
    def log_dir(self, path_str):
        """Sets the local path to write data to."""
        self._log_dir = pathlib.Path(path_str)

    # access functions
    def getBaseURL(self):
        """Returns the ELSAPI base URL currently configured for the client"""
        return self.__url_base

    # request/response execution functions
    def exec_request(self, URL, query_parameters):
        """Sends the actual request; returns response."""

        ## Throttle request, if need be
        interval = time.time() - self.__ts_last_req
        if (interval < self.__min_req_interval):
            time.sleep( self.__min_req_interval - interval )
        ## Construct and execute request
        headers = {
            "X-ELS-APIKey"  : self.api_key,
            "User-Agent"    : self.__user_agent,
            "Accept"        : 'application/json'
            }
        if self.inst_token:
            headers["X-ELS-Insttoken"] = self.inst_token
        self.logger.info('Sending GET request to ' + URL)
        r = requests.get(
            URL,
            headers = headers,
            params = query_parameters,
            )
        self.logger.info(r.request.url)
        self.logger.info(r.request.body)
        self.logger.info(r.request.headers)
        self.__ts_last_req = time.time()
        self._status_code=r.status_code
        if r.status_code == 200:
            self._status_msg='data retrieved'
            return json.loads(r.text)
        else:
            self._status_msg="HTTP " + str(r.status_code) + " Error from " + URL + " and using headers " + str(headers) + ": " + r.text
            raise requests.HTTPError("HTTP " + str(r.status_code) + " Error from " + URL + "\nand using headers " + str(headers) + ":\n" + r.text)
