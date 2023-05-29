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
from requests_toolbelt import MultipartEncoder
from urllib.parse import urljoin


def change_memory_size(api_key, site_url, uuid, memory_size):
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


# def upload_iso(api_key, base_url, iso_file_path, window):
#     assert api_key, "API key is required"
#     assert base_url, "Base URL is required"
#     assert iso_file_path, "ISO file path is required"
#
#     url = f"{base_url}/api/upload-iso/"
#     headers = {
#         'X-Api-Key': api_key,
#     }
#
#     file_size = os.path.getsize(iso_file_path)
#     progress_bar = sg.one_line_progress_meter('Uploading ISO file', 0, file_size, '-PROGRESS-')
#
#     def perform_upload():
#         try:
#             multipart_data = MultipartEncoder(fields={'iso_file': (os.path.basename(iso_file_path), open(iso_file_path, 'rb'))})
#             headers['Content-Type'] = multipart_data.content_type
#             response = requests.post(url, headers=headers, data=multipart_data, stream=True)
#             response.raise_for_status()
#             total_uploaded = 0
#
#             for chunk in response.iter_content(chunk_size=1024):
#                 if chunk:
#                     total_uploaded += len(chunk)
#                     progress_bar.UpdateBar(total_uploaded)
#
#             sg.one_line_progress_meter('Uploading ISO file', file_size, file_size, '-PROGRESS-', 'Upload complete')
#             sg.popup('Upload complete!')
#
#         except requests.exceptions.RequestException as e:
#             sg.popup_error('Error:', e)
#
#     # Start the upload in a separate thread
#     upload_thread = threading.Thread(target=perform_upload)
#     upload_thread.start()
#
#     # Wait for the upload_thread to finish
#     while upload_thread.is_alive():
#         event, _ = window.read(timeout=100)
#         if event == sg.WINDOW_CLOSED:
#             break


def run_plugin(api_key, base_url, plugin_directory, image_uuid):
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
    assert isinstance(s, str), 'Expecting a string!'
    return re.sub('[^0-9a-zA-Z]+', '_', s)


