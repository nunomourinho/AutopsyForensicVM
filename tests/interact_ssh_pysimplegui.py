import PySimpleGUI as sg
import threading
from run_ssh_commands import run_ssh_commands

ssh_details = {
    "key": "mykey",
    "user": "forensicinvestigator",
    "host": "85.240.2.211",
    "port": 8228
}

# Function to execute the entered commands
def execute_commands(commands, output_callback):
    run_ssh_commands(ssh_details, commands, output_callback)

# Create the GUI layout
layout = [
    [sg.Text("Enter commands (one per line):")],
    [sg.Multiline(size=(60, 10), key="COMMANDS")],
    [sg.Text("Output:")],
    [sg.Output(size=(60, 20), key="OUTPUT")],
    [sg.Button("Run Commands", key="RUN"), sg.Button("Exit")]
]

# Create the window
window = sg.Window("SSH Command Runner", layout)

# Event loop
while True:
    event, values = window.read(timeout=100)

    if event in (sg.WIN_CLOSED, "Exit"):
        break

    if event == "RUN":
        commands = values["COMMANDS"].strip().split('\n')
        print("Running commands...")

        # Run the execute_commands function in a separate thread
        output_thread = threading.Thread(target=execute_commands, args=(commands, print))
        output_thread.start()

window.close()
