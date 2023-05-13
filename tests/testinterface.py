import PySimpleGUI as sg
import os
import shutil


config = {
    "server_address": "",
    "forensic_api": "",
    "ssh_server_address": "",
    "ssh_server_port": "",
    "folder_share_server": "",
    "share_login": "",
    "share_password": "",
    "equivalence": ""
}

image_config = {
    "folder_share_server": "",
    "share_login": "",
    "share_password": "",
    "equivalence": ""
}

def create_interface():
    # Create the menus
    menu_layout = [['&File', ['&Exit']],
                   ['&Virtualize', ['&Convert to VM', '&Link to VM']],
                   ['&ForensicVM', ['&Open ForensicVM', '&Screenshot', '&Save Screenshots', '&Memory']],
                   ['&VM Control', ['&Start VM', '&Shutdown VM', '&Reset VM', '&Stop VM', '&Delete VM']],
                   ['&Tools', ['&Open ForensicVM WebShell', '&Analyse ForensicVM Performance', '&Import Evidence Disk']],
                   ['&Help', ['&About...']]]

    # Define the layout of the virtualize tab
    virtualize_layout = [
        [sg.Menu(menu_layout)],
        [sg.Text("Cannot communicate with the ForensicVM Server. Please check access configuration on the"
                 " config tab, or check if the server is running. Press the test server button to see if it is running.",
                 key="alert_server_off", visible=False)],
    ]

    # Define the layout of the configuration tab
    config_layout = [
        [sg.Menu(menu_layout)],
        [sg.Frame("Forensic VM Server Configuration",
                  [
                      [sg.Text("Forensic VM server address:"), sg.InputText(key="server_address",
                                                                             default_text=config.get("server_address", ""))],
                      [sg.Text("Forensic API:"), sg.InputText(key="forensic_api",
                                                              default_text=config.get("forensic_api", "")),
                       sg.Button("Test Server Connection", key="test_forensicServer_connect")]
                  ]
                  )
         ],
        [sg.Frame("Windows Share over Forensic SSH Server Redirection",
                  [
                      [sg.Text("SSH Server Address and port:"), sg.InputText(key="ssh_server_address",
                                                                             default_text=config.get("ssh_server_address", ""),
                                                                             size=(20, 1)),
                       sg.InputText(key="ssh_server_port", default_text=config.get("ssh_server_port", ""), size=(8, 1)),
                       sg.Button("Test SSH connection", key="test_ssh_connect"),
                       sg.Button("Copy SSH key to server", key="copy-ssh-key-to-server")]
                  ]
                  )],
        [sg.Frame("Forensic Image source and Windows share",
                  [
                      [sg.Text("Windows folder share server:"), sg.InputText(key="folder_share_server",
                                                                             default_text=image_config.get("folder_share_server",
                                                                                                           config.get("folder_share_server", "")))],
                      [sg.Text("Share login:"), sg.InputText(key="share_login",
                                                             default_text=image_config.get("share_login",
                                                                                           config.get("share_login", "")))],
                      [sg.Text("Share password:"), sg.InputText(key="share_password", password_char="*",
                                                                default_text=image_config.get("share_password",
                                                                                              config.get("share_password", "")))],
                      [sg.Text("Local or remote path to share:"), sg.InputText(key="equivalence",
                                                                               default_text=image_config.get("equivalence",
                                                                                                             config.get("equivalence", ""))),
                       sg.Button("Test Windows share", key="test_windows_share"),
                       sg.Button("Autofill info", key="autofill_share"),
                       sg.Button("Create share", key="create_windows_share")]
                  ]
                  )],
        [sg.Button("Save Configuration", key="save_button", size=(20, 3))],
        [sg.Text("", key="output_text")]
    ]

    # Create the tabs
    # Create the tabs
    virtualize_tab = sg.Tab("Virtualize", virtualize_layout, element_justification="center")
    config_tab = sg.Tab("Configuration", config_layout, key="config_tab")

    # Create the window layout
    layout = [[sg.TabGroup([[virtualize_tab, config_tab]])]]

    # Create the window
    window = sg.Window("ISO File Manager", layout)

    # Event loop
    while True:
        event, values = window.read()

        # Exit the program if the window is closed
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break

        # Handle menu and submenu events
        if event == "Convert to VM":
            # Handle Convert to VM action
            pass
        elif event == "Link to VM":
            # Handle Link to VM action
            pass
        elif event == "Open ForensicVM":
            # Handle Open ForensicVM action
            pass
        elif event == "Screenshot":
            # Handle Screenshot action
            pass
        elif event == "Save Screenshots":
            # Handle Save Screenshots action
            pass
        elif event == "Memory":
            # Handle Memory action
            pass
        elif event == "Start VM":
            # Handle Start VM action
            pass
        elif event == "Shutdown VM":
            # Handle Shutdown VM action
            pass
        elif event == "Reset VM":
            # Handle Reset VM action
            pass
        elif event == "Stop VM":
            # Handle Stop VM action
            pass
        elif event == "Delete VM":
            # Handle Delete VM action
            pass
        elif event == "Open ForensicVM WebShell":
            # Handle Open ForensicVM WebShell action
            pass
        elif event == "Analyse ForensicVM Performance":
            # Handle Analyse ForensicVM Performance action
            pass
        elif event == "Import Evidence Disk":
            # Handle Import Evidence Disk action
            pass

    # Close the window
    window.close()

# Call the create_interface function
create_interface()
