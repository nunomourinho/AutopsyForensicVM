import PySimpleGUI as sg
import os
import shutil

# Define the layout of the interface
layout = [
    [sg.Text("Upload ISO File")],
    [sg.Input(key="-UPLOAD_FILE-", enable_events=True, visible=False), sg.FileBrowse()],
    [sg.Button("Upload")],
    [sg.Text("ISO Files in Directory")],
    [sg.Listbox(values=[], size=(40, 10), key="-FILE_LIST-")],
    [sg.Button("Delete")]
]

# Create the window
window = sg.Window("ISO File Manager", layout)

# Event loop
while True:
    event, values = window.read()

    # Exit the program if the window is closed
    if event == sg.WINDOW_CLOSED:
        break

    # Upload a file
    if event == "Upload":
        file_path = values["-UPLOAD_FILE-"]
        if file_path:
            file_name = os.path.basename(file_path)
            # Move the uploaded file to the current directory
            shutil.move(file_path, file_name)

    # Delete a file
    if event == "Delete":
        selected_files = values["-FILE_LIST-"]
        if selected_files:
            for file_name in selected_files:
                os.remove(file_name)

    # Update the list of files in the directory
    file_list = os.listdir()
    window["-FILE_LIST-"].update(file_list)

# Close the window
window.close()
