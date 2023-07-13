import re
import json
import uuid
import paramiko
import PySimpleGUI as sg
import webbrowser
import threading
import ctypes
import time
import os
import sys
import subprocess
import requests
from datetime import datetime
from requests_toolbelt import MultipartEncoder
from urllib.parse import urljoin

def remove_vm_datetime(base_url, uuid, api_key):
    """
    Removes the datetime for a virtual machine specified by UUID.

    Args:
        base_url (str): The base URL of the API.
        uuid (str): The UUID of the virtual machine.
        api_key (str): The API key for authentication.

    Returns:
        bool: True if the datetime was successfully removed, False otherwise.
    """
    url = f"{base_url}/api/remove_vm_datetime/"
    headers = {'X-API-KEY': api_key}
    data = {'uuid': uuid}

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        print('Success:', response.json())
        return True
    else:
        print('Failed:', response.json())
        return False

def change_vm_datetime(base_url, uuid, datetime_str, api_key):
    """
    Changes the datetime for a virtual machine specified by UUID.

    Args:
        base_url (str): The base URL of the API.
        uuid (str): The UUID of the virtual machine.
        datetime_str (str): The new datetime in string format.
        api_key (str): The API key for authentication.

    Returns:
        bool: True if the datetime was successfully changed, False otherwise.
    """
    url = f"{base_url}/api/change_vm_datetime/"
    headers = {'X-API-KEY': api_key}
    data = {'uuid': uuid, 'datetime': datetime_str}
    print(headers)

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        print('Success:', response.json())
        return True
    else:
        print('Failed:', response.json())
        return False

def download_pcap(api_key, uuid, base_url, output_file):
    """
    Downloads pcap files identified by UUID using the API endpoint and saves them to a local file.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the screenshots to download.
        base_url (str): The base URL of the API.
        output_file (str): The path of the output file to save the downloaded pcap files.

    Returns:
        bool: True if the pcap files were downloaded successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `uuid`, `base_url`, `output_file`) is missing.
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: If an unexpected error occurs during the download.

    Example:
        >>> download_pcap('your_api_key', 'screenshots_uuid', 'https://example.com', 'output_file.zip')
        Pcap downloaded to output_file.zip
        True
    """
    assert api_key, "API key is required"
    assert uuid, "UUID is required"
    assert base_url, "Base URL is required"
    assert output_file, "Output file is required"

    url = f"{base_url}/api/download_pcap/{uuid}/"
    headers = {"X-API-KEY": api_key}

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('Content-Length', 0))
        bytes_downloaded = 0

        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
                    bytes_downloaded += len(chunk)

                    # Update the progress bar
                    sg.one_line_progress_meter(
                        "Downloading Pcap files",
                        bytes_downloaded,
                        total_size,
                        "key",
                        f"Downloaded {bytes_downloaded} / {total_size} bytes",
                    )
        print(f"Pcap files download downloaded to {output_file}")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False


def check_tap_interface(base_url, uuid, api_key):
    """
    Checks the status of the TAP interface for a virtual machine specified by UUID.

    Args:
        base_url (str): The base URL of the API.
        uuid (str): The UUID of the virtual machine.
        api_key (str): The API key for authentication.

    Returns:
        Union[str, bool]: The status of the TAP interface if the request was successful, False otherwise.
    """
    try:
        # URL of the web service
        url = f"{base_url}/api/check_tap/"

        # The headers for the request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Api-Key': api_key
        }

        # The data to send in the request body
        data = {
            'uuid': uuid,
        }

        # Send the POST request
        response = requests.post(url, headers=headers, data=data)

        # Check the response
        if response.status_code == 200:
            response_json = response.json()
            return response_json['status']
        else:
            print(f"Error: {response.json()}")
            return False
    except Exception as e:
        return False

