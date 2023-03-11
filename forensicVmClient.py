import os
import re
import json
import PySimpleGUI as sg
import socket

# Define the filename for the JSON file
filename = "config.json"

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


def ForensicVMForm():
    # Set the theme
    sg.theme("DefaultNoMoreNagging")

    # Load the configuration from the JSON file if it exists
    config = load_config()
    
    # Create the layout for the configuration tab
    config_layout = [
        [sg.Text("Forensic VM server address:"), sg.InputText(key="server_address", default_text=config.get("server_address", ""))],
        [sg.Text("Forensic API:"), sg.InputText(key="forensic_api", default_text=config.get("forensic_api", ""))],
        [sg.Text("Windows folder share server:"), sg.InputText(key="folder_share_server", default_text=config.get("folder_share_server", ""))],
        [sg.Text("Share login:"), sg.InputText(key="share_login", default_text=config.get("share_login", ""))],
        [sg.Text("Share password:"), sg.InputText(key="share_password", password_char="*", default_text=config.get("share_password", ""))],
        [sg.Text("Forensic image local path:"), sg.InputText(key="forensic_image_path", default_text=config.get("forensic_image_path", ""))],
        [sg.Text("Equivalence:"),sg.InputText(key="equivalence", default_text=config.get("equivalence", ""))],
        [sg.Button("Save", key="save_button"), sg.Button("Connect", key="connect_button")],
        [sg.Text("", key="output_text")]
    ]
    config_tab = sg.Tab("Configuration", config_layout)

    # Create the about tab
    about_layout = [
        [sg.Text("Forensic VM Client", font=("Helvetica", 20), justification="center")],
        #[sg.Image(os.path.join(os.path.dirname(__file__), "forensicVMClient.jpg"))],
        [sg.Image("forensicVMClient.png")],
        [sg.Text("Version 1.0", justification="center")],
        [sg.Text("This software is provided as-is, without warranty of any kind. Use at your own risk.")],
        [sg.Text("Created by Your Name Here", font=("Helvetica", 10), justification="center")],
    ]
    about_tab = sg.Tab("About", about_layout)

    # Create the layout for the window
    layout = [
        [sg.TabGroup([
            [sg.TabGroup([[config_tab, about_tab]])],
        ])]
    ]

    # Create the window
    window = sg.Window("Forensic VM Connection Form", layout)

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

if __name__ == '__main__':
    ForensicVMForm()
