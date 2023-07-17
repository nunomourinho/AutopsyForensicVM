import pytest
import requests_mock
from forensicVMClient import remove_vm_datetime

def test_remove_vm_datetime_success():
    base_url = 'http://example.com'
    uuid = '123456'
    api_key = 'abc123'
    url = f"{base_url}/api/remove_vm_datetime/"
    headers = {'X-API-KEY': api_key}
    data = {'uuid': uuid}

    with requests_mock.Mocker() as m:
        m.post(url, status_code=200, json={'message': 'Success'})
        result = remove_vm_datetime(base_url, uuid, api_key)
        assert result == True

def test_remove_vm_datetime_failure():
    base_url = 'http://example.com'
    uuid = '123456'
    api_key = 'abc123'
    url = f"{base_url}/api/remove_vm_datetime/"
    headers = {'X-API-KEY': api_key}
    data = {'uuid': uuid}

    with requests_mock.Mocker() as m:
        m.post(url, status_code=400, json={'message': 'Failure'})
        result = remove_vm_datetime(base_url, uuid, api_key)
        assert result == False