def read_case_config(json_filepath):
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
            sg.popup(f"Evidence downloaded to {output_file}")
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
    url = f"{baseurl}/api/check-vm-exists/{uuid}/"
    headers = {"X-API-KEY": api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        result = response.json()
        vm_exists = result['vm_exists']
        return vm_exists
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False
def start_vm(api_key, uuid, baseurl):
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
    url = f'{baseurl}/api/forensic-image-vm-status/{uuid}/'

    headers = {'X-API-KEY': api_key}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return 0, response.json()
        else:
            return response.status_code, "Access denied"
    except Exception as e:
        return 1, str(e)


def test_api_key(api_key, baseurl):
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
    # Use a namespace for your application (theoretical site)
    namespace = uuid.uuid5(uuid.NAMESPACE_DNS, 'forensic.vm.mesi.ninja')

    # Generate a UUID based on the namespace and the input string
    unique_uuid = uuid.uuid5(namespace, input_string)

    return unique_uuid


# Save the values as a json file
def save_config(values, filename):
    # Save the configuration to the JSON file
    with open(filename, "w") as f:
        json.dump(values, f)

# Load json file as values
def load_config(filename):
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


def run_openssh(server_address, server_port, windows_share,
            share_login, share_password, replacement_share,
            forensic_image_path, uuid_folder, copy):
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


def debug_remotessh(server_address, server_port, uuid_folder):
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
    # Use the 'net use' command to map a drive to the share
    cmd = 'net use {} /user:{} {}'.format(server_address, username, password)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        return False

    # Disconnect the mapped drive
    cmd = 'net use {} /delete'.format(server_address)
    subprocess.check_output(cmd, shell=True)

    return True





def validate_server_address(address):
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
    iso_file_path = values['-BROWSE-']
    window['-CDROM FILE-'].update(value=iso_file_path)
    window['-UPLOAD-'].update(disabled=False)


def list_snapshots(forensic_api, uuid_folder, web_server_address):
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


def formInit(values, window):
    forensic_image_path = values["forensic_image_path"]
    uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
    web_server_address = values["server_address"]
    forensic_api = values["forensic_api"]
    server_ok, _ = test_api_key(forensic_api, web_server_address)

    if server_ok==0:
        memory = get_memory_size(forensic_api, web_server_address, uuid_folder) / 1024
        if memory:
            print("Forensic VM Server is running on " + str(memory) + " MB")
            window['-MB-SLIDER-'].update(memory)

        # Update snapshot list
        snapshot_info_list = list_snapshots(forensic_api, uuid_folder, web_server_address)
        window['-SNAPSHOT-LIST-'].update(snapshot_info_list)

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


# Form: All fields in the form

def ForensicVMForm():
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

    # Create the frames
    convert_frame = sg.Frame("Convert forensic Image to VM", [
        [sg.Button("Virtualize - a) Convert to VM",
                   tooltip="Connect to Forensic VM Server and virtualize the forensic Image",
                   key="convert_to_vm_button", size=(25, 2), visible=True, disabled=False)],
        [sg.Button("Virtualize - b) Link to VM",
                   tooltip="Connect to Forensic VM Server and virtualize the forensic Image",
                   key="link_to_vm_button", size=(25, 2), visible=True, disabled=False)]
    ])

    screenshot_frame = sg.Frame("Screenshot", [
        [sg.Button("Screenshot", key="screenshot_vm_button", size=(25, 2), visible=True, disabled=True)],
        [sg.Button("Save screenshots", key="save_screenshots_vm_button", size=(25, 2), visible=True, disabled=True)]
    ])

    memory_frame = sg.Frame("Make and download memory dump", [
        [sg.Button("Make and download memory dump", key="download_memory_button", size=(25, 2), visible=True,
                   disabled=True)]
    ])

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
        [sg.Button("Insert network card", key="insert_network_button", size=(25, 1), visible=True,
                   disabled=True)],
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

    list_plugins_frame = sg.Frame('List', [
        [sg.Button('List Remote Plugins', key='-LIST PLUGINS-', disabled=False)]
    ])

    run_plugin_frame = sg.Frame('Run', [
        [sg.Button('Run Selected Plugin', key='-RUN PLUGIN-', disabled=False)]
    ])

    plugins_frame = sg.Frame('Plugin Management', [
        [sg.Listbox([], size=(61, 21), key='-PLUGIN LIST-', enable_events=True)],
        [list_plugins_frame, run_plugin_frame],
    ])

    snapshots_frame = sg.Frame('Snapshot management', [
        [sg.Button('List Remote Snapshots', key='-LIST SNAPSHOTS-', disabled=False),
        sg.Button('Create new', key='-CREATE SNAPSHOT-', disabled=False),
        sg.Button('Rollback', key='-ROLLBACK SNAPSHOT-', disabled=False)],
    ])


    delete_snapshot_frame = sg.Frame('Danger Zone!', [
        [sg.Button('Delete ???', key='-DELETE SNAPSHOT-', disabled=False)]
    ])

    snapshot_frame = sg.Frame('Snapshot Management', [
        [sg.Listbox([], size=(61, 21), key='-SNAPSHOT-LIST-', enable_events=True)],
        [snapshots_frame, delete_snapshot_frame],
    ])

    finetune_frame = sg.Frame('Memory Size (GB)', [
        [sg.Slider(range=(0, 128), default_value=0.128, orientation='h',
                   size=(40, 20),  resolution=0.1, key='-MB-SLIDER-'),
         sg.Button('CHANGE', size=(10, 2), key='-CHANGE-MB-')],

    ])

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
                [finetune_frame]
            ]),
        ]
    ])

    # Define the layout of the virtualize tab
    virtualize_layout = [
        [sg.Column([[convert_frame], [vm_control_frame]],
                   element_justification='left',
                   vertical_alignment='top'),
        sg.Column([[tab_group]],
                   element_justification='left',
                   vertical_alignment='top'),
        sg.Column([[screenshot_frame], [memory_frame], [tools_frame]],
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
                   sg.Button("Test Server Connection", key="test_forensicServer_connect")
                   ]
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
                   sg.Button("Test Ssh connection", key="test_ssh_connect"),
                   sg.Button("Copy ssh key to server", key="copy-ssh-key-to-server")
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
         sg.Button("Test windows share", key="test_windows_share"),
         sg.Button("Autofill info", key="autofill_share"),
         sg.Button("Create share", key="create_windows_share")],

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
    about_tab = sg.Tab("About", about_layout, element_justification="center")

    output_layout = [
        [sg.Output(size=(100, 25), key="-OUTPUT-",
                   background_color='black',
                   text_color='white',
                   font=('Courier New', 12))]
    ]

    output_tab = sg.Tab("Output Console", output_layout, element_justification="left")

    # Create the layout for the window
    layout = [
        [sg.TabGroup([
            #[sg.TabGroup([[virtualize_tab, autopsy_tab, config_tab, about_tab]])],
            [sg.TabGroup([[virtualize_tab, autopsy_tab, config_tab, output_tab, about_tab]])],
        ])]
    ]


    # Create the window

    window = sg.Window("Autopsy ForensicVM Client", layout, element_justification="center", icon=icon_path)



    # Event loop
    while True:
        event, values = window.read(timeout=1000)
        if event == sg.TIMEOUT_EVENT:

            # Test if the vm exists
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            server_ok = 1
            if not server_offline:
                server_ok, _ = test_api_key(forensic_api, web_server_address)
                if server_ok != 0:
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
                if first_run:
                    formInit(values, window)
                    first_run = False
                window["alert_server_off"].update(visible=False)
                if check_vm_exists(forensic_api, uuid_folder, web_server_address):
                    window["convert_to_vm_button"].update(disabled=not False)
                    window["link_to_vm_button"].update(disabled=not False)
                    window["delete_vm_button"].update(disabled=False)
                    window["open_forensic_vm_button"].update(disabled=not False)
                    window["open_forensic_shell_button"].update(disabled=not True)
                    window["open_forensic_netdata_button"].update(disabled=not True)
                    window["save_screenshots_vm_button"].update(disabled=not True)
                    return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
                    if vm_status.get("vm_status", "") == "running":
                        window["delete_vm_button"].update(disabled=True)
                        window["start_vm_button"].update(disabled=not False)
                        window["screenshot_vm_button"].update(disabled=not True)
                        window["insert_network_button"].update(disabled=False)
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
                    elif vm_status.get("vm_status", "") == "stopped":
                        window["delete_vm_button"].update(disabled=False, visible=True)
                        window["start_vm_button"].update(disabled=not True)
                        window["screenshot_vm_button"].update(disabled=not False)
                        window["download_memory_button"].update(disabled=not False)
                        window["insert_network_button"].update(disabled=True)
                        window["shutdown_vm_button"].update(disabled=not False)
                        window["stop_vm_button"].update(disabled=not False)
                        window["reset_vm_button"].update(disabled=not False)
                        window["import_evidence_button"].update(disabled=not True)
                        window["recreate_evidence_disk_button"].update(disabled=False)
                        window["save_screenshots_vm_button"].update(disabled=not True)
                        window["-RUN PLUGIN-"].update(disabled=False)
                        vm_stopped = True
                        if not folders_created:
                            forensic_image_path = values["forensic_image_path"]
                            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                            web_server_address = values["server_address"]
                            forensic_api = values["forensic_api"]
                            create_folders_in_qcow2_background(forensic_api, web_server_address, uuid_folder, case_tags)
                            folders_created = True
            elif not server_offline:
                window["convert_to_vm_button"].update(disabled=not True)
                window["link_to_vm_button"].update(disabled=not True)
                window["delete_vm_button"].update(disabled=not False)
                window["download_memory_button"].update(disabled=not False)
                window["save_screenshots_vm_button"].update(disabled=not True)
                window["open_forensic_shell_button"].update(disabled=not False)
                window["open_forensic_netdata_button"].update(disabled=not False)


        if event == sg.WINDOW_CLOSED:
            break
        elif event == '-CHANGE-MB-':
            try:
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                web_server_address = values["server_address"]
                forensic_api = values["forensic_api"]
                change_memory_size(forensic_api, web_server_address, uuid_folder, values["-MB-SLIDER-"] * 1024)
                sg.popup(f"Memory size changed to {values['-MB-SLIDER-']} MB")
            except Exception as e:
                print(str(e))
        elif event == '-DELETE SNAPSHOT-':
            try:
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                web_server_address = values["server_address"]
                forensic_api = values["forensic_api"]
                selected_files = values['-SNAPSHOT-LIST-']
                if selected_files:
                    snap_filename = selected_files[0]
                    # Find out the snapshot name from inside the file name
                    match = re.search(r'\((.*?)\)', snap_filename)
                    if match:
                        snapshot_name =match.group(1)
                        if sg.PopupYesNo("Are you sure you want to delete the snapshot " +
                                         snapshot_name + "?", title="") == "Yes":
                            delete_snapshot(forensic_api, web_server_address, uuid_folder, snapshot_name)
                            snapshot_info_list = list_snapshots(forensic_api, uuid_folder, web_server_address)
                            window['-SNAPSHOT-LIST-'].update(snapshot_info_list)
                            sg.popup(f"Deleted snapshot {snapshot_name}")

            except Exception as e:
                print(str(e))
        elif event == '-ROLLBACK SNAPSHOT-':
            try:
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                web_server_address = values["server_address"]
                forensic_api = values["forensic_api"]
                selected_files = values['-SNAPSHOT-LIST-']
                if selected_files:
                    snap_filename = selected_files[0]
                    # Find out the snapshot name from inside the file name
                    match = re.search(r'\((.*?)\)', snap_filename)
                    if match:
                        snapshot_name =match.group(1)
                        rollback_snapshot(forensic_api, web_server_address, uuid_folder, snapshot_name)
                        snapshot_info_list = list_snapshots(forensic_api, uuid_folder, web_server_address)
                        window['-SNAPSHOT-LIST-'].update(snapshot_info_list)
                        sg.popup(f"Reverted to snapshot {snapshot_name}")

            except Exception as e:
                print(str(e))
        elif event == '-CREATE SNAPSHOT-':
            try:
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                web_server_address = values["server_address"]
                forensic_api = values["forensic_api"]
                create_snapshot(forensic_api, uuid_folder, web_server_address)
                snapshot_info_list = list_snapshots(forensic_api, uuid_folder, web_server_address)
                window['-SNAPSHOT-LIST-'].update(snapshot_info_list)
                sg.popup(f"Snapshot created")
            except Exception as e:
                print(str(e))
        elif event == '-LIST SNAPSHOTS-':
            forensic_api = values["forensic_api"]
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            snapshot_info_list=list_snapshots(forensic_api, uuid_folder, web_server_address)
            window['-SNAPSHOT-LIST-'].update(snapshot_info_list)





        elif event == 'debug_ssh_button':
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            server_address = values["ssh_server_address"]
            server_port = values["ssh_server_port"]
            debug_remotessh(server_address, server_port,uuid_folder )
        elif event == 'recreate_evidence_disk_button':
            response = sg.PopupYesNo('Do you want delete the evidence disk?', title='Confirmation')
            if response == 'Yes':
                response_2 = sg.PopupYesNo('ARE YOU REALLY SURE?', title='Confirmation')
                if response_2 == 'Yes':
                    forensic_image_path = values["forensic_image_path"]
                    uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                    web_server_address = values["server_address"]
                    forensic_api = values["forensic_api"]
                    recreate_folders(forensic_api, web_server_address, uuid_folder, case_tags)
                    folders_created = True
                    print('Evidence Drive recreated')
                    sg.popup("Evidence Drive recreated")
            else:
                print('User clicked No')
        elif event == '-EJECT-':
            try:
                api_key = values["forensic_api"]
                base_url = values["server_address"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                response = eject_cdrom(api_key, base_url, uuid_folder)
                if response:
                    print(response)
                else:
                    print("Failed to eject CD-ROM")
            except Exception as e:
                 print(str(e))
        elif event == 'insert_network_button':
            try:
                api_key = values["forensic_api"]
                base_url = values["server_address"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                response = insert_network_card(api_key, uuid_folder, base_url)
                if response:
                    print(response)
                else:
                    print("Failed to insert network card")
            except Exception as e:
                 print(str(e))
        elif event == '-INSERT-':
            try:
                api_key = values["forensic_api"]
                base_url = values["server_address"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                selected_files = values['-CDROM LIST-']
                if selected_files:
                    iso_filename = selected_files[0]
                    response = insert_cdrom(api_key, base_url, uuid_folder, iso_filename)
                    if response:
                        print(response)
                    else:
                        print("Failed to insert CD-ROM")
            except Exception as e:
                 print(str(e))
        elif event == '-RUN PLUGIN-':
            try:
                api_key = values["forensic_api"]
                base_url = values["server_address"]
                forensic_image_path = values["forensic_image_path"]
                uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
                selected_files = values['-PLUGIN LIST-']
                if selected_files:
                    pattern = r'\((.*?)\)'
                    matches = re.findall(pattern, selected_files[0])

                    # Check if any matches found
                    if matches:
                        plugin_dir = matches[0]
                        response = run_plugin(api_key, base_url, plugin_dir, uuid_folder)
                        if response:
                            print(response)
                        else:
                            print("Failed to run plugin")
                        print(plugin_dir)

            except Exception as e:
                 print(str(e))
        elif event == '-DELETE-':
            # Get the selected ISO file from the Listbox
            try:
                selected_files = values['-CDROM LIST-']
                print(selected_files)
                if selected_files:
                    iso_filename = selected_files[0]
                    # Call the delete_iso function
                    api_key = values["forensic_api"]
                    base_url = values["server_address"]
                    deleted = delete_iso(api_key, base_url, iso_filename)
                    if deleted:
                        web_server_address = values["server_address"]
                        forensic_api = values["forensic_api"]
                        try:
                            iso_files = list_iso_files(forensic_api, web_server_address)
                            if iso_files:
                                print(iso_files)
                                window['-CDROM LIST-'].update(iso_files['iso_files'])
                        except Exception as e:
                            print(str(e))
            except Exception as e:
                print(str(e))
        elif event == '-BROWSE-':
            try:
                save_path = sg.popup_get_file('Choose iso file',
                                              save_as=False,
                                              no_window=True,
                                              default_extension=".iso",
                                              file_types=(("Iso Files", "*.iso"),))
                if save_path:
                    api_key = values["forensic_api"]
                    base_url = values["server_address"]
                    result = upload_iso(api_key, base_url, save_path)
                    if result:
                        sg.popup('Upload successful')
                        web_server_address = values["server_address"]
                        forensic_api = values["forensic_api"]
                        try:
                            iso_files = list_iso_files(forensic_api, web_server_address)
                            if iso_files:
                                print(iso_files)
                                window['-CDROM LIST-'].update(iso_files['iso_files'])
                        except Exception as e:
                            print(str(e))
                    else:
                        sg.popup_error('Upload failed')
            except Exception as e:
                print(str(e))
        elif event == '-LIST-':
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            try:
                iso_files = list_iso_files(forensic_api, web_server_address)
                if iso_files:
                    print(iso_files)
                    window['-CDROM LIST-'].update(iso_files['iso_files'])
            except Exception as e:
                print(str(e))
        elif event == '-LIST PLUGINS-':

            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
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
        elif event == "save_screenshots_vm_button":
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
            if save_path:
                download_screenshots(forensic_api, uuid_folder, web_server_address, save_path)
        elif event == "import_evidence_button":
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
            if save_path:
                download_evidence(forensic_api, uuid_folder, web_server_address, save_path)
        elif event == "download_memory_button":
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
            if save_path:
                download_memory_dump(forensic_api, uuid_folder, web_server_address, save_path)
        elif event == "screenshot_vm_button":
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
            if vm_status.get("vm_status", "") == "running":
                screenshot_vm(forensic_api, uuid_folder, web_server_address)
        elif event == "reset_vm_button":
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
            if vm_status.get("vm_status", "") == "running":
                reset_vm(forensic_api, uuid_folder, web_server_address)
        elif event == "shutdown_vm_button":
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
            if vm_status.get("vm_status", "") == "running":
                shutdown_vm(forensic_api, uuid_folder, web_server_address)
        elif event == "delete_vm_button":
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
            if vm_status.get("vm_status", "") == "stopped":
                delete_vm(forensic_api, uuid_folder, web_server_address)
        elif event == "start_vm_button":
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            start_vm(forensic_api, uuid_folder, web_server_address)
        elif event == "save_button":
            try:
                # Save the configuration to the JSON file
                save_config(values, filename)

                image_values = {
                    "folder_share_server": values["folder_share_server"],
                    "share_login": values["share_login"],
                    "share_password": values["share_password"],
                    "equivalence": values["equivalence"]
                }
                save_config(image_values, case_image_folder + "\\image-share.json")
                print("Configuration saved successfully!")
                sg.popup("Configuration saved successfully!")
            except Exception as e:
                print(str(e))
                sg.popup_error(str(e))
        elif event == "convert_to_vm_button":

            print("Copy and convert...")

            server_address = values["ssh_server_address"]
            server_port = values["ssh_server_port"]
            windows_share = values["folder_share_server"]
            share_login = values["share_login"]
            share_password = values["share_password"]
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            copy = "copy"
            replacement_share = values["equivalence"]

            # Run the remote openssh command
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
            window["convert_to_vm_button"].update(disabled=not False)
            window["link_to_vm_button"].update(disabled=not False)
            window["import_evidence_button"].update(disabled=not True)
            window["open_forensic_vm_button"].update(disabled=not True)
            window["stop_vm_button"].update(disabled=not True)
            window["reset_vm_button"].update(disabled=not True)
            window["open_forensic_shell_button"].update(disabled=not True)
            window["open_forensic_netdata_button"].update(disabled=not True)

        elif event == "link_to_vm_button":

            print("Link...")

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

            if return_code != 0:
                if return_code!= 404:
                    sg.popup_error("Could not connect to the server:\n" + vm_status)
                else:
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

                    window["convert_to_vm_button"].update(disabled=not False)
                    window["link_to_vm_button"].update(disabled=not False)
                    window["import_evidence_button"].update(disabled=not True)
                    window["stop_vm_button"].update(disabled=not True)
                    window["reset_vm_button"].update(disabled=not True)
                    window["open_forensic_vm_button"].update(disabled=not True)
                    window["open_forensic_shell_button"].update(disabled=not True)
                    window["open_forensic_netdata_button"].update(disabled=not True)
            else:
                print(vm_status)
                if vm_status.get("vm_status", "") == "running":
                    sg.popup("The machine is running.\n No actions required")
                    window["convert_to_vm_button"].update(disabled=not False)
                    window["link_to_vm_button"].update(disabled=not False)
                    window["import_evidence_button"].update(disabled=not True)
                    window["stop_vm_button"].update(disabled=not True)
                    window["reset_vm_button"].update(disabled=not True)
                    window["open_forensic_vm_button"].update(disabled=not True)
                    window["open_forensic_shell_button"].update(disabled=not True)
                    window["open_forensic_netdata_button"].update(disabled=not True)
                elif vm_status.get("vm_status", "") == "stopped":
                    sg.popup("The vm exists and is stopped.\n Starting the VM in the remote server.\n")
                    # TODO: Start the VM in the remote_port
                    remote_port = ssh_background_session(server_address, server_port, windows_share)
                    if start_vm(forensic_api, uuid_folder, web_server_address) == "running":
                        sg.popup("The machine is running.\n No actions required")
                    else:
                        sg.popup_error("Could not start the VM:\n")
                else:
                    continue





        elif event == "open_forensic_vm_button":
            # get server address value
            print("Open ForensicVM Webserver...")
            server_address = values["server_address"]
            return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
            print(vm_status)
            if return_code== 0:
                webbrowser.open(f"{server_address}?port={vm_status['websocket_port']}&uuid={uuid_folder}")
        elif event == "stop_vm_button":
            # get server address value
            print("Stop VM...")
            forensic_api = values["forensic_api"]
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]

            stop_result = stop_vm(forensic_api, uuid_folder, web_server_address)
            if stop_result:
                print(f"VM stopped: {stop_result['vm_stopped']}")


        elif event == "open_forensic_shell_button":
            # get server address value
            print("Open ForensicVM Webserver...")
            server_address = values["server_address"] + "/shell"
            webbrowser.open(server_address)
        elif event == "open_forensic_netdata_button":
            # get server address value
            print("Open ForensicVM Webserver...")
            server_address = values["server_address"] + "/netdata"
            webbrowser.open(server_address)
        elif event == "test_ssh_connect":
            # get server address value
            if test_ssh(values['ssh_server_address'], values['ssh_server_port']):
                sg.popup("Connected successfully!")
            else:
                sg.popup_error("Could not connect to the server")
        elif event == "test_windows_share":
            # get server address value
            if test_windows_share(values['folder_share_server'], values['share_login'], values['share_password']):
                sg.popup("Connected successfully!")
            else:
                sg.popup_error("Could not connect to the server")
        elif event == "test_forensicServer_connect":
            server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            return_code, message= test_api_key(forensic_api, server_address)
            if return_code != 0:
                sg.popup_error("Could not connect to the server:\n" +  message)
            else:
                sg.popup("Connected successfully!\n" + message)
                server_offline = False
        elif event == "copy-ssh-key-to-server":
            ssh_dir = os.path.dirname(os.path.abspath(__file__))
            message, status_code = generate_and_send_public_key(values["server_address"], values["forensic_api"],
                                                                ssh_dir)
            if status_code!= 200:
                sg.popup_error(message)
            else:
                sg.popup(message)
        elif event == "autofill_share":
            # Get the values from the PySimpleGUI window
            new_equivalence = os.path.dirname(os.path.realpath(image_path_arg))
            window.Element('equivalence').update(value=new_equivalence)
            new_share_folder = "\\\\127.0.0.1\\" + os.path.basename(new_equivalence)
            window.Element('folder_share_server').update(value=new_share_folder)
        elif event == "create_windows_share":
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
                sg.popup_error(e)


if __name__ == '__main__':
    ForensicVMForm()