def stop_tap_interface(base_url, uuid, api_key):
    """
    Stops the TAP interface for a virtual machine specified by UUID.

    Args:
        base_url (str): The base URL of the API.
        uuid (str): The UUID of the virtual machine.
        api_key (str): The API key for authentication.

    Returns:
        bool: True if the TAP interface was successfully stopped, False otherwise.
    """
    # URL of the web service
    url = f"{base_url}/api/stop_tap/"

    # The headers for the request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Api-Key': api_key
    }

    # The data to send in the request body
    data = {
        'uuid': uuid,
    }

    # Send the POST request
    response = requests.post(url, headers=headers, data=data)

    # Check the response
    if response.status_code == 200:
        print(f"Success: {response.json()}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False


def start_tap_interface(base_url, uuid, api_key):
    """
    Starts the TAP interface for a virtual machine specified by UUID.

    Args:
        base_url (str): The base URL of the API.
        uuid (str): The UUID of the virtual machine.
        api_key (str): The API key for authentication.

    Returns:
        bool: True if the TAP interface was successfully started, False otherwise.
    """

    # URL of the web service
    url = f"{base_url}/api/start_tap/"

    # The headers for the request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Api-Key': api_key
    }

    # The data to send in the request body
    data = {
        'uuid': uuid,
    }

    # Send the POST request
    response = requests.post(url, headers=headers, data=data)

    # Check the response
    if response.status_code == 200:
        print(f"Success: {response.json()}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def get_available_memory(api_key, site_url):
    """
    Retrieves the available memory in megabytes from a specified API VM.

    Args:
        api_key (str): The API key required for authentication.
        site_url (str): The URL of the site to fetch the available memory from.

    Returns:
        float: The available memory in megabytes.

    Raises:
        None

    Example:
        >>> get_available_memory('your_api_key', 'https://example.com')
        Available Memory: 256.0 MB
        256.0
    """
    headers = {
        'X-API-Key': api_key,
    }
    endpoint = f"{site_url}/api/get-available-memory/"
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        available_memory = int(response.json().get('available_memory'))/1024
        print(f"Available Memory: {available_memory} MB")
        return(available_memory)
    else:
        print(f"Error: {response.text}")
        return(0)


def change_memory_size(api_key, site_url, uuid, memory_size):
    """
    Changes the memory size of a specified VM identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        site_url (str): The URL of the site where the VM is located.
        uuid (str): The UUID of the VM to modify.
        memory_size (int): The new memory size in megabytes.

    Returns:
        None

    Raises:
        None

    Example:
        >>> change_memory_size('your_api_key', 'https://example.com', 'resource_uuid', 512)
        Memory size updated successfully
    """
    headers = {
        'X-API-Key': api_key,
    }
    endpoint = f"{site_url}/api/change-memory-size/{uuid}/"
    payload = {
        'memory_size': int(memory_size),
    }
    response = requests.post(endpoint, headers=headers, data=payload)

    if response.status_code == 200:
        print("Memory size updated successfully")
    else:
        print(f"Error: {response.text}")

def get_memory_size(api_key, site_url, uuid):
    """
    Retrieves the memory size of a specified resource identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        site_url (str): The URL of the site where the resource is located.
        uuid (str): The UUID of the resource to fetch the memory size from.

    Returns:
        int: The memory size of the resource in megabytes.

    Raises:
        None

    Example:
        >>> get_memory_size('your_api_key', 'https://example.com', 'resource_uuid')
        1024
    """
    headers = {'X-API-KEY': api_key}
    url = f"{site_url}/api/get-memory-size/{uuid}/"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            memory_size = data['memory_size']
            return memory_size
        else:
            print(f"Error: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request Error: {str(e)}")

def delete_snapshot(api_key, site_url, uuid, snapshot_name):
    """
    Deletes a snapshot with the specified name for a resource identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        site_url (str): The URL of the site where the resource is located.
        uuid (str): The UUID of the resource from which to delete the snapshot.
        snapshot_name (str): The name of the snapshot to delete.

    Returns:
        str: A message indicating the success or failure of the snapshot deletion.

    Raises:
        None

    Example:
        >>> delete_snapshot('your_api_key', 'https://example.com', 'resource_uuid', 'snapshot_1')
        'Snapshot snapshot_1 deleted successfully'
    """
    url = f"{site_url}/api/delete-snapshot/{uuid}/"
    headers = {'X-API-KEY': api_key}
    data = {'snapshot_name': snapshot_name}

    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            data = response.json()
            message = data.get('message')
            return message
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return None
    
def rollback_snapshot(api_key, site_url, uuid, snapshot_name):
    """
    Rolls back a resource identified by UUID to a specific snapshot using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        site_url (str): The URL of the site where the resource is located.
        uuid (str): The UUID of the resource to rollback.
        snapshot_name (str): The name of the snapshot to rollback to.

    Returns:
        str: A message indicating the success or failure of the snapshot rollback.

    Raises:
        None

    Example:
        >>> rollback_snapshot('your_api_key', 'https://example.com', 'resource_uuid', 'snapshot_1')
        'Snapshot snapshot_1 rolled back successfully'
    """
    url = f"{site_url}/api/rollback-snapshot/{uuid}/"
    headers = {'X-API-KEY': api_key}
    data = {'snapshot_name': snapshot_name}

    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            data = response.json()
            message = data.get('message')
            return message
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return None
    
def create_snapshot(api_key, uuid_path, base_url):
    """
    Creates a snapshot for a resource identified by UUID path using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid_path (str): The UUID path of the resource for which to create a snapshot.
        base_url (str): The base URL of the API.

    Returns:
        str: The name of the created snapshot.

    Raises:
        None

    Example:
        >>> create_snapshot('your_api_key', 'resource_uuid_path', 'https://example.com')
        'snapshot_1'
    """
    url = urljoin(base_url, f"api/create-snapshot/{uuid_path}/")
    headers = {'X-API-KEY': api_key}

    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            snapshot_name = data.get('snapshot_name')
            return snapshot_name
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return None
    
def get_snapshot_list(api_key, uuid_path, base_url):
    """
    Retrieves the list of snapshots for a resource identified by UUID path using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid_path (str): The UUID path of the resource for which to retrieve the snapshot list.
        base_url (str): The base URL of the API.

    Returns:
        list: A list of snapshot names for the specified resource.

    Raises:
        None

    Example:
        >>> get_snapshot_list('your_api_key', 'resource_uuid_path', 'https://example.com')
        ['snapshot_1', 'snapshot_2', 'snapshot_3']
    """
    url = urljoin(base_url, f"api/snapshots-list/{uuid_path}/")
    headers = {'X-API-KEY': api_key}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            snapshots = data.get('snapshots')
            return snapshots
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return []

def insert_network_card(api_key, uuid_path, base_url):
    """
    Inserts a network card for a resource identified by UUID path using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid_path (str): The UUID path of the resource for which to insert the network card.
        base_url (str): The base URL of the API.

    Returns:
        None

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `base_url`, `uuid`) is missing.

    Example:
        >>> insert_network_card('your_api_key', 'resource_uuid_path', 'https://example.com')
        Network card inserted successfully.
    """
    assert api_key, "API key is required"
    assert base_url, "Base URL is required"
    assert uuid, "UUID is required"

    url = f'{base_url}/api/insert-network-card/{uuid_path}'
    print(url)

    headers = {'X-API-KEY': api_key}

    #data = {'uuid': uuid}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print('Network card inserted successfully.')
    else:
        print(f'Failed to insert network card. Error: {response.text}')

def insert_cdrom(api_key, base_url, uuid, filename):
    """
    Inserts a CD-ROM with a specified filename for a resource identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        base_url (str): The base URL of the API.
        uuid (str): The UUID of the resource for which to insert the CD-ROM.
        filename (str): The filename of the CD-ROM.

    Returns:
        dict: The JSON response from the API containing the result of the CD-ROM insertion.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `base_url`, `uuid`, `filename`) is missing.
        requests.exceptions.RequestException: If an error occurs during the request.

    Example:
        >>> insert_cdrom('your_api_key', 'https://example.com', 'resource_uuid', 'cdrom.iso')
        {'status': 'success', 'message': 'CD-ROM inserted successfully'}
    """
    assert api_key, "API key is required"
    assert base_url, "Base URL is required"
    assert uuid, "UUID is required"
    assert filename, "Filename is required"

    url = f"{base_url}/api/insert-cdrom/{uuid}/{filename}/"
    headers = {
        'X-Api-Key': api_key
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def eject_cdrom(api_key, base_url, uuid):
    """
    Ejects the CD-ROM for a resource identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        base_url (str): The base URL of the API.
        uuid (str): The UUID of the resource for which to eject the CD-ROM.

    Returns:
        dict: The JSON response from the API containing the result of the CD-ROM ejection.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `base_url`, `uuid`) is missing.
        requests.exceptions.RequestException: If an error occurs during the request.

    Example:
        >>> eject_cdrom('your_api_key', 'https://example.com', 'resource_uuid')
        {'status': 'success', 'message': 'CD-ROM ejected successfully'}
    """
    assert api_key, "API key is required"
    assert base_url, "Base URL is required"
    assert uuid, "UUID is required"

    url = f"{base_url}/api/eject-cdrom/{uuid}/"
    headers = {
        'X-Api-Key': api_key
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def delete_iso(api_key, base_url, iso_filename):
    """
    Deletes an ISO file with the specified filename using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        base_url (str): The base URL of the API.
        iso_filename (str): The filename of the ISO file to delete.

    Returns:
        bool: True if the ISO file was deleted successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `base_url`, `iso_filename`) is missing.
        requests.exceptions.RequestException: If an error occurs during the request.

    Example:
        >>> delete_iso('your_api_key', 'https://example.com', 'my_iso_file.iso')
        ISO file my_iso_file.iso deleted successfully
        True
    """
    assert api_key, "API key is required"
    assert base_url, "Base URL is required"
    assert iso_filename, "ISO file name is required"

    url = f"{base_url}/api/delete-iso/{iso_filename}/"
    headers = {
        'X-Api-Key': api_key
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()

        if response.status_code == requests.codes.ok:
            print(f"ISO file {iso_filename} deleted successfully")
            return True
        else:
            print("Failed to delete ISO file")
            return False

    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return False

def upload_iso(api_key, base_url, iso_file_path):
    """
    Uploads an ISO file to the specified base URL using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        base_url (str): The base URL of the API.
        iso_file_path (str): The file path of the ISO file to upload.

    Returns:
        bool: True if the ISO file was uploaded successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `base_url`, `iso_file_path`) is missing.
        requests.exceptions.RequestException: If an error occurs during the request.

    Example:
        >>> upload_iso('your_api_key', 'https://example.com', '/path/to/iso_file.iso')
        True
    """
    assert api_key, "API key is required"
    assert base_url, "Base URL is required"
    assert iso_file_path, "ISO file path is required"

    url = f"{base_url}/api/upload-iso/"
    headers = {
        'X-Api-Key': api_key
    }
    files = {
        'iso_file': open(iso_file_path, 'rb')
    }

    try:
        response = requests.post(url, headers=headers, files=files, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('Content-Length', 0))
        bytes_uploaded = 0

        progress_bar = None

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                bytes_uploaded += len(chunk)
                progress_bar = sg.one_line_progress_meter(
                    "Uploading ISO file",
                    bytes_uploaded,
                    total_size,
                    "key",
                    f"Uploaded {bytes_uploaded / 1048576:.2f} / {total_size / 1048576:.2f} MB"
                )
                if not progress_bar:
                    break

        if progress_bar:
            return True
        else:
            sg.popup_error("Upload canceled by user")
            return False

    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return False




def run_plugin(api_key, base_url, plugin_directory, image_uuid):
    """
    Runs a plugin on a specified image identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        base_url (str): The base URL of the API.
        plugin_directory (str): The directory of the plugin to run.
        image_uuid (str): The UUID of the image on which to run the plugin.

    Returns:
        dict: The JSON response from the API containing the result of the plugin execution.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `base_url`, `plugin_directory`, `image_uuid`) is missing.
        requests.exceptions.RequestException: If an error occurs during the request.

    Example:
        >>> run_plugin('your_api_key', 'https://example.com', 'plugin_directory', 'image_uuid')
        {'status': 'success', 'message': 'Plugin execution completed'}
    """
    assert api_key, "API key is required"
    assert base_url, "Base URL is required"
    assert plugin_directory, "Plugin directory is required"
    assert image_uuid, "Image UUID is required"

    url = f"{base_url}/api/run-plugin/"
    headers = {"X-Api-Key": api_key}
    params = {"plugin_directory": plugin_directory, "image_uuid": image_uuid}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def list_plugins(api_key, base_url):
    """
    Retrieves the list of available plugins using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        base_url (str): The base URL of the API.

    Returns:
        list: A list of available plugins.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `base_url`) is missing.
        requests.exceptions.RequestException: If an error occurs during the request.

    Example:
        >>> list_plugins('your_api_key', 'https://example.com')
        ['plugin_1', 'plugin_2', 'plugin_3']
    """
    assert api_key, "API key is required"
    assert base_url, "Base URL is required"

    url = f"{base_url}/api/list-plugins/"
    headers = {"X-Api-Key": api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('plugins', [])
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return []

def list_iso_files(api_key, base_url):
    """
    Retrieves the list of available ISO files using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        base_url (str): The base URL of the API.

    Returns:
        dict: The JSON response from the API containing the list of available ISO files.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `base_url`) is missing.
        requests.exceptions.RequestException: If an error occurs during the request.

    Example:
        >>> list_iso_files('your_api_key', 'https://example.com')
        {'iso_files': ['file_1.iso', 'file_2.iso', 'file_3.iso']}
    """
    assert api_key, "API key is required"
    assert base_url, "Base URL is required"

    url = f"{base_url}/api/list-iso-files/"
    headers = {"X-Api-Key": api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def recreate_folders(api_key, base_url, uuid_path, folders):
    """
    Recreates a list of folders for a resource identified by UUID path using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        base_url (str): The base URL of the API.
        uuid_path (str): The UUID path of the resource for which to recreate the folders.
        folders (list): A list of folders to recreate.

    Returns:
        dict: The JSON response from the API containing the result of the folder recreation.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `base_url`, `uuid_path`, `folders`) is missing.
        requests.exceptions.RequestException: If an error occurs during the request.

    Example:
        >>> recreate_folders('your_api_key', 'https://example.com', 'resource_uuid_path', ['folder1', 'folder2', 'folder3'])
        {'status': 'success', 'message': 'Folders recreated successfully'}
    """
    assert api_key, "API key is required"
    assert base_url, "Base URL is required"
    assert uuid_path, "UUID path is required"
    assert folders, "Folders list is required"

    url = f"{base_url}/api/recreate-folders/"
    headers = {"X-Api-Key": api_key}
    data = {
        "uuid_path": uuid_path,
        "folders": folders
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def create_folders_in_qcow2(api_key, base_url, uuid_path, folders):
    """
    Creates folders within a qcow2 image for a resource identified by UUID path using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        base_url (str): The base URL of the API.
        uuid_path (str): The UUID path of the resource for which to create the folders within the qcow2 image.
        folders (list): A list of folders to create within the qcow2 image.

    Returns:
        bool: True if the folders were created successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `base_url`, `uuid_path`, `folders`) is missing.
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: If an unexpected error occurs during the request.

    Example:
        >>> create_folders_in_qcow2('your_api_key', 'https://example.com', 'resource_uuid_path', ['folder1', 'folder2', 'folder3'])
        Response: {'status': 'success', 'message': 'Folders created successfully'}
        True
    """
    assert api_key, "API key is required"
    assert base_url, "Base URL is required"
    assert uuid_path, "VMDK path is required"
    assert folders, "Folders are required"

    url = f"{base_url}/api/create-folders/"
    headers = {"X-API-KEY": api_key}
    data = {
        "uuid_path": uuid_path,
        "folders": folders,
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        print(f"Response: {response.json()}")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

def create_folders_in_qcow2_background(api, web_server_address, uuid_folder, case_tags):
    """
    Run the create_folders_in_vmdk function in the background using a separate thread.

    Args:
        api (str): Forensic API
        web_server_address (str): Web server address
        uuid_folder (str): UUID folder
        case_tags (str): Case tags

    Returns:
        None
    """
    # Define the target function
    def target_function():
        create_folders_in_qcow2(api, web_server_address, uuid_folder, case_tags)
        print("Folders created")

    # Create a thread and run the target function
    thread = threading.Thread(target=target_function)
    thread.start()

def sanitize_string(s):
    """
    Sanitizes a string by replacing non-alphanumeric characters with underscores.

    Args:
        s (str): The string to sanitize.

    Returns:
        str: The sanitized string.

    Raises:
        AssertionError: If the input is not a string.

    Example:
        >>> sanitize_string('Hello World!')
        'Hello_World'
    """
    assert isinstance(s, str), 'Expecting a string!'
    return re.sub('[^0-9a-zA-Z]+', '_', s)


def read_case_config(json_filepath):
    """
    Reads a JSON file containing case configuration data and returns a list of sanitized directory names.

    Args:
        json_filepath (str): The filepath of the JSON file to read.

    Returns:
        list: A list of sanitized directory names.

    Raises:
        AssertionError: If the JSON file does not exist.
        IOError: If there is an error opening or reading the JSON file.
        KeyError: If a required key is not found in the JSON data.

    Example:
        >>> read_case_config('case_config.json')
        ['directory_name1', 'directory_name2', 'directory_name3']
    """
    # Check if file exists
    assert os.path.isfile(json_filepath), f'File {json_filepath} does not exist!'

    # Read the JSON file
    try:
        with open(json_filepath, 'r') as file:
            data = json.load(file)
    except Exception as e:
        raise IOError(f'Failed to open or read the file {json_filepath}. Error: {e}')

    # Convert the JSON data to a list of directory names
    dir_names = []
    for tag in data:
        try:
            #type_ = sanitize_string(tag['type'])
            name = sanitize_string(tag['name'])
            #description = sanitize_string(tag['description'])
        except KeyError as e:
            raise KeyError(f'KeyError - {e} not found in the tag')

        directory_name = f"{name}"
        dir_names.append(directory_name)
        #sort dir_name
        dir_names.sort()
    return(dir_names)




def download_evidence(api_key, uuid, base_url, output_file):
    """
    Downloads evidence vmdk identified by UUID using the API endpoint and saves it to a local file.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the evidence to download.
        base_url (str): The base URL of the API.
        output_file (str): The path of the output file to save the downloaded evidence.

    Returns:
        bool: True if the evidence was downloaded successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `uuid`, `base_url`, `output_file`) is missing.
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: If an unexpected error occurs during the download.

    Example:
        >>> download_evidence('your_api_key', 'evidence_uuid', 'https://example.com', 'output_file.bin')
        Evidence downloaded to evidence.vmdk
        True
    """
    assert api_key, "API key is required"
    assert uuid, "UUID is required"
    assert base_url, "Base URL is required"
    assert output_file, "Output file is required"

    chunk_size = 1048576  # 1 MB

    url = f"{base_url}/api/download-evidence/{uuid}/"
    headers = {"X-API-KEY": api_key}

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('Content-Length', 0))
        bytes_downloaded = 0

        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    bytes_downloaded += len(chunk)

                    progress_bar = sg.one_line_progress_meter(
                        "Downloading Evidence",
                        bytes_downloaded,
                        total_size,
                        "key",
                        f"Downloaded {bytes_downloaded / 1048576:.2f} / {total_size / 1048576:.2f} MB",
                    )
                    # If the user clicked the cancel button, break the loop
                    if not progress_bar:
                        break
        if progress_bar:
            sg.popup(f"Evidence downloaded to {output_file}. Opening path in explorer. \nPlease import this image into" \
                      " Autopsy Case")
            return True
        else:
            sg.popup_error("Download canceled by user")
            os.remove(output_file)
            return False

    except requests.exceptions.HTTPError as e:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False


def download_memory_dump(api_key, uuid, base_url, output_file):
    """
    Downloads a memory dump identified by UUID using the API endpoint and saves it to a local file.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the memory dump to download.
        base_url (str): The base URL of the API.
        output_file (str): The path of the output file to save the downloaded memory dump.

    Returns:
        bool: True if the memory dump was downloaded successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `uuid`, `base_url`, `output_file`) is missing.
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: If an unexpected error occurs during the download.

    Example:
        >>> download_memory_dump('your_api_key', 'memory_dump_uuid', 'https://example.com', 'output_file.bin')
        Memory dump downloaded to output_file.bin
        True
    """
    assert api_key, "API key is required"
    assert uuid, "UUID is required"
    assert base_url, "Base URL is required"
    assert output_file, "Output file is required"

    chunk_size = 1048576  # 1 MB

    url = f"{base_url}/api/download-memory-dump/{uuid}/"
    headers = {"X-API-KEY": api_key}

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('Content-Length', 0))
        bytes_downloaded = 0

        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    bytes_downloaded += len(chunk)

                    progress_bar = sg.one_line_progress_meter(
                        "Downloading Memory Dump",
                        bytes_downloaded,
                        total_size,
                        "key",
                        f"Downloaded {bytes_downloaded / 1048576:.2f} / {total_size / 1048576:.2f} MB",
                    )
                    # If the user clicked the cancel button, break the loop
                    if not progress_bar:
                        break
        if progress_bar:
            sg.popup(f"Memory dump downloaded to {output_file}")
            return True
        else:
            sg.popup_error("Download canceled by user")
            os.remove(output_file)
            return False

    except requests.exceptions.HTTPError as e:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

def download_screenshots(api_key, uuid, base_url, output_file):
    """
    Downloads screenshots identified by UUID using the API endpoint and saves them to a local file.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the screenshots to download.
        base_url (str): The base URL of the API.
        output_file (str): The path of the output file to save the downloaded screenshots.

    Returns:
        bool: True if the screenshots were downloaded successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `uuid`, `base_url`, `output_file`) is missing.
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: If an unexpected error occurs during the download.

    Example:
        >>> download_screenshots('your_api_key', 'screenshots_uuid', 'https://example.com', 'output_file.zip')
        Screenshots downloaded to output_file.zip
        True
    """
    assert api_key, "API key is required"
    assert uuid, "UUID is required"
    assert base_url, "Base URL is required"
    assert output_file, "Output file is required"

    url = f"{base_url}/api/download-screenshots/{uuid}/"
    headers = {"X-API-KEY": api_key}

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('Content-Length', 0))
        bytes_downloaded = 0

        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bytes_downloaded += len(chunk)

                    # Update the progress bar
                    sg.one_line_progress_meter(
                        "Downloading Screenshots",
                        bytes_downloaded,
                        total_size,
                        "key",
                        f"Downloaded {bytes_downloaded} / {total_size} bytes",
                    )
        print(f"Screenshots downloaded to {output_file}")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

def screenshot_vm(api_key, uuid, base_url):
    """
    Takes a screenshot of a virtual machine identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the virtual machine to take a screenshot of.
        base_url (str): The base URL of the API.

    Returns:
        bool: True if the screenshot was taken successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `uuid`, `base_url`) is missing.
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: If an unexpected error occurs.

    Example:
        >>> screenshot_vm('your_api_key', 'vm_uuid', 'https://example.com')
        Screenshot taken successfully.
        True
    """
    assert api_key, "API key is required"
    assert uuid, "UUID is required"
    assert base_url, "Base URL is required"

    url = f"{base_url}/api/screenshot-vm/{uuid}/"
    headers = {"X-API-KEY": api_key}

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()

        result = response.json()
        if result['screenshot_taken']:
            print("Screenshot taken successfully.")
            return True
        else:
            print("Error taking screenshot.")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

def shutdown_vm(api_key, uuid, base_url):
    """
    Shuts down a virtual machine identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the virtual machine to shut down.
        base_url (str): The base URL of the API.

    Returns:
        bool: True if the virtual machine has been shut down successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `uuid`, `base_url`) is missing.
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: If an unexpected error occurs.

    Example:
        >>> shutdown_vm('your_api_key', 'vm_uuid', 'https://example.com')
        VM has been shut down.
        True
    """
    assert api_key, "API key is required"
    assert uuid, "UUID is required"
    assert base_url, "Base URL is required"

    url = f"{base_url}/api/shutdown-vm/{uuid}/"
    headers = {"X-API-KEY": api_key}

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()

        result = response.json()
        if result['vm_shutdown']:
            print("VM has been shut down.")
            return True
        else:
            print("Error shutting down VM.")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

def reset_vm(api_key, uuid, base_url):
    """
    Resets a virtual machine identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the virtual machine to reset.
        base_url (str): The base URL of the API.

    Returns:
        bool: True if the virtual machine has been reset successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `uuid`, `base_url`) is missing.
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: If an unexpected error occurs.

    Example:
        >>> reset_vm('your_api_key', 'vm_uuid', 'https://example.com')
        VM has been reset.
        True
    """
    assert api_key, "API key is required"
    assert uuid, "UUID is required"
    assert base_url, "Base URL is required"

    url = f"{base_url}/api/reset-vm/{uuid}/"
    headers = {"X-API-KEY": api_key}

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()

        result = response.json()
        if result['vm_reset']:
            print("VM has been reset.")
            return True
        else:
            print("Error resetting VM.")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

def mount_folder(api_key, uuid, base_url, folder):
    """
    Mounts a folder on a virtual machine identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the virtual machine to mount the folder on.
        base_url (str): The base URL of the API.
        folder (str): The path of the folder to mount on the virtual machine.

    Returns:
        bool: True if the folder has been mounted successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `uuid`, `base_url`, `folder`) is missing.
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: If an unexpected error occurs.

    Example:
        >>> mount_folder('your_api_key', 'vm_uuid', 'https://example.com', '/path/to/folder')
        Folder '/path/to/folder' has been mounted.
        True
    """
    assert api_key, "API key is required"
    assert uuid, "UUID is required"
    assert base_url, "Base URL is required"
    assert folder, "Folder path is required"

    url = f"{base_url}/api/mount-folder/{uuid}/"
    headers = {"X-API-KEY": api_key}
    data = {"folder": folder}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        if result['folder_mounted']:
            print(f"Folder '{folder}' has been mounted.")
            return True
        else:
            print(f"Error mounting folder: {result['error']}")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False


def confirm_deletion_twice():
    """
    Displays a confirmation dialog twice, asking the user if they want to delete a VM.

    Returns:
        bool: True if the user confirms the deletion twice, False otherwise.

    Example:
        >>> confirm_deletion_twice()
        Are you sure you want to delete the VM? (1/2)
        [Yes] [No]
        Are you sure you want to delete the VM? (2/2)
        [Yes] [No]
        True
    """
    for i in range(2):
        confirmation_layout = [
            [sg.Text(f"Are you sure you want to delete the VM? ({i + 1}/2)")],
            [sg.Button("Yes"), sg.Button("No")]
        ]

        confirmation_window = sg.Window("Confirm Deletion", confirmation_layout)

        event, values = confirmation_window.read()
        confirmation_window.close()

        if event != "Yes":
            return False
    return True
    
    
def delete_vm(api_key, uuid, base_url):
    """
    Deletes a virtual machine identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the virtual machine to delete.
        base_url (str): The base URL of the API.

    Returns:
        bool: True if the virtual machine has been deleted successfully, False otherwise.

    Raises:
        AssertionError: If any of the required arguments (`api_key`, `uuid`, `base_url`) is missing.
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: If an unexpected error occurs.

    Example:
        >>> delete_vm('your_api_key', 'vm_uuid', 'https://example.com')
        Are you sure you want to delete the VM? (1/2)
        [Yes] [No]
        Are you sure you want to delete the VM? (2/2)
        [Yes] [No]
        VM with UUID vm_uuid has been deleted.
        True
    """
    if not confirm_deletion_twice():
        print("VM deletion canceled.")
        return False

    url = f"{base_url}/api/delete-vm/{uuid}/"
    headers = {"X-API-KEY": api_key}

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        result = response.json()
        if result['vm_deleted']:
            print(f"VM with UUID {uuid} has been deleted.")
            return True
        else:
            print(f"Error deleting VM: {result['error']}")
            return False
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
        
def check_vm_exists(api_key, uuid, baseurl):
    """
    Checks if a virtual machine identified by UUID exists using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the virtual machine to check.
        base_url (str): The base URL of the API.

    Returns:
        bool: True if the virtual machine exists, False otherwise.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the request.
        Exception: If an unexpected error occurs.

    Example:
        >>> check_vm_exists('your_api_key', 'vm_uuid', 'https://example.com')
        True
    """
    try:
        url = f"{baseurl}/api/check-vm-exists/{uuid}/"
        headers = {"X-API-KEY": api_key}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            vm_exists = result['vm_exists']
            return vm_exists
        else:
            print("DEBUG:")
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

def start_vm(api_key, uuid, baseurl):
    """
    Starts a virtual machine identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the virtual machine to start.
        base_url (str): The base URL of the API.

    Returns:
        dict: The response JSON data if the virtual machine is started successfully, None otherwise.

    Example:
        >>> start_vm('your_api_key', 'vm_uuid', 'https://example.com')
        {'vm_started': True, 'message': 'VM started successfully.'}
    """
    url = f"{baseurl}/api/start-vm/{uuid}/"
    headers = {"X-API-KEY": api_key}

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print(str(result))
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def stop_vm(api_key, uuid, baseurl):
    """
    Stops a virtual machine identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the virtual machine to stop.
        base_url (str): The base URL of the API.

    Returns:
        dict: The response JSON data if the virtual machine is stopped successfully, None otherwise.

    Example:
        >>> stop_vm('your_api_key', 'vm_uuid', 'https://example.com')
        {'vm_stopped': True, 'message': 'VM stopped successfully.'}
    """
    url = f"{baseurl}/api/stop-vm/{uuid}/"
    headers = {"X-API-KEY": api_key}

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def get_forensic_image_info(api_key, uuid, baseurl):
    """
    Retrieves forensic image information for a virtual machine identified by UUID using the API endpoint.

    Args:
        api_key (str): The API key required for authentication.
        uuid (str): The UUID of the virtual machine to retrieve forensic image information.
        base_url (str): The base URL of the API.

    Returns:
        tuple: A tuple containing the status code and the response JSON data if the information is retrieved successfully,
               or the status code and error message if an error occurs.

    Example:
        >>> get_forensic_image_info('your_api_key', 'vm_uuid', 'https://example.com')
        (0, {'forensic_image_info': { ... }})

    Note:
        - The status code 0 indicates success.
        - The status code 1 indicates an unexpected error occurred.
        - The status code other than 0 and 1 indicates access denied.

    Raises:
        Exception: If an unexpected error occurs.

    """
    url = f'{baseurl}/api/forensic-image-vm-status/{uuid}/'

    headers = {'X-API-KEY': api_key}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return 0, response.json()
        else:
            return response.status_code, "Access denied"
    except Exception as e:
        print(f"DEBUG: An unexpected error occurred: {str(e)}")
        return 1, str(e)


def test_api_key(api_key, baseurl):
    """
    Tests the validity of an API key by making a test request to the API endpoint.

    Args:
        api_key (str): The API key to test.
        base_url (str): The base URL of the API.

    Returns:
        tuple: A tuple containing the status code and a message indicating the result of the test.
            - If the status code is 0, the message is 'Access granted', indicating that the API key is valid.
            - If the status code is other than 0, the message is 'Access denied', indicating that the API key is invalid.

    Example:
        >>> test_api_key('your_api_key', 'https://example.com')
        (0, 'Access granted')

    Raises:
        Exception: If an unexpected error occurs during the test.

    """
    url = baseurl + '/api/test/'
    headers = {'X-Api-Key': api_key}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return 0, 'Access granted'
        else:
            return response.status_code, 'Access denied'
    except Exception as e:
        return 1, str(e)

def generate_and_send_public_key(baseurl, api_key, ssh_dir):
    """
    Generates an SSH key pair and sends the public key to the server.

    Args:
        base_url (str): The base URL of the server.
        api_key (str): The API key required for authentication.
        ssh_dir (str): The directory to store the SSH key pair.

    Returns:
        tuple: A tuple containing the message from the server response and the status code.
            - The message indicates the result of adding the public key to the authorized keys.
            - The status code indicates the status of the request.

    Example:
        >>> generate_and_send_public_key('https://example.com', 'your_api_key', '/path/to/ssh_dir')
        ('Public key added to authorized keys', 200)

    Raises:
        Exception: If an unexpected error occurs during key generation or sending the public key to the server.

    """
    # Generate SSH key pair

    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir)

    private_key_path = os.path.join(ssh_dir, 'mykey')
    public_key_path = os.path.join(ssh_dir, 'mykey.pub')

    if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(private_key_path)
        #key.write_public_key_file(public_key_path)
        # Save public key to disk
        public_key_path = f"{private_key_path}.pub"
        with open(public_key_path, "w") as public_key_file:
            public_key_file.write(f"{key.get_name()} {key.get_base64()}")

    with open(public_key_path, 'r') as f:
        public_key = f.read().strip()

    # Send public key to server
    url = baseurl + '/api/create-ssh-keys/'
    headers = {
        'X-Api-Key': api_key
    }

    data = {
        'public_key': public_key
    }

    response = requests.post(url, headers=headers, data=data)

    # if response.status_code == 200:
    #     return 'Public key added to authorized keys'
    # else:
    #     return 'Failed to add public key to authorized keys'
    return response.json().get('message'), response.status_code


# Define the filename for the JSON file
filename = "config.json"
icon_path = "forensicVMCLient.ico"

def create_login_and_share(username, password, sharename, folderpath):
    """
    Creates a login and share using a batch file.

    Args:
        username (str): The username for the login.
        password (str): The password for the login.
        sharename (str): The name of the share.
        folderpath (str): The path to the folder to be shared.

    Returns:
        None

    Example:
        >>> create_login_and_share('myuser', 'mypassword', 'myshare', 'C:\\shared_folder')

    Raises:
        None

    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    batch_file = os.path.join(script_dir, 'create_user_and_share.bat')
    share_name = sharename.split('\\')[-1]  # extract the share_name part

    cmd = '"{}\\nircmdc" elevate cmd /c {} "{}" "{}" "{}" ""{}""'.format(os.getcwd(),batch_file, username,
                                                                    password, share_name.replace(" ", ""),
                                                                    folderpath)


    #os.system(cmd)
    pshell='powershell -Command "{}"'.format(cmd)
    print(pshell)
    os.system(pshell)



def string_to_uuid(input_string):
    """
    Converts a string to a UUID using a namespace and input string.

    Args:
        input_string (str): The input string to convert to a UUID.

    Returns:
        UUID: The UUID generated from the input string.

    Example:
        >>> string_to_uuid('example')
        UUID('9ce7f70f-070e-5d72-91a0-2f0ca6ad3d15')

    """
    # Use a namespace for your application (theoretical site)
    namespace = uuid.uuid5(uuid.NAMESPACE_DNS, 'forensic.vm.mesi.ninja')

    # Generate a UUID based on the namespace and the input string
    unique_uuid = uuid.uuid5(namespace, input_string)

    return unique_uuid


# Save the values as a json file
def save_config(values, filename):
    """
    Saves the configuration values to a JSON file.

    Args:
        values (dict): The configuration values to save.
        filename (str): The name of the JSON file to save to.

    Returns:
        None

    Example:
        >>> config = {
        >>>     'username': 'myuser',
        >>>     'password': 'mypassword',
        >>>     'server': 'example.com'
        >>> }
        >>> save_config(config, 'config.json')

    Raises:
        None

    """
    # Save the configuration to the JSON file
    with open(filename, "w") as f:
        json.dump(values, f)

# Load json file as values
def load_config(filename):
    """
    Loads the configuration values from a JSON file.

    Args:
        filename (str): The name of the JSON file to load from.

    Returns:
        dict: The configuration values loaded from the JSON file.

    Example:
        >>> config = load_config('config.json')
        >>> print(config)
        {'username': 'myuser', 'password': 'mypassword', 'server': 'example.com'}

    Raises:
        None

    """
    # Load the configuration from the JSON file if it exists
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return {}

# Check if there are enough command line arguments
try:
    image_path_arg = ""
    case_directory_arg = ""
    case_name_arg = ""
    case_number_arg = ""
    case_examiner_arg = ""
    if len(sys.argv) >= 4:
        image_path_arg = sys.argv[1]
        case_directory_arg = sys.argv[2]
        case_name_arg = sys.argv[3]
        try:
            case_number_arg = sys.argv[4]
        except Exception as e:
            case_number_arg = "-"

        try:
            case_examiner_arg = sys.argv[5]
        except Exception as e:
            case_examiner_arg = "-"

        # Save the values as a JSON file
        values = {
            "image_path_arg": image_path_arg,
            "case_directory_arg": case_directory_arg,
            "case_name_arg": case_name_arg,
            "case_number_arg": case_number_arg,
            "case_examiner_arg": case_examiner_arg
        }
        uuid_folder = str(string_to_uuid(image_path_arg + case_name_arg))
        case_image_folder = case_directory_arg + "\\" + uuid_folder
        os.makedirs(case_image_folder, exist_ok=True)

        save_config(values, "case-config.json")
    else:
        # Load the configuration from the JSON file
        config = load_config("case-config.json")
        image_path_arg = config.get("image_path_arg", "")
        case_directory_arg = config.get("case_directory_arg", "")
        case_name_arg = config.get("case_name_arg", "")
        case_number_arg = config.get("case_number_arg", "")
        case_examiner_arg = config.get("case_examiner_arg", "")
        uuid_folder = str(string_to_uuid(image_path_arg + case_name_arg))
        case_image_folder = case_directory_arg + "\\" + uuid_folder
except Exception as e:
    sg.popup(e)

# Rest of the code using the values

def run_snap(server_address, server_port, windows_share,
            share_login, share_password, replacement_share,
            forensic_image_path, uuid_folder, copy):
    """
    Runs the OpenSSH command to connect to a remote server and execute a command
    that runs the local forensic image by accessing it by samba over reverse ssh.

    Args:
        server_address (str): The IP address or hostname of the remote server.
        server_port (int): The port number to connect to on the remote server.
        windows_share (str): The Windows share path on the remote server.
        share_login (str): The login username for accessing the Windows share.
        share_password (str): The password for accessing the Windows share.
        replacement_share (str): The replacement path to use in the command.
        forensic_image_path (str): The path of the forensic image on the remote server.
        uuid_folder (str): The UUID folder name for the conversion process.
        copy (bool): Flag indicating whether to copy the forensic image.

    Returns:
        None

    Example:
        >>> run_openssh(
        >>>     server_address='192.168.0.100',
        >>>     server_port=22,
        >>>     windows_share='\\server\share',
        >>>     share_login='username',
        >>>     share_password='password',
        >>>     replacement_share='/mnt/share',
        >>>     forensic_image_path='\\server\share\image.bin',
        >>>     uuid_folder='12345678',
        >>>     copy=True
        >>> )

    Raises:
        None

    """
    try:


        private_key_path = os.path.expanduser("mykey")

        # Connect to remote host using SSH key authentication
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_address, username='forensicinvestigator', key_filename=private_key_path, port=server_port)
        # Get an available remote port
        transport = ssh.get_transport()
        remote_port = transport.request_port_forward("", 0)
        # Close the connection
        ssh.close()

        # Replacing the common path with an empty string and replacing backslashes with forward slashes
        new_path = forensic_image_path.replace(replacement_share, "").replace("\\", "/")


        print(windows_share)
        # Removing the backslashes and splitting the address into host and share components
        temp = windows_share.replace("\\\\", "")
        print(temp)
        samba_host, samba_share = temp.split("\\")

        # Creating the port forwarding string and assigning it to result
        reverse_ssh_foward = f"-R {remote_port}:{samba_host}:445"
        print(reverse_ssh_foward)


        # Prepare the command to run the convertor
        command = f'sudo /forensicVM/bin/run_snap_1 ' \
                  f'--windows-share {samba_share} ' \
                  f'--share-login {share_login} ' \
                  f'--share-password {share_password} ' \
                  f'--forensic-image-path {new_path} ' \
                  f'--folder-uuid {uuid_folder} ' \
                  f'--copy {copy} ' \
                  f'--share-port {remote_port}'

        ssh_command ="start cmd /c " + os.path.dirname(os.path.abspath(__file__))+ "\\ssh.exe -t -i " \
                     + os.path.dirname(os.path.abspath(__file__))+ \
                     "\\mykey -oStrictHostKeyChecking=no forensicinvestigator@" \
                     + str(server_address)\
                     + " -p " + str(server_port)\
                     + " " + reverse_ssh_foward + " " + command

        print(ssh_command)
        # Run the command redirecting local samba port to a free open port remote\ly
        os.system(ssh_command)

    except Exception as e:
        print(e)



def run_openssh(server_address, server_port, windows_share,
            share_login, share_password, replacement_share,
            forensic_image_path, uuid_folder, copy):
    """
    Runs the OpenSSH command to connect to a remote server and execute a command
    that converts the local forensic image by accessing it by samba over reverse ssh.

    Args:
        server_address (str): The IP address or hostname of the remote server.
        server_port (int): The port number to connect to on the remote server.
        windows_share (str): The Windows share path on the remote server.
        share_login (str): The login username for accessing the Windows share.
        share_password (str): The password for accessing the Windows share.
        replacement_share (str): The replacement path to use in the command.
        forensic_image_path (str): The path of the forensic image on the remote server.
        uuid_folder (str): The UUID folder name for the conversion process.
        copy (bool): Flag indicating whether to copy the forensic image.

    Returns:
        None

    Example:
        >>> run_openssh(
        >>>     server_address='192.168.0.100',
        >>>     server_port=22,
        >>>     windows_share='\\server\share',
        >>>     share_login='username',
        >>>     share_password='password',
        >>>     replacement_share='/mnt/share',
        >>>     forensic_image_path='\\server\share\image.bin',
        >>>     uuid_folder='12345678',
        >>>     copy=True
        >>> )

    Raises:
        None

    """            
    try:


        private_key_path = os.path.expanduser("mykey")

        # Connect to remote host using SSH key authentication
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_address, username='forensicinvestigator', key_filename=private_key_path, port=server_port)
        # Get an available remote port
        transport = ssh.get_transport()
        remote_port = transport.request_port_forward("", 0)
        # Close the connection
        ssh.close()

        # Replacing the common path with an empty string and replacing backslashes with forward slashes
        new_path = forensic_image_path.replace(replacement_share, "").replace("\\", "/")


        print(windows_share)
        # Removing the backslashes and splitting the address into host and share components
        temp = windows_share.replace("\\\\", "")
        print(temp)
        samba_host, samba_share = temp.split("\\")

        # Creating the port forwarding string and assigning it to result
        reverse_ssh_foward = f"-R {remote_port}:{samba_host}:445"
        print(reverse_ssh_foward)


        # Prepare the command to run the convertor
        command = f'sudo /forensicVM/bin/run-or-convert.sh ' \
                  f'--windows-share {samba_share} ' \
                  f'--share-login {share_login} ' \
                  f'--share-password {share_password} ' \
                  f'--forensic-image-path {new_path} ' \
                  f'--folder-uuid {uuid_folder} ' \
                  f'--copy {copy} ' \
                  f'--share-port {remote_port}'

        ssh_command ="start /wait cmd /c " + os.path.dirname(os.path.abspath(__file__))+ "\\ssh.exe -t -i " \
                     + os.path.dirname(os.path.abspath(__file__))+ \
                     "\\mykey -oStrictHostKeyChecking=no forensicinvestigator@" \
                     + str(server_address)\
                     + " -p " + str(server_port)\
                     + " " + reverse_ssh_foward + " " + command

        print(ssh_command)
        # Run the command redirecting local samba port to a free open port remote\ly
        os.system(ssh_command)

    except Exception as e:
        print(e)

def start_server_remotessh(server_address, server_port):
    """
    Starts the remote forensicVM server via SSH by executing a command.

    Args:
        server_address (str): The IP address or hostname of the remote server.
        server_port (int): The port number to connect to on the remote server.

    Returns:
        None

    Example:
        >>> start_server_remotessh(
        >>>     server_address='192.168.0.100',
        >>>     server_port=22
        >>> )

    Raises:
        None

    """
    try:
        command = f"cd /forensicVM/bin; exec sudo /forensicVM/bin/run-django-screen"

        ssh_command ="start /wait cmd /c " + os.path.dirname(os.path.abspath(__file__))+ "\\ssh.exe -t -i " \
                     + os.path.dirname(os.path.abspath(__file__))+ \
                     "\\mykey -oStrictHostKeyChecking=no forensicinvestigator@" \
                     + str(server_address)\
                     + " -p " + str(server_port)\
                     + " " + command

        os.system(ssh_command)

    except Exception as e:
        print(e)


def debug_remotessh(server_address, server_port, uuid_folder):
    """
    Starts an interactive debug session on the remote server via SSH.

    Args:
        server_address (str): The IP address or hostname of the remote server.
        server_port (int): The port number to connect to on the remote server.
        uuid_folder (str): The UUID folder to navigate to for the debug session.

    Returns:
        None

    Example:
        >>> debug_remotessh(
        >>>     server_address='192.168.0.100',
        >>>     server_port=22,
        >>>     uuid_folder='12345678-1234-5678-1234-567812345678'
        >>> )

    Raises:
        None

    """
    try:
        command = f"cd /forensicVM/mnt/vm/{uuid_folder}; exec bash"

        ssh_command ="start /wait cmd /c " + os.path.dirname(os.path.abspath(__file__))+ "\\ssh.exe -t -i " \
                     + os.path.dirname(os.path.abspath(__file__))+ \
                     "\\mykey -oStrictHostKeyChecking=no forensicinvestigator@" \
                     + str(server_address)\
                     + " -p " + str(server_port)\
                     + " " + command

        os.system(ssh_command)

    except Exception as e:
        print(e)


def ssh_background_session(server_address, server_port, windows_share):
    """
    Starts a background SSH session with port forwarding to access a Windows share.

    Args:
        server_address (str): The IP address or hostname of the remote server.
        server_port (int): The port number to connect to on the remote server.
        windows_share (str): The Windows share path to be accessed.

    Returns:
        int: The dynamically allocated remote port for the SSH session.

    Example:
        >>> remote_port = ssh_background_session(
        >>>     server_address='192.168.0.100',
        >>>     server_port=22,
        >>>     windows_share='\\\\192.168.0.200\\ShareFolder'
        >>> )
        >>> print(remote_port)

    Raises:
        None

    """
    try:
        private_key_path = os.path.expanduser("mykey")

        # Connect to remote host using SSH key authentication
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_address, username='forensicinvestigator', key_filename=private_key_path, port=server_port)
        # Get an available remote port
        transport = ssh.get_transport()
        remote_port = transport.request_port_forward("", 0)
        # Close the connection
        ssh.close()



        # Prepare the command to run the convertor
        command = '/home/forensicinvestigator/wait-y.sh'
        temp = windows_share.replace("\\\\", "")
        print(temp)
        samba_host, samba_share = temp.split("\\")

        # Creating the port forwarding string and assigning it to result
        reverse_ssh_foward = f"-R {remote_port}:{samba_host}:445"

        ssh_command ="start cmd /c " + os.path.dirname(os.path.abspath(__file__))+ "\\ssh.exe -t -i mykey " \
                                                                                   "-oStrictHostKeyChecking=no " \
                                                                                   "forensicinvestigator@" \
                     + str(server_address)\
                     + " -p " + str(server_port)\
                     + " " + reverse_ssh_foward + " " + command
        os.system(ssh_command)
        return remote_port
    except Exception as e:
        print(e)


def test_ssh(address, port):
    """
    Tests SSH connectivity to a remote host.

    Args:
        address (str): The IP address or hostname of the remote host.
        port (int): The port number to connect to on the remote host.

    Returns:
        bool: True if the SSH connection was successful, False otherwise.

    Example:
        >>> result = test_ssh('192.168.0.100', 22)
        >>> print(result)

    Raises:
        None

    """
    try:
        private_key_path = os.path.expanduser("mykey")

        ###ssh_key.write_private_key_file(private_key_path)

        # Save public key to disk
        ###public_key_path = f"{private_key_path}.pub"
        ###with open(public_key_path, "w") as public_key_file:
        ###public_key_file.write(f"{ssh_key.get_name()} {ssh_key.get_base64()}")

        # Connect to remote host using SSH key authentication
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(address, username='forensicinvestigator', key_filename=private_key_path, port=port)

        # Run a command on the remote host and print the output
        stdin, stdout, stderr = ssh.exec_command('ls -al')
        for line in stdout:
            print(line.strip())

        # Close the SSH connection
        ssh.close()
        return True
    except Exception as e:
        print(e)
        if not os.path.exists(private_key_path):
            ssh_key = paramiko.rsakey.RSAKey.generate(2048)
            ssh_key.write_private_key_file(private_key_path)
            public_key_path = f"{private_key_path}.pub"
            with open(public_key_path, "w") as public_key_file:
                public_key_file.write(f"{ssh_key.get_name()} {ssh_key.get_base64()}")

        # Save public key to disk

        return False




def run_command_ssh(ssh, window2, cmd):
    """
    Executes a command on a remote host via SSH and prints the output.

    Args:
        ssh (paramiko.SSHClient): The SSH client object connected to the remote host.
        window2 (sg.Window): The PySimpleGUI window object to display the output.
        cmd (str): The command to execute on the remote host.

    Returns:
        None

    Example:
        >>> ssh = paramiko.SSHClient()
        >>> # Connect to the remote host...
        >>> window = sg.Window("Output Window", layout)
        >>> run_command_ssh(ssh, window, "ls -al")

    Raises:
        None

    """
    # Run a command on the remote host and print the output
    # stdin, stdout, stderr = ssh.exec_command("sudo /forensicVM/bin/forensicv2v.sh")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    while not stdout.channel.exit_status_ready():

        # show command output in real time
        output = ""
        while stdout.channel.recv_ready():
            output += stdout.channel.recv(1024).decode("utf-8")
            print(output)
            # window2.read()
            current_output = window2['-OUTPUT-'].get()
            window2['-OUTPUT-'].update(current_output+output, text_color='white')

        output = ""
        while stderr.channel.recv_stderr_ready():
            output += stderr.channel.recv_stderr(1024).decode("utf-8")
            print(output)
            # window2.read()
            current_output = window2['-OUTPUT-'].get()
            window2['-OUTPUT-'].update(current_output+"e:"+output, text_color='white')

def test_windows_share(server_address, username, password):
    """
    Tests the connectivity to a Windows share.

    Args:
        server_address (str): The address of the Windows share.
        username (str): The username for authentication.
        password (str): The password for authentication.

    Returns:
        bool: True if the connectivity test is successful, False otherwise.

    Example:
        >>> test_windows_share("\\\\server\\share", "username", "password")

    Raises:
        subprocess.CalledProcessError: If the 'net use' command fails.

    """
    # Use the 'net use' command to map a drive to the share
    cmd = 'net use {} /user:{} {}'.format(server_address, username, password)
    #print(cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        return False

    # Disconnect the mapped drive
    cmd = 'net use {} /delete'.format(server_address)
    subprocess.check_output(cmd, shell=True)

    return True





def validate_server_address(address):
    """
    Validates the format of a server address.

    Args:
        address (str): The server address to validate.

    Returns:
        bool: True if the address is valid, False otherwise.

    Example:
        >>> validate_server_address("192.168.0.1")
        True

        >>> validate_server_address("https://example.com")
        True

        >>> validate_server_address("invalid_address")
        False

    """
    ip_regex = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
    url_regex = r"\b(https?:\/\/)?[\w.-]+\.[a-zA-Z]{2,}(\S+)?\b"
    if re.match(ip_regex, address):
        return True
    elif re.match(url_regex, address):
        return True
    else:
        return False


# Event handler for the file browse button
def handle_file_browse(event, values, window):
    """
    Handle the file browse event.

    Args:
        event (str): The event triggered by the file browse button.
        values (dict): The current values of the window elements.
        window (sg.Window): The GUI window object.

    """
    iso_file_path = values['-BROWSE-']
    window['-CDROM FILE-'].update(value=iso_file_path)
    window['-UPLOAD-'].update(disabled=False)


def list_snapshots(forensic_api, uuid_folder, web_server_address):
    """
    List the snapshots associated with a forensic VM.

    Args:
        forensic_api (object): The forensic API object.
        uuid_folder (str): The UUID folder of the forensic VM.
        web_server_address (str): The address of the web server.

    Returns:
        list: A list of snapshot information.

    """
    snapshot_info_list = []

    try:
        snapshots = get_snapshot_list(forensic_api, uuid_folder, web_server_address)

        for snapshot in snapshots:
            snapshot_tag = snapshot.get('tag')
            vm_size = snapshot.get('vm_size')
            snapshot_info = f"({snapshot_tag}) - {vm_size} MB"
            snapshot_info_list.append(snapshot_info)
            print(snapshot_info)

        return snapshot_info_list

    except Exception as e:
        print(e)
        sg.popup_ok("Error listing snapshots", title="Error")
        return []

def validate_date(date_str):
    """
    Function to validate the date string against the format 'YYYY-MM-DDTHH:MM:SS'
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        return True
    except ValueError:
        return False

def formInit(values, window):
    """
    Initialize the form window by populating various elements with data retrieved from the forensic API.

    It performs the following tasks:

    Retrieves the UUID folder based on the forensic image path and case name.
    Tests the API key and server address to ensure they are valid.
    Retrieves the memory size of the forensic VM server and updates the memory slider in the form.
    Retrieves the list of snapshots associated with the forensic VM and updates the snapshot list in the form.
    Retrieves the list of available ISO files and updates the CD-ROM list in the form.
    Retrieves the list of remote plugins and updates the plugin list in the form.

    Args:
        values (dict): A dictionary containing the form values.
        window: The PySimpleGUI window object.

    """
    forensic_image_path = values["forensic_image_path"]
    uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
    web_server_address = values["server_address"]
    forensic_api = values["forensic_api"]
    server_ok, _ = test_api_key(forensic_api, web_server_address)

    if server_ok==0:
        try:
            memory = get_memory_size(forensic_api, web_server_address, uuid_folder) / 1024
            if memory:
                print("Forensic VM Server is running on " + str(memory) + " MB")


                available_memory = get_available_memory(forensic_api, web_server_address)
                window['-MB-SLIDER-'].update(range=(0, available_memory))
                window['-MB-SLIDER-'].update(memory)
        except Exception as e:
            print(str(e))

        try:
            # Update snapshot list
            snapshot_info_list = list_snapshots(forensic_api, uuid_folder, web_server_address)
            window['-SNAPSHOT-LIST-'].update(snapshot_info_list)
        except Exception as e:
            print(str(e))

        # Update iso file list
        try:
            iso_files = list_iso_files(forensic_api, web_server_address)
            if iso_files:
                window['-CDROM LIST-'].update(iso_files['iso_files'])
        except Exception as e:
            print(str(e))

        # List remote plugins
        try:
            plugins = list_plugins(forensic_api, web_server_address)
            if plugins:
                plugin_list = []
                for plugin in plugins:
                    plugin_dir = plugin.get('plugin_dir')
                    print(plugin_dir)
                    plugin_name = plugin.get('plugin_name')
                    print(plugin_name)
                    plugin_description = plugin.get('plugin_description')
                    print(plugin_description)
                    plugin_list.append(f"{plugin_name} - {plugin_description} ({plugin_dir}) ")

                window['-PLUGIN LIST-'].update(plugin_list)
        except Exception as e:
            print(str(e))

        try:
            status=check_tap_interface(web_server_address, str(uuid_folder), forensic_api)
            if status:
                print(f" Network: {status}")
                window['insert_network_button'].update(disabled=True)
                window['remove_network_button'].update(disabled=False)
            else:
                print(f" Network: {status}")
                window['insert_network_button'].update(disabled=False)
                window['remove_network_button'].update(disabled=True)
        except Exception as e:
            print(str(e))


# Form: All fields in the form

def ForensicVMForm():
    """
    This function is used to create a forensic VM form with a user interface.

    The function initializes a number of state variables, configures GUI theme, loads or creates the configuration from a JSON file,
    creates different frames for performing tasks such as uploading, managing, deleting and listing CD-ROMs, converting forensic image 
    to VM, screenshot management, memory dump creation, VM control, and various tools. The function also incorporates plugin management,
    snapshot management and VM fine-tuning options.

    Frames are arranged in tabs for convenient access, including tabs for virtualization, configuration, autopsy case details, 
    and about info. The function continuously listens for events on the GUI and takes appropriate actions based on the event triggers.

    It creates the window with the aforementioned layout and goes into an event loop where it waits for events to occur. These events
    can be button presses, input changes etc. which are handled appropriately within the loop.

    The function makes heavy use of PySimpleGUI library to design and control the GUI components.

    This function does not take any parameters, and does not return any values. It runs indefinitely, until the window is closed.
    """
    vm_stopped = True
    folders_created = False
    server_offline = False
    first_run = True
    # Set the theme
    sg.theme("DefaultNoMoreNagging")
    # Define the filename for the JSON file

    filename = "config.json"
    icon_path = "forensicVMCLient.ico"
    # Load the configuration from the JSON file if it exists
    if os.path.isfile(filename):
        config = load_config(filename)
    else:
        config = {}
    if 'case_image_folder' in locals():
        if os.path.isfile(case_image_folder + "\\image-share.json"):
            image_config = load_config(case_image_folder + "\\image-share.json")
        else:
            image_config = {}
    else:
        image_config = {}
    case_tag_path = case_directory_arg + "\\case_tags.json"
    if os.path.isfile(case_tag_path):
        case_tags = read_case_config(case_tag_path)
        # convert case_tags to a string
        case_tags_str = str(case_tags)
    else:
        case_tags_str=""
        case_tags = {}


    upload_frame = sg.Frame('Upload', [
        [sg.Input(key='-CDROM FILE-', enable_events=True, visible=False),
         sg.Button('Browse and Upload', key='-BROWSE-', disabled=False)]
    ])
    """
    Frame: Upload
    Components:
    - Input field for CD-ROM file path (hidden by default)
    - File browse button for selecting an ISO file
    - Upload button (disabled until a file is selected)
    """

    cdrom_frame = sg.Frame('Manage', [
        [sg.Button('Insert', key='-INSERT-'), sg.Button('Eject', key='-EJECT-')],
    ])
    """
    Frame: Manage
    Components:
    - Button: Insert (for inserting CD-ROM)
    - Button: Eject (for ejecting CD-ROM)
    """

    delete_frame = sg.Frame('Delete', [
        [sg.Button('Delete', key='-DELETE-')],
    ])
    """
    Frame: Delete
    Components:
    - Button: Delete (for deleting CD-ROM)
    """

    list_frame = sg.Frame('List', [
        [sg.Button('Remote ISO files', key='-LIST-', disabled=False)]
    ])
    """
    Frame: List
    Components:
    - Button: Remote ISO files (for fetching and displaying a list of remote ISO files)
    """

    iso_frame = sg.Frame('ISO Management', [
            [sg.Listbox([], size=(61, 21), key='-CDROM LIST-', enable_events=True)],
            [list_frame, cdrom_frame, upload_frame, delete_frame],
        ])
    """
    Frame: ISO Management
    Components:
    - Listbox: Displaying CD-ROMs (initially empty)
    - Other frames for managing CD-ROMs (list_frame, cdrom_frame, upload_frame, delete_frame)
    """

    # Create a frame for converting a forensic image to a virtual machine
    convert_frame = sg.Frame("Convert forensic Image to VM", [
        [sg.Button("Virtualize - a) Convert to VM",
                   tooltip="Connect to Forensic VM Server and virtualize the forensic Image",
                   key="convert_to_vm_button", size=(25, 2), visible=True, disabled=False)],
        [sg.Button("Virtualize - b) Link to VM",
                   tooltip="Connect to Forensic VM Server and virtualize the forensic Image",
                   key="link_to_vm_button", size=(25, 2), visible=True, disabled=False)]
    ])

    # Create a frame for taking screenshots
    screenshot_frame = sg.Frame("Screenshot", [
        [sg.Button("Screenshot", key="screenshot_vm_button", size=(25, 2), visible=True, disabled=True)],
        [sg.Button("Save screenshots", key="save_screenshots_vm_button", size=(25, 2), visible=True, disabled=True)]
    ])

    # Create a frame for making and downloading a memory dump
    memory_frame = sg.Frame("Make and download memory dump", [
        [sg.Button("Make and download memory dump", key="download_memory_button", size=(25, 2), visible=True,
                   disabled=True)]
    ])

    # Create a frame for VM control options
    vm_control_frame = sg.Frame("VM Control", [
        [sg.Button("Open ForensicVM", key="open_forensic_vm_button", size=(25, 2), visible=True, disabled=True)],
        [sg.Button("Start VM", key="start_vm_button", size=(25, 2), visible=True, disabled=True)],
        [sg.Button("Shutdown VM", key="shutdown_vm_button", size=(25, 2), visible=True, disabled=True)],
        [sg.Button("Reset VM", key="reset_vm_button", size=(25, 2), visible=True, disabled=True)],
        [sg.Button("Stop VM", key="stop_vm_button", size=(25, 2), visible=True, disabled=True)],
        [sg.Button("Delete VM", key="delete_vm_button",
                   size=(25, 2),
                   visible=True,
                   disabled=True,
                   button_color=('white', '#A00000'))]
    ])


    tools_frame = sg.Frame("Tools", [
        [sg.Button("Import Evidence Disk", key="import_evidence_button", size=(25, 1), visible=True,
                   disabled=True)],
        [sg.Button("Analyse ForensicVM performance", key="open_forensic_netdata_button", size=(25, 1), visible=True,
                   disabled=False)],
        [sg.Button("Open ForensicVM WebShell", key="open_forensic_shell_button", size=(25, 1), visible=True,
                   disabled=False)],
        [sg.Button("Recreate Evidence Disk", key="recreate_evidence_disk_button", size=(25, 1), visible=True,
                   disabled=False)],
        [sg.Button("DEGUG: Remote ssh to folder", key="debug_ssh_button", size=(25, 1), visible=True,
                   disabled=False)]
    ])

    # Create a frame for various tools
    network_frame = sg.Frame("Network", [
        [sg.Button("Enable network card", key="insert_network_button", size=(25, 1), visible=True,
                   disabled=False)],
        [sg.Button("Disable network card", key="remove_network_button", size=(25, 1), visible=True,
                   disabled=False)],
        [sg.Button("Download wireshark pcap files", key="download_wireshark_button", size=(25, 1), visible=True,
                   disabled=False)],
    ])

    # Create a frame for listing remote plugins
    list_plugins_frame = sg.Frame('List', [
        [sg.Button('List Remote Plugins', key='-LIST PLUGINS-', disabled=False)]
    ])

   # Create a frame for running a selected plugin
    run_plugin_frame = sg.Frame('Run', [
        [sg.Button('Run Selected Plugin', key='-RUN PLUGIN-', disabled=False)]
    ])

    # Create a frame for plugin management
    plugins_frame = sg.Frame('Plugin Management', [
        [sg.Listbox([], size=(61, 21), key='-PLUGIN LIST-', enable_events=True)],
        [list_plugins_frame, run_plugin_frame],
    ])

    # Create a frame for snapshot management
    snapshots_frame = sg.Frame('Snapshot management', [
        [sg.Button('List Remote Snapshots', key='-LIST SNAPSHOTS-', disabled=False),
        sg.Button('Create new', key='-CREATE SNAPSHOT-', disabled=False),
        sg.Button('Rollback', key='-ROLLBACK SNAPSHOT-', disabled=False)],
    ])

    # Create a frame for snapshot deletion (Danger Zone!)
    delete_snapshot_frame = sg.Frame('Danger Zone!', [
        [sg.Button('Delete ???', key='-DELETE SNAPSHOT-', disabled=False)]
    ])

    # Create a frame for snapshot management
    snapshot_frame = sg.Frame('Snapshot Management', [
        [sg.Listbox([], size=(61, 21), key='-SNAPSHOT-LIST-', enable_events=True)],
        [snapshots_frame, delete_snapshot_frame],
    ])


    # Create a frame for memory size fine-tuning
    finetune_frame = sg.Frame('Memory Size (GB)', [
        [sg.Slider(range=(0, 128), default_value=0.128, orientation='h',
                   size=(40, 20),  resolution=0.1, key='-MB-SLIDER-'),
         sg.Button('CHANGE', size=(10, 2), key='-CHANGE-MB-')],

    ])

    # Create a frame for setting VM datetime
    data_frame = sg.Frame('Set VM Datetime', [
        [sg.InputText(key='date_input'),
        sg.Button('Set', key='set_date_button'),
        sg.Button('Reset', key='reset_date_button')], [sg.Text('Format: YYYY-MM-DDTHH:MM:SS')],
    ])

    # Create a tab group for organizing different sections
    tab_group = sg.TabGroup([
        [
            sg.Tab('Media', [
                [iso_frame]
            ]),
            sg.Tab('Plugins', [
                [plugins_frame]
            ]),
            sg.Tab('Snapshots', [
                [snapshot_frame]
            ]),
            sg.Tab('Finetuning', [
                [finetune_frame],
                [data_frame],
            ]),
        ]
    ])

    # Define the layout for the virtualize tab
    virtualize_layout = [
        [sg.Column([[convert_frame], [vm_control_frame]],
                   element_justification='left',
                   vertical_alignment='top'),
        sg.Column([[tab_group]],
                   element_justification='left',
                   vertical_alignment='top'),
        sg.Column([[screenshot_frame], [memory_frame], [tools_frame], [network_frame]],
                   element_justification='left',
                   vertical_alignment='top')],
        [sg.Text("Cannot communicate with the ForensicVM Server. Please check access configuration on the "
                 "config tab, or check if the server is running. Press the test server button to see if it is running.",
                 key="alert_server_off", visible=False)]
    ]


    # Create the virtualize tab
    virtualize_tab = sg.Tab("Virtualize", virtualize_layout, element_justification="left")
    
    # layout for the configuration tab
    config_layout = [
        [sg.Frame("Forensic VM Server Configuration",
                 [
                     [sg.Text("Forensic VM server address:"),
                                    sg.InputText(key="server_address",
                                                 default_text=config.get("server_address", ""))],
                  [sg.Text("Forensic API:"), sg.InputText(key="forensic_api",
                                                default_text=config.get("forensic_api", "")),
                   sg.Button("Test Server Connection", key="test_forensicServer_connect"),
                   sg.Button("Start ForensicVM server", key="start_server_ssh_button", size=(25, 1), visible=True,
                     disabled=False)
                   ],

                 ]
                 )
         ],
        [sg.Frame("Windows Share over Forensic SSH Server Redirection",
                  [
                  [sg.Text("SSH Server Address and port:"),
                    sg.InputText(key="ssh_server_address",
                                 default_text=config.get("ssh_server_address", ""), size=(20,1)),
                   sg.InputText(key="ssh_server_port",
                                 default_text=config.get("ssh_server_port", ""),size=(8,1)),
                   sg.Button("Copy ssh key to server", key="copy-ssh-key-to-server"),
                   sg.Button("Test Ssh connection", key="test_ssh_connect")                   
                   ],
                  ]
                  )],

        [sg.Frame("Forensic Image source and windows share",
                  [

                      [sg.Text("Windows folder share server:"), sg.InputText(key="folder_share_server",
                                                               default_text=image_config.get("folder_share_server",
                                                                                             config.get("folder_share_server", "")))],
        [sg.Text("Share login:"), sg.InputText(key="share_login", default_text=image_config.get("share_login",
                                                                                                config.get("share_login", "")))],
        [sg.Text("Share password:"), sg.InputText(key="share_password", password_char="*",
                                                  default_text=image_config.get("share_password",
                                                                                config.get("share_password", "")))],
        [sg.Text("Local ou remote path to share:"),sg.InputText(key="equivalence",
                                                                default_text=image_config.get("equivalence",
                                                                                              config.get("equivalence", ""))),
         sg.Button("Autofill info", key="autofill_share"),
         sg.Button("Create share", key="create_windows_share"),
         sg.Button("Test windows share", key="test_windows_share")],
         

                  ]
                  )],

        [sg.Button("Save Configuration", key="save_button", size=(20,3))],
        [sg.Text("", key="output_text")]
    ]
    config_tab = sg.Tab("Configuration", config_layout, key="config_tab")


    # Layout for the autopsy data
    autopsy_layout = [
        [sg.Frame("Case data",
                 [
                     [sg.Text("Forensic Image Path:"),
                      # multiline textbox with size 20,
                      sg.InputText(key="forensic_image_path",
                                   default_text=image_path_arg, size=(50,3), disabled=True)],





                     [sg.Text("Case Path:"),
                      sg.InputText(key="case_image_path",
                                   default_text=case_directory_arg, size=(50, 3), disabled=True)],

                     [sg.Text("Case Name:"),
                      sg.InputText(key="case_name",
                                   default_text=case_name_arg, size=(50, 3), disabled=True)],

                     [sg.Text("Case Number:"),
                      sg.InputText(key="case_number",
                                   default_text=case_number_arg, size=(50, 3), disabled=True)],

                     [sg.Text("Case Examiner:"),
                      sg.InputText(key="case_examiner",
                                   default_text=case_examiner_arg, size=(50, 3), disabled=True)]

                 ])
    ], [sg.Frame("Generated UUID",   [[sg.Text("Unique Path and Case UUID"),
                                       sg.Text(string_to_uuid(image_path_arg+case_name_arg))]]),

        ], [sg.Frame("Case Tags", [
        [sg.Multiline(case_tags_str, size=(120, 5), disabled=True)],
    ]),
            ]
    ]

    # Create a tab for Autopsy case
    autopsy_tab = sg.Tab("Autopsy case", autopsy_layout, key="autopsy_tab")


    # Create the about tab
    about_layout = [
        [sg.Text("Forensic VM Client", font=("Helvetica", 20), justification="center")],
        [sg.Image("forensicVMClient.png")],
        [sg.Text("Version 1.0", justification="center")],
        [sg.Text("This software is provided as-is, without warranty of any kind. Use at your own risk.")],
        [sg.Multiline(default_text="Copyright (c) 2023 Nuno Mourinho - This software was created as "
                                   "part of a Master's degree in Cybersecurity Engineering at Escola Superior de "
                                   "Tecnologia e Gestão de Beja. All rights reserved.", size=(65, 3), disabled=True)],
    ]

    # Create a tab for the About section
    about_tab = sg.Tab("About", about_layout, element_justification="center")

    # Define the layout for the output section
    output_layout = [
        [sg.Output(size=(100, 25), key="-OUTPUT-",
                   background_color='black',
                   text_color='white',
                   font=('Courier New', 12))]
    ]

    # Create a tab for the Output Console
    output_tab = sg.Tab("Output Console", output_layout, element_justification="left")

    # Create the layout for the window
    layout = [
        [sg.TabGroup([
            #[sg.TabGroup([[virtualize_tab, autopsy_tab, config_tab, about_tab]])],
            [sg.TabGroup([[virtualize_tab, autopsy_tab, config_tab, output_tab, about_tab]])],
        ])]
    ]


    # Create the main application window
    window = sg.Window("Autopsy ForensicVM Client", layout, element_justification="center", icon=icon_path)


    # Event loop
    while True:
        # Read events from the window with a timeout of 1000 milliseconds (1 second)
        event, values = window.read(timeout=1000)

        # Check if the event is a timeout event
        if event == sg.TIMEOUT_EVENT:

            # Test if the vm exists
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            server_ok = 1
            # Check if the server is not offline
            # The server_offline variable indicates whether the server is offline or not

            # Call the test_api_key() function to test the forensic API key
            if not server_offline:
                server_ok, _ = test_api_key(forensic_api, web_server_address)
                if server_ok != 0:
                    # Check if the server is okay (the forensic API key is valid)
                    # The server_ok variable stores the result of the test_api_key() function

                    # Disable certain buttons and display an alert message
                    window["convert_to_vm_button"].update(disabled=not False)
                    window["link_to_vm_button"].update(disabled=not False)
                    window["alert_server_off"].update(visible=True)
                    window["start_vm_button"].update(disabled=not False)
                    window["stop_vm_button"].update(disabled=not False)
                    window["screenshot_vm_button"].update(disabled=not False)
                    window["download_memory_button"].update(disabled=not False)
                    window["save_screenshots_vm_button"].update(disabled=not False)
                    window["delete_vm_button"].update(disabled=not False)
                    window["reset_vm_button"].update(disabled=not False)
                    window["import_evidence_button"].update(disabled=not False)
                    window["open_forensic_vm_button"].update(disabled=not False)
                    window["open_forensic_shell_button"].update(disabled=not False)
                    window["open_forensic_netdata_button"].update(disabled=not False)
                    window["-RUN PLUGIN-"].update(disabled=True)
                    server_offline = True

            if server_ok == 0:
                # Check if the server is not okay (the forensic API key is invalid)
                # The server_ok variable stores the result of the test_api_key() function

                if first_run:
                    # Check if it is the first run of the application
                    # The first_run variable indicates whether it is the first run or not

                    # Perform the initial setup of the form
                    formInit(values, window)
                    first_run = False
                
                window["alert_server_off"].update(visible=False)
                # Hide the alert message indicating that the server is offline

                vm_folder_exists = check_vm_exists(forensic_api, uuid_folder, web_server_address)

                if vm_folder_exists:
                    # Check if the VM folder exists
                    # The vm_folder_exists variable indicates whether the VM folder exists or not

                    # Disable or enable buttons based on the VM folder status
                    window["convert_to_vm_button"].update(disabled=not False)
                    window["link_to_vm_button"].update(disabled=not False)
                    window["delete_vm_button"].update(disabled=False)
                    window["open_forensic_vm_button"].update(disabled=not False)
                    window["open_forensic_shell_button"].update(disabled=not True)
                    window["open_forensic_netdata_button"].update(disabled=not True)
                    window["save_screenshots_vm_button"].update(disabled=not True)

                    # Call the get_forensic_image_info() function to retrieve forensic image information
                    return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
                    # The get_forensic_image_info() function retrieves information about the forensic image and returns the result in return_code and 
                    # vm_status variables
                    # The forensic_api, uuid_folder, and web_server_address are the parameters passed to the function                    

                    if check_tap_interface(web_server_address, uuid_folder, forensic_api):
                        # Check if the TAP interface exists for the VM
                        # The check_tap_interface() function is called with the web server address, UUID folder, and forensic API as parameters

                        # Update button properties based on the result of the TAP interface check
                        window['insert_network_button'].update(disabled=True)
                        window['remove_network_button'].update(disabled=False)
                        # Disable the "Insert Network" button and enable the "Remove Network" button
                    else:
                        # If the TAP interface does not exist for the VM

                        # Update button properties based on the result of the TAP interface check                        
                        window['insert_network_button'].update(disabled=False)
                        window['remove_network_button'].update(disabled=True)
                        # Enable the "Insert Network" button and disable the "Remove Network" button                        

                    if vm_status.get("vm_status", "") == "running":
                        # Check if the VM status is "running"
                        # The vm_status dictionary is checked for the "vm_status" key and its value is compared to "running"

                        # Update button properties based on the VM status                        
                        window["delete_vm_button"].update(disabled=True)
                        window["start_vm_button"].update(disabled=not False)
                        window["screenshot_vm_button"].update(disabled=not True)
                        window["download_memory_button"].update(disabled=not True)
                        window["shutdown_vm_button"].update(disabled=not True)
                        window["stop_vm_button"].update(disabled=not True)
                        window["reset_vm_button"].update(disabled=not True)
                        window["import_evidence_button"].update(disabled=not False)
                        window["open_forensic_vm_button"].update(disabled=not True)
                        window["save_screenshots_vm_button"].update(disabled=not True)
                        window["recreate_evidence_disk_button"].update(disabled=True)
                        window["-RUN PLUGIN-"].update(disabled=True)
                        vm_stopped = False
                        # Set the vm_stopped variable to False to indicate that the VM is not stopped                        

                    elif vm_status.get("vm_status", "") == "stopped":
                        # Check if the VM status is "stopped"
                        # The vm_status dictionary is checked for the "vm_status" key and its value is compared to "stopped"

                        # Update button properties based on the VM status                        
                        window["delete_vm_button"].update(disabled=False, visible=True)
                        window["start_vm_button"].update(disabled=not True)
                        window["screenshot_vm_button"].update(disabled=not False)
                        window["download_memory_button"].update(disabled=not False)
                        window["shutdown_vm_button"].update(disabled=not False)
                        window["stop_vm_button"].update(disabled=not False)
                        window["reset_vm_button"].update(disabled=not False)
                        window["import_evidence_button"].update(disabled=not True)
                        window["recreate_evidence_disk_button"].update(disabled=False)
                        window["save_screenshots_vm_button"].update(disabled=not True)
                        window["-RUN PLUGIN-"].update(disabled=False)
                        vm_stopped = True
                        # Set the vm_stopped variable to True to indicate that the VM is stopped

                        if not folders_created:
                            # Check if the evidence folders with Autopsy tags for the VM have not been created yet
                            # The folders_created variable indicates whether the folders have been created or not

                            # Retrieve the necessary values from the form                            
                            forensic_image_path = values["forensic_image_path"]
                            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                            web_server_address = values["server_address"]
                            forensic_api = values["forensic_api"]

                            # Create the necessary folders in the Qcow2 background                            
                            create_folders_in_qcow2_background(forensic_api, web_server_address, uuid_folder, case_tags)
                            # The create_folders_in_qcow2_background() function is called with the necessary parameters to create the folders

                            folders_created = True
                else:
                    # If the VM status is neither "running" nor "stopped"

                    # Update button properties based on the VM status
                    window["convert_to_vm_button"].update(disabled=False)
                    window["link_to_vm_button"].update(disabled=False)
                    window["delete_vm_button"].update(disabled=True)
                    window["open_forensic_vm_button"].update(disabled=True)
                    window["open_forensic_shell_button"].update(disabled=False)
                    window["open_forensic_netdata_button"].update(disabled=False)
                    window["save_screenshots_vm_button"].update(disabled=True)
                    window["start_vm_button"].update(disabled=True)
            elif not server_offline:
                # Check if the server is not offline
                # The server_offline variable is checked for its negation

                # Update button properties based on the server status                
                window["convert_to_vm_button"].update(disabled=not True)
                window["link_to_vm_button"].update(disabled=not True)
                window["delete_vm_button"].update(disabled=not False)
                window["download_memory_button"].update(disabled=not False)
                window["save_screenshots_vm_button"].update(disabled=not True)
                window["open_forensic_shell_button"].update(disabled=not False)
                window["open_forensic_netdata_button"].update(disabled=not False)


        if event == sg.WINDOW_CLOSED:
            # Check if the event is a window close event
            # The event variable is checked against sg.WINDOW_CLOSED            
            break
            # Exit the loop to stop the program execution


        elif event == 'reset_date_button':
            # Check if the event is the "reset_date_button" button event
            # The event variable is checked against the string value 'reset_date_button'

            try:
                # Attempt to execute the following code block

                # Retrieve the necessary values from the form                
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                web_server_address = values["server_address"]
                forensic_api = values["forensic_api"]
                # Call the remove_vm_datetime() function to reset the VM's date and time
                if remove_vm_datetime(web_server_address, uuid_folder, forensic_api):
                    # If the date and time reset is successful

                    # Display a popup message indicating that the date has been reset
                    sg.Popup('Date reseted. Please reboot the VM')
                else:
                    # If there was an error resetting the date and time                    
                    sg.popup_error('Error reseting date.')
                    # Display a popup error message
            except Exception as e:
                # Catch any exceptions that occur during the execution of the code block

                print(str(e))
                # Print the error message to the console



        elif event == 'set_date_button':
            # Check if the event is the "set_date_button" button event
            # The event variable is checked against the string value 'set_date_button'

            try:
                # Attempt to execute the following code block

                # Validate the input date and time
                if validate_date(values['date_input']):
                    # If the date and time is valid

                    # Retrieve the necessary values from the form                    
                    forensic_image_path = values["forensic_image_path"]
                    uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                    web_server_address = values["server_address"]
                    forensic_api = values["forensic_api"]

                    # Call the change_vm_datetime() function to set the VM's date and time                    
                    if change_vm_datetime(web_server_address, uuid_folder, values['date_input'], forensic_api):
                        # If the date and time is successfully set                        
                        sg.Popup('The date and time is valid. Date Changed. Please reboot the VM')
                        # Display a popup message indicating that the date and time is changed
                    else:
                        # If the input date and time is invalid
                        sg.popup_error('Error setting date.')
                        # Display a popup error message
                else:
                    # Catch any exceptions that occur during the execution of the code block
                    sg.popup_error('The date and time is invalid, please try again.')
                    # Print the error message to the console
            except Exception as e:
                print(str(e))


        elif event == '-CHANGE-MB-':
            # Check if the event is the "-CHANGE-MB-" button event
            # The event variable is checked against the string value '-CHANGE-MB-'
            try:
                # Attempt to execute the following code block

                # Retrieve the necessary values from the form
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                web_server_address = values["server_address"]
                forensic_api = values["forensic_api"]

                # Call the change_memory_size() function to change the VM's memory size
                change_memory_size(forensic_api, web_server_address, uuid_folder, values["-MB-SLIDER-"] * 1024)

                # Display a popup message indicating the successful memory size change
                sg.popup(f"Memory size changed to {values['-MB-SLIDER-']} GB")
            except Exception as e:
                # Catch any exceptions that occur during the execution of the code block
                print(str(e))
                # Print the error message to the console                                


        elif event == '-DELETE SNAPSHOT-':
            # Check if the event is the "-DELETE SNAPSHOT-" button event
            # The event variable is checked against the string value '-DELETE SNAPSHOT-'

            try:
                # Attempt to execute the following code block

                # Retrieve the necessary values from the form                
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                web_server_address = values["server_address"]
                forensic_api = values["forensic_api"]
                selected_files = values['-SNAPSHOT-LIST-']
                if selected_files:
                    # Check if any snapshot is selected from the snapshot list                    

                    snap_filename = selected_files[0]                    
                    # Get the selected snapshot filename

                    # Find out the snapshot name from inside the file name using regular expression                    
                    match = re.search(r'\((.*?)\)', snap_filename)
                    if match:
                        snapshot_name =match.group(1)
                        # Extract the snapshot name from the matched group                        

                        if sg.PopupYesNo("Are you sure you want to delete the snapshot " +
                                         snapshot_name + "?", title="") == "Yes":
                            # Display a popup confirmation message to confirm snapshot deletion

                            # Call the delete_snapshot() function to delete the specified snapshot                                  
                            delete_snapshot(forensic_api, web_server_address, uuid_folder, snapshot_name)

                            # Update the snapshot list after deletion                           
                            snapshot_info_list = list_snapshots(forensic_api, uuid_folder, web_server_address)
                            window['-SNAPSHOT-LIST-'].update(snapshot_info_list)

                            # Display a popup message indicating the successful deletion of the snapshot
                            sg.popup(f"Deleted snapshot {snapshot_name}")

            except Exception as e:                
                # Catch any exceptions that occur during the execution of the code block
                print(str(e))
                # Print the error message to the console          


        elif event == '-ROLLBACK SNAPSHOT-':
            # Check if the event is the "-ROLLBACK SNAPSHOT-" button event
            # The event variable is checked against the string value '-ROLLBACK SNAPSHOT-'

            try:
                # Attempt to execute the following code block

                # Retrieve the necessary values from the form
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                web_server_address = values["server_address"]
                forensic_api = values["forensic_api"]
                selected_files = values['-SNAPSHOT-LIST-']

                if selected_files:
                    # Check if any snapshot is selected from the snapshot list                    
                    snap_filename = selected_files[0]
                    # Get the selected snapshot filename

                    # Find out the snapshot name from inside the file name using regular expression 
                    match = re.search(r'\((.*?)\)', snap_filename)
                    if match:
                        snapshot_name =match.group(1)
                        # Extract the snapshot name from the matched group

                        # Call the rollback_snapshot() function to rollback to the specified snapshot
                        rollback_snapshot(forensic_api, web_server_address, uuid_folder, snapshot_name)

                        # Update the snapshot list after rollback                    
                        snapshot_info_list = list_snapshots(forensic_api, uuid_folder, web_server_address)
                        window['-SNAPSHOT-LIST-'].update(snapshot_info_list)

                        # Display a popup message indicating the successful rollback to the snapshot
                        sg.popup(f"Reverted to snapshot {snapshot_name}")

            except Exception as e:
                # Catch any exceptions that occur during the execution of the code block
                print(str(e))
                # Print the error message to the console



        elif event == '-CREATE SNAPSHOT-':
            # Check if the event is the "-CREATE SNAPSHOT-" button event
            # The event variable is checked against the string value '-CREATE SNAPSHOT-'

            try:
                # Attempt to execute the following code block

                # Retrieve the necessary values from the form                
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                web_server_address = values["server_address"]
                forensic_api = values["forensic_api"]

                # Call the create_snapshot() function to create a new snapshot                
                create_snapshot(forensic_api, uuid_folder, web_server_address)

                # Update the snapshot list after creating a new snapshot
                snapshot_info_list = list_snapshots(forensic_api, uuid_folder, web_server_address)
                window['-SNAPSHOT-LIST-'].update(snapshot_info_list)

                # Display a popup message indicating the successful creation of the snapshot
                sg.popup(f"Snapshot created")

            except Exception as e:                
                # Catch any exceptions that occur during the execution of the code block
                print(str(e))
                # Print the error message to the console



        elif event == '-LIST SNAPSHOTS-':
            # Check if the event is the "-LIST SNAPSHOTS-" button event
            # The event variable is checked against the string value '-LIST SNAPSHOTS-'

            # Retrieve the necessary values from the form
            forensic_api = values["forensic_api"]
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]

            # Call the list_snapshots() function to retrieve the list of snapshots
            snapshot_info_list=list_snapshots(forensic_api, uuid_folder, web_server_address)

             # Update the snapshot list in the UI with the retrieved snapshot information
            window['-SNAPSHOT-LIST-'].update(snapshot_info_list)


        elif event == 'start_server_ssh_button':
            # Check if the event is the "start_server_ssh_button" button event
            # The event variable is checked against the string value 'start_server_ssh_button'

            # Retrieve the necessary values from the form            
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            server_address = values["ssh_server_address"]
            server_port = values["ssh_server_port"]

            # Call the start_server_remotessh() function to start the remote SSH server
            start_server_remotessh(server_address, server_port)


        elif event == 'debug_ssh_button':
            # Check if the event is the "debug_ssh_button" button event
            # The event variable is checked against the string value 'debug_ssh_button'

            # Retrieve the necessary values from the form
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            server_address = values["ssh_server_address"]
            server_port = values["ssh_server_port"]

            # Call the debug_remotessh() function to perform remote SSH debugging
            debug_remotessh(server_address, server_port,uuid_folder )


        elif event == 'recreate_evidence_disk_button':
            # Check if the event is the "recreate_evidence_disk_button" button event
            # The event variable is checked against the string value 'recreate_evidence_disk_button'

            # Show a confirmation dialog to confirm deleting the evidence disk
            response = sg.PopupYesNo('Do you want delete the evidence disk?', title='Confirmation')
            if response == 'Yes':
                # If the user confirms deleting the evidence disk, show another confirmation dialog for extra confirmation
                response_2 = sg.PopupYesNo('ARE YOU REALLY SURE?', title='Confirmation')

                if response_2 == 'Yes':
                    # If the user confirms again, proceed with recreating the evidence disk
                    # Retrieve the necessary values from the form                    
                    forensic_image_path = values["forensic_image_path"]
                    uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                    web_server_address = values["server_address"]
                    forensic_api = values["forensic_api"]

                    # Call the recreate_folders() function to recreate the evidence disk folders
                    recreate_folders(forensic_api, web_server_address, uuid_folder, case_tags)
                    folders_created = True

                    # Display a success message                  
                    print('Evidence Drive recreated')
                    sg.popup("Evidence Drive recreated")
            else:
                # If the user chooses not to delete the evidence disk, display a message
                print('Delete action aborted')


        elif event == '-EJECT-':
            # Check if the event is the "-EJECT-" button event
            # The event variable is checked against the string value '-EJECT-'

            try:
                # Try to execute the following code block, which handles the CD-ROM ejection process

                # Retrieve the necessary values from the form                
                api_key = values["forensic_api"]
                base_url = values["server_address"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)

                # Call the eject_cdrom() function to eject the CD-ROM                
                response = eject_cdrom(api_key, base_url, uuid_folder)

                if response:
                    # If the response is not empty, print the response (e.g., success message)
                    print(response)
                    sg.popup("CD-ROM ejected")
                else:
                    # If the response is empty, print a failure message
                    print("Failed to eject CD-ROM")
                    sg.popup_error("Failed to eject CD-ROM")
            except Exception as e:
                 print(str(e))


        elif event == 'download_wireshark_button':
            # Check if the event is the "download_wireshark_button" button event
            # The event variable is checked against the string value 'download_wireshark_button'

            # Retrieve the necessary values from the form
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]

            # Prompt the user to choose the path to save the network pcap files
            save_path = sg.popup_get_file('Choose the path to save the network pcap files',
                                          save_as=True,
                                          no_window=True,
                                          default_extension=".zip",
                                          default_path=f"{case_image_folder}/pcap.zip",
                                          file_types=(("Zip files", "*.zip"),))
            if save_path:
                # If a save path is selected by the user, proceed to download the network pcap files

                try:
                    # Try to download the network pcap files using the download_pcap() function
                    download_pcap(forensic_api, uuid_folder, web_server_address, save_path)

                    saved_path = os.path.dirname(save_path)                    
                    sg.popup(f"Network pcap files downloaded and saved at {save_path}. Opening path")
                    os.startfile(saved_path)
                    

                except Exception as e:
                    # If an exception occurs during the execution of the code block, display an error popup
                    sg.popup_error(f'Failed to download network pcap files {str(e)}')


        elif event == 'insert_network_button':
            # Check if the event is the "insert_network_button" button event
            # The event variable is checked against the string value 'insert_network_button'

            try:
                # Try to execute the code block within the try block

                # Retrieve the necessary values from the form                
                api_key = values["forensic_api"]
                base_url = values["server_address"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
        
                # Start the TAP interface by calling the start_tap_interface() function                
                response = start_tap_interface(base_url, uuid_folder, api_key)

                if response:
                    # If the TAP interface was successfully started, check if the interface is active
                    if check_tap_interface(base_url, uuid_folder, api_key):
                        # If the interface is active, display a success message and update button states
                        print(response)                        
                        sg.popup("Network card inserted")

                        # Update the button states
                        window['insert_network_button'].update(disabled=True)
                        window['remove_network_button'].update(disabled=False)
                else:
                    # If the TAP interface failed to start, display an error message
                    print("Failed to insert network card")
                    sg.popup_error("Failed to insert network card")

            except Exception as e:
                 # If an exception occurs during the execution of the code block, print the exception message
                 print(str(e))
                 sg.popup_error(f'Failed to enable network card {str(e)}')


        elif event == 'remove_network_button':
            # Check if the event is the "remove_network_button" button event
            # The event variable is checked against the string value 'remove_network_button'
            try:
                # Try to execute the code block within the try block

                # Retrieve the necessary values from the form                
                api_key = values["forensic_api"]
                base_url = values["server_address"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)

                # Stop the TAP interface by calling the stop_tap_interface() function               
                response = stop_tap_interface(base_url, uuid_folder, api_key)
                if response:
                    # If the TAP interface was successfully stopped, check if the interface is disabled

                    if not check_tap_interface(base_url, uuid_folder, api_key):
                        # If the interface is disabled, display a success message and update button states
                        print(response)
                        sg.popup("Network card disabled")

                        # Update the button states
                        window['insert_network_button'].update(disabled=False)
                        window['remove_network_button'].update(disabled=True)
                else:
                    # If disabling the TAP interface failed, display an error message
                    print("Failed to disable network card")
                    sg.popup_error("Failed to disable network card")

            except Exception as e:
                # If an exception occurs during the execution of the code block, print the exception message                 
                 print(str(e))
                 sg.popup_error(f'Failed to disable network card {str(e)}')


        elif event == '-INSERT-':
            # Check if the event is the "-INSERT-" event
            # The event variable is checked against the string value '-INSERT-'

            try:
                # Try to execute the code block within the try block

                # Retrieve the necessary values from the form                
                api_key = values["forensic_api"]
                base_url = values["server_address"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                selected_files = values['-CDROM LIST-']

                if selected_files:
                    # Check if any CD-ROM file is selected
                    iso_filename = selected_files[0]

                    # Insert the CD-ROM by calling the insert_cdrom() function
                    response = insert_cdrom(api_key, base_url, uuid_folder, iso_filename)

                    if response:
                        # If the CD-ROM was successfully inserted, display a success message

                        print(response)
                        sg.popup("CD-ROM inserted")
                    else:
                        # If inserting the CD-ROM failed, display an error message

                        print("Failed to insert CD-ROM")
                        sg.popup_error("Failed to insert CD-ROM")

            except Exception as e:
                 # If an exception occurs during the execution of the code block, print the exception message

                 print(str(e))
                 sg.popup_error(f'Failed to insert CD-ROM {str(e)}')



        elif event == '-RUN PLUGIN-':
            # Check if the event is the "-RUN PLUGIN-" event
            # The event variable is checked against the string value '-RUN PLUGIN-'

            try:
                # Try to execute the code block within the try block

                # Retrieve the necessary values from the form                
                api_key = values["forensic_api"]
                base_url = values["server_address"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                selected_files = values['-PLUGIN LIST-']

                if selected_files:
                    # Check if any plugin file is selected
                    pattern = r'\((.*?)\)'
                    matches = re.findall(pattern, selected_files[0])

                    # Check if any matches found
                    if matches:
                        plugin_dir = matches[0]

                        # Run the selected plugin by calling the run_plugin() function
                        response = run_plugin(api_key, base_url, plugin_dir, uuid_folder)

                        if response:
                            # If the plugin was successfully run, print the response

                            print(response)
                            sg.popup("Plugin run")
                        else:
                            # If running the plugin failed, print an error message

                            print("Failed to run plugin")
                            sg.popup_error("Failed to run plugin")
                        

            except Exception as e:
                 # If an exception occurs during the execution of the code block, print the exception message

                 print(str(e))
                 sg.popup_error(f'Failed to run plugin {str(e)}')


        elif event == '-DELETE-':
            # Check if the event is the "-DELETE-" event
            # The event variable is checked against the string value '-DELETE-'
            
            try:
                # Try to execute the code block within the try block

                # Get the selected ISO file from the Listbox                
                selected_files = values['-CDROM LIST-']
                
                if selected_files:
                    # Check if any ISO file is selected
                    iso_filename = selected_files[0]

                    # Call the delete_iso function to delete the selected ISO file                    
                    api_key = values["forensic_api"]
                    base_url = values["server_address"]
                    deleted = delete_iso(api_key, base_url, iso_filename)

                    if deleted:
                        # If the ISO file was successfully deleted, update the Listbox with the remaining ISO files

                        web_server_address = values["server_address"]
                        forensic_api = values["forensic_api"]
                        try:
                            # Attempt to list the ISO files again after the deletion
                            iso_files = list_iso_files(forensic_api, web_server_address)

                            if iso_files:
                                # If ISO files are successfully listed, update the Listbox with the updated ISO files

                                sg.popup("ISO files deleted")
                                print(iso_files)
                                window['-CDROM LIST-'].update(iso_files['iso_files'])

                        except Exception as e:
                            # If an exception occurs while listing ISO files, print the exception message

                            print(str(e))
                            sg.popup_error(f'Failed to list ISO files {str(e)}')
                    else:
                        # If deleting the ISO file failed, display an error message
                        sg.popup_error("Failed to delete ISO file")

            except Exception as e:
                # If an exception occurs during the execution of the code block, print the exception message
                print(str(e))
                sg.popup_error(f'Failed to delete ISO file {str(e)}')



        elif event == '-BROWSE-':
            # Check if the event is the "-BROWSE-" event

            try:
                # Try to execute the code block within the try block

                # Open a file dialog to browse and select an ISO file                
                save_path = sg.popup_get_file('Choose iso file',
                                              save_as=False,
                                              no_window=True,
                                              default_extension=".iso",
                                              file_types=(("Iso Files", "*.iso"),))

                if save_path:
                    # Check if a file path is selected                    
                    api_key = values["forensic_api"]
                    base_url = values["server_address"]

                    # Call the upload_iso function to upload the selected ISO file
                    result = upload_iso(api_key, base_url, save_path)

                    if result:
                        # If the ISO file upload is successful, display a success message

                        sg.popup('Upload successful')

                        
                        web_server_address = values["server_address"]
                        forensic_api = values["forensic_api"]
                        
                        try:
                            # Attempt to list the ISO files again after the upload

                            iso_files = list_iso_files(forensic_api, web_server_address)
                            if iso_files:
                                # If ISO files are successfully listed, update the Listbox with the updated ISO files    

                                window['-CDROM LIST-'].update(iso_files['iso_files'])

                        except Exception as e:
                            # If an exception occurs while listing ISO files, print the exception message
                            print(str(e))
                            sg.popup_error(f'Failed to list ISO files {str(e)}')

                    else:
                        # If the ISO file upload fails, display an error message

                        sg.popup_error('Upload failed')

            except Exception as e:
                # If an exception occurs during the execution of the code block, print the exception message

                print(str(e))
                sg.popup_error(f'Failed to upload ISO file {str(e)}')


        elif event == '-LIST-':
            # Check if the event is the "-LIST-" event
            # The event variable is checked against the string value '-LIST-'

            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            try:
                # Try to execute the code block within the try block

                # Call the list_iso_files function to list the available ISO files
                iso_files = list_iso_files(forensic_api, web_server_address)

                if iso_files:
                    # If ISO files are successfully listed, update the Listbox with the updated ISO files                    
                    window['-CDROM LIST-'].update(iso_files['iso_files'])
                    sg.popup("ISO files listed")

            except Exception as e:
                # If an exception occurs during the execution of the code block, print the exception message
                sg.popup_error(f'Failed to list ISO files {str(e)}')
                print(str(e))


        elif event == '-LIST PLUGINS-':
            # Check if the event is the "-LIST PLUGINS-" event
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]

            try:
                # Try to execute the code block within the try block

                # Call the list_plugins function to list the available plugins
                plugins = list_plugins(forensic_api, web_server_address)

                if plugins:
                    # If plugins are successfully listed, update the Listbox with the plugin information
                    plugin_list = []

                    for plugin in plugins:
                        # Iterate over each plugin and extract the necessary information

                        plugin_dir = plugin.get('plugin_dir')
                        #print(plugin_dir)

                        plugin_name = plugin.get('plugin_name')
                        #print(plugin_name)

                        plugin_description = plugin.get('plugin_description')
                        #print(plugin_description)

                        # Append the formatted plugin information to the plugin_list
                        plugin_list.append(f"{plugin_name} - {plugin_description} ({plugin_dir}) ")

                    # Update the Listbox with the updated plugin_list
                    window['-PLUGIN LIST-'].update(plugin_list)
                    sg.popup("Plugins listed")

            except Exception as e:
                # If an exception occurs during the execution of the code block, print the exception message
                print(str(e))
                sg.popup_error(f'Failed to list plugins {str(e)}')



        elif event == "save_screenshots_vm_button":
            # Check if the event is the "save_screenshots_vm_button" event

            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            save_path = sg.popup_get_file('Choose the path to save the screenshots',
                                          save_as=True,
                                          no_window=True,
                                          default_extension=".zip",
                                          default_path=f"{case_image_folder}/screenshots.zip",
                                          file_types=(("Zip files", "*.zip"),))
            try:
                # Try to execute the code block within the try block

                if save_path:
                    # If a valid save path is selected, proceed with downloading the screenshots

                    download_screenshots(forensic_api, uuid_folder, web_server_address, save_path)
                    # Call the download_screenshots function to download the screenshots
                    
                    saved_path = os.path.dirname(save_path)
                    sg.popup(f"Screenshots downloaded. Opening path {saved_path} in explorer")                    
                    os.startfile(saved_path)
                                        
                    # Open path in explorer and display a popup message to indicate that the 
                    # screenshots have been downloaded
                    

                else:
                    sg.popup_error("Canceled to download screenshots")
                    # Display a popup error message indicating that the user canceled the screenshot download

            except Exception as e:       
                # If an exception occurs during the execution of the code block, display an error popup
                         
                sg.popup_error(f'Failed to download screenshots {str(e)}')



        elif event == "import_evidence_button":
            # Check if the event is the "import_evidence_button" event            

            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            save_path = sg.popup_get_file('Choose the path to save probable evidence disk',
                                          save_as=True,
                                          no_window=True,
                                          default_extension=".vmdk",
                                          default_path=f"{case_image_folder}/evidence.vmdk",
                                          file_types=(("vmdk disk", "*.vmdk"),))
            try:
                # Try to execute the code block within the try block

                if save_path:
                    # If a valid save path is selected, proceed with downloading the evidence disk

                    download_evidence(forensic_api, uuid_folder, web_server_address, save_path)
                    # Call the download_evidence function to download the evidence disk

                    #sg.popup(f"Evidence disk downloaded and saved to {save_path}. Close to open path in explorer. Then import the evidence disk in Autopsy Software")
                    # Display a popup message to indicate that the evidence disk has been downloaded and saved to the specified path
                    
                    saved_path = os.path.dirname(save_path)
                    #sg.popup(f"Downloaded Evidence disk. Opening path {saved_path} in explorer")                    
                    os.startfile(saved_path)

                    # Open the saved path in the file explorer

                else:
                    sg.popup_error("Canceled to download evidence disk")
                    # Display a popup error message indicating that the user canceled the evidence disk download

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f'Failed to download evidence {str(e)}')


        elif event == "download_memory_button":
            # Check if the event is the "download_memory_button" event

            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]

            save_path = sg.popup_get_file('Choose the path to save the screenshots',
                                          save_as=True,
                                          no_window=True,
                                          default_extension=".dump",
                                          default_path=f"{case_image_folder}/memory.dump",
                                          file_types=(("Dump files", "*.dump"),))

            try:
                # Try to execute the code block within the try block

                if save_path:
                    # If a valid save path is selected, proceed with downloading the memory dump

                    download_memory_dump(forensic_api, uuid_folder, web_server_address, save_path)
                     # Call the download_memory_dump function to download the memory dump

                    sg.popup(f"Memory dump downloaded and saved to {save_path}. Close to open path in explorer. Then import the memory dump in Autopsy Software")
                    # Display a popup message to indicate that the memory dump has been downloaded and saved to the specified path

                    saved_path = os.path.dirname(save_path)
                    subprocess.Popen(f'explorer {saved_path}')
                    # Open the saved path in the file explorer

                else:
                    sg.popup_error("Canceled to download memory dump")
                    # Display a popup error message indicating that the user canceled the memory dump download

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup(f'Failed to download memory dump {str(e)}')



        elif event == "screenshot_vm_button":
            # Check if the event is the "screenshot_vm_button" event            

            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]

            try:
                # Try to execute the code block within the try block

                return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
                # Call the get_forensic_image_info function to retrieve information about the forensic image

                
                if vm_status.get("vm_status", "") == "running":
                    # If the VM status is "running", proceed with taking a screenshot

                    screenshot_vm(forensic_api, uuid_folder, web_server_address)
                    # Call the screenshot_vm function to take a screenshot of the VM

                    sg.popup("Screenshot taken")
                    # Display a popup message to indicate that the screenshot has been taken
                else:
                    sg.popup_error("Vm is not running. Screenshot not possible")

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f'Failed to take screenshot {str(e)}')
                # Display a popup error message indicating the error



        elif event == "reset_vm_button":
            # Check if the event is the "reset_vm_button" event

            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]

            try:
                # Try to execute the code block within the try block

                return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
                # Call the get_forensic_image_info function to retrieve information about the forensic image

                if vm_status.get("vm_status", "") == "running":
                    # If the VM status is "running", proceed with resetting the VM

                    reset_vm(forensic_api, uuid_folder, web_server_address)
                    # Call the reset_vm function to reset the VM

                    sg.popup("Vm reset")
                    # Display a popup message to indicate that the VM has been reset

                else:
                    # If the VM status is not "running", display an error popup message

                    sg.popup_error("Vm is not running. Reset not possible")

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f'Failed to reset vm {str(e)}')
                # Display a popup error message indicating that the VM reset failed


        elif event == "shutdown_vm_button":
            # Check if the event is the "shutdown_vm_button" event
            # Shutdown the VM

            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]

            try:
                # Try to execute the code block within the try block

                return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
                # Call the get_forensic_image_info function to retrieve information about the forensic image

                if vm_status.get("vm_status", "") == "running":
                    # If the VM status is "running", proceed with shutting down the VM

                    shutdown_vm(forensic_api, uuid_folder, web_server_address)
                    # Call the shutdown_vm function to shut down the VM

                    sg.popup("Vm shutdown")
                    # Display a popup message to indicate that the VM has been shutdown

                else:
                    sg.popup_error("Vm is not running. Shutdown not possible")

                    # Display a popup error message indicating that the VM shutdown failed

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f'Failed to shutdown vm {str(e)}')
                # Display a popup error message indicating that the VM shutdown failed


        elif event == "delete_vm_button":
            # Check if the event is the "delete_vm_button" event

            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]

            try:
                # Try to execute the code block within the try block

                return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
                # Call the get_forensic_image_info function to retrieve information about the forensic image

                if vm_status.get("vm_status", "") == "stopped":
                    # If the VM status is "stopped", proceed with deleting the VM
                    delete_vm(forensic_api, uuid_folder, web_server_address)

                else:
                    sg.popup_error("Vm is not stopped. Delete not possible")
                    # Display a popup error message indicating that the VM delete failed

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f'Failed to delete vm {str(e)}')
                # Display a popup error message indicating that the VM delete failed


        elif event == "start_vm_button":
            # Check if the event is the "start_vm_button" event

            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]

            try:
                # Try to execute the code block within the try block
                return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
                # Call the get_forensic_image_info function to retrieve information about the forensic image

                #print(vm_status)

                if vm_status["running_mode"]=="snap":
                    # If the VM is in snapshot mode, execute the code block for snapshot mode

                    server_address = values["ssh_server_address"]
                    server_port = values["ssh_server_port"]
                    windows_share = values["folder_share_server"]
                    share_login = values["share_login"]
                    share_password = values["share_password"]
                    forensic_image_path = values["forensic_image_path"]
                    uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                    copy = "copy"
                    replacement_share = values["equivalence"]

                    # Run ForensicVM in snapshot mode
                    run_snap(server_address,
                            server_port,
                            windows_share,
                            share_login,
                            share_password,
                            replacement_share,
                            forensic_image_path,
                            uuid_folder,
                            copy)
                    
                    sg.popup("ForensicVM started in snap mode. Do not close the command window. Please minimize it and processed to vm control")
                    # Display a popup message to indicate that the VM has been started in snap mode

                else:
                    # If the VM is not in snapshot mode, execute the code block for normal mode

                    start_vm(forensic_api, uuid_folder, web_server_address)
                    sg.popup("ForensicVm started in normal mode")

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f'Failed to start vm {str(e)}')


        elif event == "save_button":
            # Check if the event is the "save_button" event

            try:
                # Try to execute the code block within the try block

                # Save the configuration to the JSON file
                save_config(values, filename)

                # Create a dictionary containing the image-related values to be saved
                image_values = {
                    "folder_share_server": values["folder_share_server"],
                    "share_login": values["share_login"],
                    "share_password": values["share_password"],
                    "equivalence": values["equivalence"]
                }

                # Save the image-related values to a separate JSON file in the case image folder
                save_config(image_values, case_image_folder + "\\image-share.json")

                print("Configuration saved successfully!")
                sg.popup("Configuration saved successfully!")
                # Display a popup message to indicate that the configuration has been saved

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(str(e))
                # Display a popup error message indicating that the configuration save failed


        elif event == "convert_to_vm_button":
            # Check if the event is the "convert_to_vm_button" event

            print("Copy and convert...")
            sg.popup("The conversion will start in command window. Please do not close it until the conversion is finished...")

            # Extract the necessary values from the form
            server_address = values["ssh_server_address"]
            server_port = values["ssh_server_port"]
            windows_share = values["folder_share_server"]
            share_login = values["share_login"]
            share_password = values["share_password"]
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            copy = "copy"
            replacement_share = values["equivalence"]

            try:
                # Try to execute the code block within the try block

                if test_windows_share(values['folder_share_server'], values['share_login'], values['share_password']):  
                    # Run the remote openssh command to copy and convert the forensic image        
                    run_openssh(server_address,
                                server_port,
                                windows_share,
                                share_login,
                                share_password,
                                replacement_share,
                                forensic_image_path,
                                uuid_folder,
                                copy)

                    print("Convert")
                    sg.popup("Forensic Image converted sucessfully to a ForensicVM")
                    # Display a popup message to indicate that the forensic image has been converted

                    # Update the state of the buttons after the conversion is complete
                    window["convert_to_vm_button"].update(disabled=not False)
                    window["link_to_vm_button"].update(disabled=not False)
                    window["import_evidence_button"].update(disabled=not True)
                    window["open_forensic_vm_button"].update(disabled=not True)
                    window["stop_vm_button"].update(disabled=not True)
                    window["reset_vm_button"].update(disabled=not True)
                    window["open_forensic_shell_button"].update(disabled=not True)
                    window["open_forensic_netdata_button"].update(disabled=not True)
                else:
                    sg.popup_error("The image windows share does not exist, is not accessible or from a previous image. " \
                                           " Please check the configuration tab")

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup
                
                print(str(e))
                sg.popup_error(f"Error converting VM to a forensic VM {str(e)}")
                # Display a popup error message indicating that the forensic image conversion failed
                

        elif event == "link_to_vm_button":
            # Check if the event is the "link_to_vm_button" event

            try:
                # Try to execute the code block within the try block

                print("Link...")
                sg.popup("The conversion will start in command window. Please do not close it until the conversion is finished...")
                # Sucessfull message to indicate that the forensic image has been linked

                # Extract the necessary values from the form
                server_address = values["ssh_server_address"]
                server_port = values["ssh_server_port"]
                windows_share = values["folder_share_server"]
                share_login = values["share_login"]
                share_password = values["share_password"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                copy = "snap"
                replacement_share = values["equivalence"]
                web_server_address = values["server_address"]
                forensic_api = values["forensic_api"]

                return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
                # Call the get_forensic_image_info function to retrieve information about the forensic image

                if return_code != 0:
                    
                    if return_code!= 404:
                        # Error getting information about the forensic image
                        sg.popup_error("Could not connect to the server:\n" + vm_status)

                    else:
                        # Run the remote openssh command to convert the image to a VM
                        
                        if test_windows_share(values['folder_share_server'], values['share_login'], values['share_password']):  
                            # Check if the windows share exists and is accessible
                            
                            # Run the remote openssh command to convert the image to a VM                       
                            run_openssh(server_address,
                                        server_port,
                                        windows_share,
                                        share_login,
                                        share_password,
                                        replacement_share,
                                        forensic_image_path,
                                        uuid_folder,
                                        copy)
                            
                            sg.popup("Forensic Image linked sucessfully to the a new VM")
                            # Display a popup message to indicate that the forensic image has been linked

                            # Update the state of the buttons after the linking process is complete                
                            window["convert_to_vm_button"].update(disabled=not False)
                            window["link_to_vm_button"].update(disabled=not False)
                            window["import_evidence_button"].update(disabled=not True)
                            window["stop_vm_button"].update(disabled=not True)
                            window["reset_vm_button"].update(disabled=not True)
                            window["open_forensic_vm_button"].update(disabled=not True)
                            window["open_forensic_shell_button"].update(disabled=not True)
                            window["open_forensic_netdata_button"].update(disabled=not True)
                        else:
                            sg.popup_error("The image windows share does not exist, is not accessible or from a previous image. " \
                                           " Please check the configuration tab")
                else:
                    # Display error message to indicate that could not connect to the server
                    print(vm_status)
                    sg.popup_error("Could not connect to the server:\n" + vm_status)

                    if vm_status.get("vm_status", "") == "running":
                        # Show message to indicate that the machine is running and no actions are required
                        sg.popup("The machine is running.\n No actions required")

                        # Update the state of the buttons after the linking process is complete
                        window["convert_to_vm_button"].update(disabled=not False)
                        window["link_to_vm_button"].update(disabled=not False)
                        window["import_evidence_button"].update(disabled=not True)
                        window["stop_vm_button"].update(disabled=not True)
                        window["reset_vm_button"].update(disabled=not True)
                        window["open_forensic_vm_button"].update(disabled=not True)
                        window["open_forensic_shell_button"].update(disabled=not True)
                        window["open_forensic_netdata_button"].update(disabled=not True)

                    else:                        
                        continue

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))                    
                sg.popup_error(f"Error converting VM to a forensic VM {str(e)}")
                # Display a popup error message indicating that the forensic image conversion failed
                    
            

        elif event == "open_forensic_vm_button":
            # Check if the event is the "open_forensic_vm_button" event

            try:
                # get server address value
                print("Open ForensicVM Webserver...")

                 # Extract the necessary values from the form
                server_address = values["server_address"]
                return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
                # Call the get_forensic_image_info function to retrieve information about the forensic image

                print(vm_status)
                if return_code== 0:
                    webbrowser.open(f"{server_address}/screen?port={vm_status['websocket_port']}&uuid={uuid_folder}")
                else:
                    sg.popup_error(f"Error getting image information {vm_status}")

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f"Error opening browser {str(e)}")




        elif event == "stop_vm_button":
            # Check if the event is the "stop_vm_button" event
            try:
                # Try to execute the code block within the try block

                # get server address value                
                forensic_api = values["forensic_api"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                web_server_address = values["server_address"]

                # Call the stop_vm function to stop the VM
                stop_result = stop_vm(forensic_api, uuid_folder, web_server_address)

                if stop_result:
                    # If the stop_result is not None, the VM was stopped successfully            
                    print(f"VM stopped: {stop_result['vm_stopped']}")
                    sg.popup(f"VM stopped: {stop_result['vm_stopped']}")
                else:
                    # If the stop_result is None, there was an error stopping the VM            
                    sg.popup_error("Could not stop the VM")

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f"Error stopping VM {str(e)}")
                # Show an error message indicating that the VM could not be stopped





        elif event == "open_forensic_shell_button":
            # Check if the event is the "open_forensic_shell_button" event

            try:
                # get server address value
                print("Open ForensicVM Webserver...")
                # Extract the necessary value from the form
                server_address = values["server_address"] + "/shell"

                # Open the web browser to the specified server address
                webbrowser.open(server_address)

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f"Error opening browser {str(e)}")



        elif event == "open_forensic_netdata_button":
            # Check if the event is the "open_forensic_netdata_button" event

            try:
                
                print("Open ForensicVM Webserver...")
                
                # Extract the necessary value from the form
                # get server address value
                server_address = values["server_address"] + "/netdata"

                # Open the web browser to the specified server address
                webbrowser.open(server_address)

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f"Error opening browser {str(e)}")



        elif event == "test_ssh_connect":
            # Check if the event is the "test_ssh_connect" event

            try:
                # Try to execute the code

                # Call the test_ssh function to check the SSH connection
                if test_ssh(values['ssh_server_address'], values['ssh_server_port']):
                    # If the SSH connection is successful, display a success popup message            
                    sg.popup("Connected successfully!")
                else:
                    # If the SSH connection fails, display an error popup message            
                    sg.popup_error("Could not connect to the server")

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f"Error testing SSH connection {str(e)}")
                # Show an error message indicating that the SSH connection could not be established



        elif event == "test_windows_share":
            # Check if the event is the "test_windows_share" event

            try:                

                # Call the test_windows_share function to check the Windows share connection        
                if test_windows_share(values['folder_share_server'], values['share_login'], values['share_password']):
                    # If the Windows share connection is successful, display a success popup message
                    sg.popup("Connected successfully!")\
                    
                else:
                    # If the Windows share connection fails, display an error popup message            
                    sg.popup_error("Could not connect to the server")

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f"Error testing Windows share {str(e)}")



        elif event == "test_forensicServer_connect":
            # Check if the event is the "test_forensicServer_connect" event

            try:
                # Try to execute the code

                # Extract the necessary values from the form
                server_address = values["server_address"]
                forensic_api = values["forensic_api"]

                # Call the test_api_key function to test the connection to the Forensic Server API        
                return_code, message= test_api_key(forensic_api, server_address)

                if return_code != 0:
                    # If the connection fails, display an error popup message
                    sg.popup_error("Could not connect to the server:\n" +  message)

                else:
                    # If the connection is successful, display a success popup message            
                    sg.popup("Connected successfully!\n" + message)
                    server_offline = False

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f"Error testing Server API Connection {str(e)}")



        elif event == "copy-ssh-key-to-server":
            # Check if the event is the "copy-ssh-key-to-server" event

            try:
                # Try to execute the code

                # Get the SSH directory path
                ssh_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Call the generate_and_send_public_key function to generate and send the public key to the server
                message, status_code = generate_and_send_public_key(values["server_address"], values["forensic_api"],
                                                                    ssh_dir)
                
                if status_code!= 200:
                    # If the operation fails, display an error popup message
                    sg.popup_error(message)
                else:
                    # If the operation is successful, display a success popup message            
                    sg.popup(message)

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f"Error creating SSH key {str(e)}")



        elif event == "autofill_share":
             # Check if the event is the "autofill_share" event

            try:
                # Get the values from the PySimpleGUI window
                new_equivalence = os.path.dirname(os.path.realpath(image_path_arg))

                # Update the value of the 'equivalence' input field in the window with the new equivalence value        
                window.Element('equivalence').update(value=new_equivalence)

                # Create the Windows share folder path using the new equivalence value        
                new_share_folder = "\\\\127.0.0.1\\" + os.path.basename(new_equivalence)

                # Update the value of the 'folder_share_server' input field in the window with the new share folder path        
                window.Element('folder_share_server').update(value=new_share_folder)

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                print(str(e))
                sg.popup_error(f"Error autofilling windows share {str(e)}")



        elif event == "create_windows_share":
            # Check if the event is the "create_windows_share" event

            try:
                # Get the values from the PySimpleGUI window
                new_equivalence=os.path.dirname(os.path.realpath(image_path_arg))

                username = values['share_login']
                password = values['share_password']
                sharename = str(values['folder_share_server']).replace(" ", "")
                values['folder_share_server'] = sharename
                folderpath = new_equivalence

                # Call the create_login_and_share function with the entered values
                create_login_and_share(username, password, sharename, folderpath)

            except Exception as e:
                # If an exception occurs during the execution of the code block, display an error popup

                sg.popup_error(f"Error creating windows share {str(e)}")


if __name__ == '__main__':
    ForensicVMForm()
