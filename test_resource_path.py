import pytest
import os
import sys
from forensicVmClient import resource_path

def test_resource_path_in_dev_env(monkeypatch):
    # Mock the abspath function to always return '/path/to/development'
    monkeypatch.setattr(os.path, 'abspath', lambda x: '/path/to/development')

    # Delete _MEIPASS attribute from sys module
    if hasattr(sys, '_MEIPASS'):
        del sys._MEIPASS

    # Call the function
    result = resource_path('relative')

    # Assert the expected result
    expected_path = os.path.join('/path/to/development', 'relative')
    assert result == expected_path

def test_resource_path_in_pyinstaller_env(monkeypatch):
    # Mock the _MEIPASS attribute
    monkeypatch.setattr(sys, '_MEIPASS', '/path/to/meipass')

    # Call the function
    result = resource_path('relative')

    # Assert the expected result
    expected_path = os.path.join('/path/to/meipass', 'relative')
    assert result == expected_path
