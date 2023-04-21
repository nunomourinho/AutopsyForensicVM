import os
import re
import json
import sys
import uuid
import paramiko
import PySimpleGUI as sg
import webbrowser
import subprocess
import threading
import time


# Define the filename for the JSON file
filename = "config.json"
icon_path = "forensicVMCLient.ico"

#sg.popup(sys.argv)
image_path_arg = sys.argv[1] if len(sys.argv) > 1 else ""
case_directory_arg = sys.argv[2] if len(sys.argv) > 2 else ""
case_name_arg = sys.argv[3] if len(sys.argv) > 3 else ""
case_number_arg = sys.argv[4] if len(sys.argv) > 4 else ""
case_examiner_arg = sys.argv[5] if len(sys.argv) > 5 else ""



def string_to_uuid(input_string):
    # Use a namespace for your application (theoretical site)
    namespace = uuid.uuid5(uuid.NAMESPACE_DNS, 'forensic.vm.mesi.ninja')

    # Generate a UUID based on the namespace and the input string
    unique_uuid = uuid.uuid5(namespace, input_string)

    return unique_uuid


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

        ssh_command ="start /wait cmd /k \"set SSH_TERM_CONHOST_PARSER=0 & set TERM=xterm & ssh -i mykey -o \"SendEnv TERM\" -oStrictHostKeyChecking=no forensicinvestigator@" \
                     + str(server_address)\
                     + " -p " + str(server_port)\
                     + " " + reverse_ssh_foward + " " + command + "\""

        print(ssh_command)
        # Run the command redirecting local samba port to a free open port remote\ly
        os.system(ssh_command)
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



# Save the values as a json file
def save_config(values):
    # Save the configuration to the JSON file
    with open(filename, "w") as f:
        json.dump(values, f)

# Load json file as values
def load_config():
    # Load the configuration from the JSON file if it exists
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return {}

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
    config = load_config()

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
                   sg.Button("Test Ssh connection", key="test_ssh_connect")
                   ],
                  ]
                  )],

        [sg.Frame("Forensic Image source and windows share",
                  [

                      [sg.Text("Windows folder share server:"), sg.InputText(key="folder_share_server",
                                                               default_text=config.get("folder_share_server", ""))],
        [sg.Text("Share login:"), sg.InputText(key="share_login", default_text=config.get("share_login", ""))],
        [sg.Text("Share password:"), sg.InputText(key="share_password", password_char="*", default_text=config.get("share_password", ""))],
        [sg.Text("Local ou remote path to share:"),sg.InputText(key="equivalence", default_text=config.get("equivalence", "")),
         sg.Button("Test windows share", key="test_windows_share")],

                  ]
                  )],

        [sg.Button("Test Connection", key="connect_button"), sg.Button("Save", key="save_button")],
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
    ], [sg.Frame("Generated UUID",   [[sg.Text("Unique Path and Case UUID"), sg.Text(string_to_uuid(image_path_arg+case_name_arg))]])]
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

    # define a janela para exibir a saída
    layout2 = [[sg.Multiline(size=(80, 20), key='-OUTPUT-', font='Courier 10', background_color='black', text_color='white')]]

    window2 = sg.Window('Migration output', layout2)



    # Event loop
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "connect_button":
            server_address = values["server_address"]
            forensic_api = values["forensic_api"]
            folder_share_server = values["folder_share_server"]
            share_login = values["share_login"]
            share_password = values["share_password"]
            forensic_image_path = values["forensic_image_path"]
            equivalence = values["equivalence"]
            if not validate_server_address(server_address):
                window["server_address"].SetFocus()
                sg.popup_error("Please enter a valid server address")
                # Validate the server port
            else:
                save_config(values)
                # Your connection code goes here
                print("Connecting to Forensic VM...")
                print("Connected successfully!")
                window["output_text"].update("Connecting to Forensic VM...\nConnected successfully!")
        elif event == "save_button":
            # Save the configuration to the JSON file
            save_config(values)
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

            window["convert_to_vm_button"].update(visible=False)
            window["link_to_vm_button"].update(visible=False)
            window["import_data_button"].update(visible=True)
            window["open_forensic_vm_button"].update(visible=True)
            window["open_forensic_shell_button"].update(visible=True)
            window["open_forensic_netdata_button"].update(visible=True)

        elif event == "open_forensic_vm_button":
            # get server address value
            print("Open ForensicVM Webserver...")
            server_address = "http://" + values["server_address"]
            webbrowser.open(server_address)
        elif event == "open_forensic_shell_button":
            # get server address value
            print("Open ForensicVM Webserver...")
            server_address = "http://" + values["server_address"] + "/shell"
            webbrowser.open(server_address)
        elif event == "open_forensic_netdata_button":
            # get server address value
            print("Open ForensicVM Webserver...")
            server_address = "http://" + values["server_address"] + "/netdata"
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





if __name__ == '__main__':
    ForensicVMForm()
