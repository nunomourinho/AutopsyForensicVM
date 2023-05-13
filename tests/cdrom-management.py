import PySimpleGUI as sg
import os
import requests

# Helper function to update CDROM list
def update_cdrom_list():
    # Call the list_iso_files function to retrieve the CDROM list
    cdroms = list_iso_files(api_key, base_url)

    # Clear the CDROM listbox and update it with the retrieved CDROMs
    window['-CDROM LIST-'].update(values=cdroms)


# Helper function to upload a CDROM
def upload_cdrom(filename):
    url = f"{base_url}/api/upload-cdrom/"
    headers = {"X-API-KEY": api_key}

    try:
        with open(filename, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()

        sg.popup('CDROM uploaded successfully!')
        update_cdrom_list()

    except requests.exceptions.HTTPError as e:
        sg.popup_error(f"Error: {response.status_code}")
        sg.popup_error(response.text)


# Initialize PySimpleGUI theme
sg.theme('DefaultNoMoreNagging')

# Define the layout for the main window
upload_frame = sg.Frame('Upload', [
        [sg.Input(key='-CDROM FILE-', enable_events=True, visible=False), sg.FileBrowse('Browse', key='-BROWSE-', file_types=(('ISO Files', '*.iso'),)) ,sg.Button('Upload', key='-UPLOAD-', disabled=True)]
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

iso_layout = [
    [sg.Frame('ISO Management', [
        [sg.Listbox([], size=(61, 7), key='-CDROM LIST-', enable_events=True)],
        [list_frame, cdrom_frame, upload_frame, delete_frame],
    ])]
]
"""
Main Layout: ISO Management
- Contains a frame named 'ISO Management'
- Frame contains:
  - Listbox for displaying CD-ROMs
  - Other frames for managing CD-ROMs (list_frame, cdrom_frame, upload_frame, delete_frame)
"""



# Create the main window
window = sg.Window('Blu-ray Management', iso_layout)

# Event loop
while True:
    event, values = window.read()

    # Exit the program if the window is closed or "Exit" button is clicked
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break

    # Handle CDROM selection event
    if event == '-CDROM LIST-':
        selected_cdrom = values['-CDROM LIST-'][0]
        if selected_cdrom:
            # Enable the Insert, Eject, and Delete buttons
            window['-INSERT-'].update(disabled=False)
            window['-EJECT-'].update(disabled=False)
            window['-DELETE-'].update(disabled=False)
        else:
            # Disable the Insert, Eject, and Delete buttons
            window['-INSERT-'].update(disabled=True)
            window['-EJECT-'].update(disabled=True)
            window['-DELETE-'].update(disabled=True)

    # Handle Insert button click event
    if event == '-INSERT-':
        selected_cdrom = values['-CDROM LIST-'][0]
        if selected_cdrom:
            # Call the insert_cdrom function to insert the selected CDROM
            insert_cdrom(api_key, base_url, selected_cdrom)
            sg.popup('CDROM inserted successfully!')

    # Handle Eject button click event
    if event == '-EJECT-':
        selected_cdrom = values['-CDROM LIST-'][0]
        if selected_cdrom:
            # Call the eject_cdrom function to eject the selected
            # Handle Delete button click event
            if event == '-DELETE-':
                selected_cdrom = values['-CDROM LIST-'][0]
                if selected_cdrom:
                    # Call the delete_cdrom function to delete the selected CDROM
                    delete_cdrom(api_key, base_url, selected_cdrom)
                    sg.popup('CDROM deleted successfully!')

            # Handle CDROM file selection event
            if event == '-CDROM FILE-':
                cdrom_file = values['-CDROM FILE-']
                if cdrom_file:
                    # Enable the Upload button
                    window['-UPLOAD-'].update(disabled=False)

            # Handle Upload button click event
            if event == '-UPLOAD-':
                cdrom_file = values['-CDROM FILE-']
                if cdrom_file:
                    upload_cdrom(cdrom_file)

            # Handle File Browse button click event
            if event == '-BROWSE-':
                # Show the file selection input element
                window['-CDROM FILE-'].update(visible=True)

            # Update the CDROM list after any modifications
            update_cdrom_list()

            # Close the window
        window.close()
