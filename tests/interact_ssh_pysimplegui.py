import PySimpleGUI as sg
import threading
from run_ssh_commands import run_ssh_commands

ssh_details = {
    "key": "mykey",
    "user": "forensicinvestigator",
    "host": "85.240.2.211",
    "port": 8228
}

def execute_commands(output_callback, stop_event):
    commands = window["COMMANDS"].get().strip().split('\n')
    run_ssh_commands(ssh_details, commands, output_callback, stop_event)


def handle_output(stream_type, output):
    if stream_type == "stdout":
        window.write_event_value("UPDATE_OUTPUT", output)
    elif stream_type == "stderr":
        window.write_event_value("UPDATE_ERROR_OUTPUT", output)


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
output_thread = None
stop_event = threading.Event()
while True:
    event, values = window.read(timeout=100)

    # Check if the output_thread is still alive
    if output_thread is not None and not output_thread.is_alive():
        output_thread = None
        stop_event.clear()

    if event in (sg.WIN_CLOSED, "Exit"):
        # If output_thread is still running, ask the user if they want to close the program
        if output_thread is not None:
            close = sg.popup_yes_no("Commands are still running. Are you sure you want to exit?", title="Exit Confirmation")
            if close == "Yes":
                stop_event.set()
                output_thread.join()
                break
        else:
            break

    if event == "RUN":
        commands = values["COMMANDS"].strip().split('\n')
        print("Running commands...")

        # Run the execute_commands function in a separate thread
        output_thread = threading.Thread(target=execute_commands, args=(handle_output, stop_event))
        output_thread.start()

    if event == "UPDATE_OUTPUT":
        output = values["UPDATE_OUTPUT"]
        window["OUTPUT"].print(output)

    if event == "UPDATE_ERROR_OUTPUT":
        error_output = values["UPDATE_ERROR_OUTPUT"]
        window["OUTPUT"].print(error_output, text_color="red")
