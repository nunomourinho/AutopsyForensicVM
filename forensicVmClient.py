import os
import re
import json
import sys
import paramiko
import PySimpleGUI as sg

# Define the filename for the JSON file
filename = "config.json"
icon_path = "forensicVMCLient.ico"

# Get the first command line argument, if any
image_path_arg = sys.argv[1] if len(sys.argv) > 1 else ""



def connect_to_server(address, port):
    # Connect to the server
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(address, port, username="forensic", password="forensic")

    # Get an available remote port
    transport = ssh.get_transport()
    remote_port = transport.request_port_forward("", 0)

    # Open a new TCP channel and forward traffic from the remote port to the local port
    channel = transport.open_channel("direct-tcpip", ("localhost", 445), ("localhost", remote_port))

    # Close the connection
    ssh.close()

    # Return the remote port number
    return remote_port




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
        [sg.Button("Configure", key="configure_button", size=(25, 1))],
        [sg.Button("Virtualize - a) Convert to VM",
                   tooltip="Connect to Forensic VM Server and "
                                         "virtualize the forensic Image", key="convert_to_vm_button", size=(25, 2), visible=True)],
        [sg.Button("Virtualize - b) Link to VM",
                   tooltip="Connect to Forensic VM Server and "
                                         "virtualize the forensic Image", key="link_to_vm_button", size=(25, 2), visible=True)],
        [sg.Button("Open ForensicVM", key="open_forensic_vm_button", size=(25, 1), visible=False)],
        [sg.Button("Import Data", key="import_data_button", size=(25, 1), visible=False)]
    ]
    virtualize_tab = sg.Tab("Virtualize", virtualize_layout, element_justification="center")

    # Create the layout for the configuration tab
    config_layout = [
        [sg.Text("Forensic VM server address:"), sg.InputText(key="server_address", default_text=config.get("server_address", ""))],
        [sg.Text("Forensic API:"), sg.InputText(key="forensic_api", default_text=config.get("forensic_api", ""))],
        [sg.Text("SSH Server Address and port:"),
         sg.InputText(key="ssh_server_address", default_text=config.get("ssh_server_address", ""))],
        [sg.Text("SSH user Public Key:"),
         sg.InputText(key="ssh_public_key", default_text=config.get("ssh_user_key", ""))],
        [sg.Text("Windows folder share server:"), sg.InputText(key="folder_share_server", default_text=config.get("folder_share_server", ""))],
        [sg.Text("Share login:"), sg.InputText(key="share_login", default_text=config.get("share_login", ""))],
        [sg.Text("Share password:"), sg.InputText(key="share_password", password_char="*", default_text=config.get("share_password", ""))],
        [sg.Text("Forensic image local path:"), sg.InputText(key="forensic_image_path", default_text=config.get("forensic_image_path", ""))],
        [sg.Text("Equivalence:"),sg.InputText(key="equivalence", default_text=config.get("equivalence", ""))],
        [sg.Text("Forensic Image Path:"), sg.InputText(key="forensic_image_path", default_text=image_path_arg)],
        [sg.Button("Save", key="save_button"), sg.Button("Connect", key="connect_button")],
        [sg.Text("", key="output_text")]
    ]
    config_tab = sg.Tab("Configuration", config_layout, key="config_tab")

    # Create the about tab
    about_layout = [
        [sg.Text("Forensic VM Client", font=("Helvetica", 20), justification="center")],
        #[sg.Image(os.path.join(os.path.dirname(__file__), "forensicVMClient.jpg"))],
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
            [sg.TabGroup([[virtualize_tab, config_tab, about_tab]])],
        ])]
    ]

    # Create the window
    window = sg.Window("Autopsy ForensicVM Client", layout, element_justification="center", icon=icon_path)

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
            print("Convert")
            window["convert_to_vm_button"].update(visible=False)
            window["link_to_vm_button"].update(visible=False)
            window["import_data_button"].update(visible=True)
            window["open_forensic_vm_button"].update(visible=True)
        elif event == "link_to_vm_button":
            print("Link...")
            window["convert_to_vm_button"].update(visible=False)
            window["link_to_vm_button"].update(visible=False)
            window["import_data_button"].update(visible=True)
            window["open_forensic_vm_button"].update(visible=True)
            # on configure_button click, change to tab config_tab and set visible to True
        elif event == "configure_button":
            window['config_tab'].SetFocus
            window['server_address'].SetFocus
            print("Configure...")


if __name__ == '__main__':
    ForensicVMForm()
