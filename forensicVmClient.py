
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

    cmd = '"{}\\nircmdc" elevate cmd /c {} "{}" "{}" "{}" "{}"'.format(os.getcwd(),batch_file, username,
                                                                    password, share_name,
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
    if len(sys.argv) >= 4:
        image_path_arg = sys.argv[1]
        case_directory_arg = sys.argv[2]
        case_name_arg = sys.argv[3]
        case_number_arg = sys.argv[4] if len(sys.argv) > 4 else "-"
        case_examiner_arg = sys.argv[5] if len(sys.argv) > 4 else "-"
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

        ssh_key.write_private_key_file(private_key_path)

        # Save public key to disk
        ###public_key_path = f"{private_key_path}.pub"
        ###with open(public_key_path, "w") as public_key_file:
        ###public_key_file.write(f"{ssh_key.get_name()} {ssh_key.get_base64()}")

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


# Form: All fields in the form

def ForensicVMForm():
    # Set the theme
    sg.theme("DefaultNoMoreNagging")

    # Load the configuration from the JSON file if it exists
    config = load_config(filename)
    image_config = load_config(case_image_folder + "\\image-share.json")


    # Define the layout of the virtualize tab
    virtualize_layout = [
        #[sg.Button("Configure", key="configure_button", size=(25, 1))],
        [sg.Button("Virtualize - a) Convert to VM",
                   tooltip="Connect to Forensic VM Server and "
                                         "virtualize the forensic Image", key="convert_to_vm_button", size=(25, 2),
                   visible=True)],
        [sg.Button("Virtualize - b) Link to VM",
                   tooltip="Connect to Forensic VM Server and "
                                         "virtualize the forensic Image", key="link_to_vm_button", size=(25, 2), visible=True)],
        [sg.Button("Start VM", key="start_vm_button", size=(25, 2), visible=False)],
        [sg.Button("Reset VM", key="reset_vm_button", size=(25, 2), visible=False)],
        [sg.Button("Stop VM", key="stop_vm_button", size=(25, 2), visible=False)],
        [sg.Button("Open ForensicVM", key="open_forensic_vm_button", size=(25, 2), visible=False)],
        [sg.Button("Open ForensicVM WebShell", key="open_forensic_shell_button", size=(25, 1), visible=False)],
        [sg.Button("Analyse ForensicVM performance", key="open_forensic_netdata_button", size=(25, 1), visible=False)],
        [sg.Button("Import Data", key="import_data_button", size=(25, 1), visible=False)]
    ]
    virtualize_tab = sg.Tab("Virtualize", virtualize_layout, element_justification="center")

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


    # Layout for the configuration tab
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
                                       sg.Text(string_to_uuid(image_path_arg+case_name_arg))]])]
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

    # Create the layout for the window
    layout = [
        [sg.TabGroup([
            [sg.TabGroup([[virtualize_tab, autopsy_tab, config_tab, about_tab]])],
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
            if check_vm_exists(forensic_api, uuid_folder, web_server_address):
                window["convert_to_vm_button"].update(visible=False)
                window["link_to_vm_button"].update(visible=False)
                window["open_forensic_shell_button"].update(visible=True)
                window["open_forensic_netdata_button"].update(visible=True)
                return_code, vm_status = get_forensic_image_info(forensic_api, uuid_folder, web_server_address)
                if vm_status.get("vm_status", "") == "running":
                    window["start_vm_button"].update(visible=False)
                    window["stop_vm_button"].update(visible=True)
                    window["reset_vm_button"].update(visible=True)
                    window["import_data_button"].update(visible=False)
                    window["open_forensic_vm_button"].update(visible=True)
                elif vm_status.get("vm_status", "") == "stopped":
                    window["start_vm_button"].update(visible=True)
                    window["stop_vm_button"].update(visible=False)
                    window["reset_vm_button"].update(visible=False)
                    window["import_data_button"].update(visible=True)
            else:
                window["convert_to_vm_button"].update(visible=True)
                window["link_to_vm_button"].update(visible=True)
                window["open_forensic_shell_button"].update(visible=False)
                window["open_forensic_netdata_button"].update(visible=False)

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "start_vm_button":
            forensic_image_path = values["forensic_image_path"]
            uuid_folder = string_to_uuid(forensic_image_path + case_name_arg)
            web_server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            start_vm(forensic_api, uuid_folder, web_server_address)
        elif event == "save_button":
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
            window["convert_to_vm_button"].update(visible=False)
            window["link_to_vm_button"].update(visible=False)
            window["import_data_button"].update(visible=True)
            window["open_forensic_vm_button"].update(visible=True)
            window["stop_vm_button"].update(visible=True)
            window["reset_vm_button"].update(visible=True)
            window["open_forensic_shell_button"].update(visible=True)
            window["open_forensic_netdata_button"].update(visible=True)

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

                    window["convert_to_vm_button"].update(visible=False)
                    window["link_to_vm_button"].update(visible=False)
                    window["import_data_button"].update(visible=True)
                    window["stop_vm_button"].update(visible=True)
                    window["reset_vm_button"].update(visible=True)
                    window["open_forensic_vm_button"].update(visible=True)
                    window["open_forensic_shell_button"].update(visible=True)
                    window["open_forensic_netdata_button"].update(visible=True)
            else:
                print(vm_status)
                if vm_status.get("vm_status", "") == "running":
                    sg.popup("The machine is running.\n No actions required")
                    window["convert_to_vm_button"].update(visible=False)
                    window["link_to_vm_button"].update(visible=False)
                    window["import_data_button"].update(visible=True)
                    window["stop_vm_button"].update(visible=True)
                    window["reset_vm_button"].update(visible=True)
                    window["open_forensic_vm_button"].update(visible=True)
                    window["open_forensic_shell_button"].update(visible=True)
                    window["open_forensic_netdata_button"].update(visible=True)
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
            webbrowser.open(server_address)
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
                sharename = values['folder_share_server']
                folderpath = new_equivalence

                # Call the create_login_and_share function with the entered values
                create_login_and_share(username, password, sharename, folderpath)
            except Exception as e:
                sg.popup_error(e)


if __name__ == '__main__':
    ForensicVMForm()
