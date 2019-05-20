# coding: utf-8
from datetime import datetime
from datetime import timedelta
import os
from pyDataverse.api import Api
from pyDataverse.exceptions import ApiResponseError
from pyDataverse.exceptions import ApiUrlError
from pyDataverse.utils import dict_to_json
from pyDataverse.utils import read_file_json
import pytest
from requests import Response


TEST_DIR = os.path.dirname(os.path.realpath(__file__))


if 'API_TOKEN' in os.environ:
    API_TOKEN = os.environ['API_TOKEN']
else:
    print('ERROR: Environment variable API_TOKEN for test missing.')
if 'BASE_URL' in os.environ:
    BASE_URL = os.environ['BASE_URL']
else:
    print('ERROR: Environment variable BASE_URL for test missing.')


class TestApiConnect(object):
    """Test the Api() class initalization."""

    def test_api_connect(self):
        """Test successfull connection without api_token."""
        api = Api(BASE_URL)
        time_window_start = datetime.now() - timedelta(seconds=10)
        assert isinstance(api, Api)
        assert not api.api_token
        assert api.api_version == 'v1'
        assert api.conn_started > time_window_start
        assert isinstance(api.conn_started, datetime)
        assert api.base_url == BASE_URL
        assert api.native_api_base_url == '{0}/api/{1}'.format(
            BASE_URL, api.api_version)
        assert api.status == 'OK'

    def test_api_connect_base_url_wrong(self):
        """Test api connection with wrong `base_url`."""
        # wrong string
        with pytest.raises(ApiResponseError):
            base_url = 'http://wikipedia.org'
            api = Api(base_url)
            time_window_start = datetime.now() - timedelta(seconds=10)
            assert not api.api_token
            assert api.api_version == 'v1'
            assert api.conn_started > time_window_start
            assert api.base_url == 'http://wikipedia.org'
            assert api.native_api_base_url == 'http://wikipedia.org/api/v1'
            assert api.status == 'ERROR'

        # None
        with pytest.raises(ApiUrlError):
            base_url = None
            api = Api(base_url)
            time_window_start = datetime.now() - timedelta(seconds=10)
            assert not api.api_token
            assert api.api_version == 'v1'
            assert api.conn_started > time_window_start
            assert not api.base_url
            assert not api.native_api_base_url
            assert api.status == 'ERROR'


class TestApiRequests(object):
    """Test the api requests."""

    dataset_id = None

    @classmethod
    def setup_class(cls):
        """Create the api connection for later use."""
        print('TEST setup_class', BASE_URL, API_TOKEN)
        cls.api = Api(BASE_URL, api_token=API_TOKEN)
        cls.dataverse_id = 'test-pyDataverse-3'
        cls.filename_dataverse = TEST_DIR+'/data/create_dataverse_3.json'
        cls.filename_dataset = TEST_DIR+'/data/create_dataset.json'
        assert cls.api
        assert cls.api.api_token
        assert cls.api.base_url

    def test_make_get_request(self):
        """Test successfull `.make_get_request()` request."""
        # TODO: test params und auth default
        query_str = '/info/server'
        resp = self.api.make_get_request(query_str)
        assert self.api.status == 'OK'
        assert isinstance(resp, Response)

    def test_create_dataverse(self):
        """Test successfull `.create_dataverse()` request`."""
        metadata = read_file_json(self.filename_dataverse)
        resp = self.api.create_dataverse(
            self.dataverse_id, dict_to_json(metadata))
        assert isinstance(resp, Response)
        assert self.api.get_dataverse(self.dataverse_id).json()

    def test_get_dataverse(self):
        """Test successfull `.get_dataverse()` request`."""
        resp = self.api.get_dataverse(self.dataverse_id)
        assert isinstance(resp, Response)

    def test_create_dataset(self):
        """Test successfull `.create_dataset()` request`."""
        metadata = read_file_json(self.filename_dataset)
        resp = self.api.create_dataset(
            self.dataverse_id, dict_to_json(metadata))
        TestApiRequests.dataset_id = resp.json()['data']['persistentId']
        assert isinstance(resp, Response)

    def test_get_dataset(self):
        """Test successfull `.get_dataset()` request`."""
        print(self.dataset_id)
        resp = self.api.get_dataset(TestApiRequests.dataset_id)
        assert isinstance(resp, Response)

    def test_delete_dataset(self):
        """Test successfull `.delete_dataset()` request`."""
        resp = self.api.delete_dataset(TestApiRequests.dataset_id)
        assert isinstance(resp, Response)

    def test_delete_dataverse(self):
        """Test successfull `.delete_dataverse()` request`."""
        resp = self.api.delete_dataverse(self.dataverse_id)
        assert isinstance(resp, Response)
