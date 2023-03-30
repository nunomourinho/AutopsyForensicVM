import subprocess
import PySimpleGUI as sg
import os
import threading

def send_command(proc, command):
    proc.stdin.write(command + '\n')
    proc.stdin.flush()

def read_output(proc, window):
    while True:
        output = proc.stdout.readline()
        if output:
            window.write_event_value('output', output.strip())
        else:
            break

shell = subprocess.Popen('ssh-test.bat', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

layout = [
    [sg.Text('Interactive Command Prompt')],
    [sg.Output(size=(80, 20))],
    [sg.InputText(key='input', size=(80, 1)), sg.Button('Execute')],
    [sg.Button('Exit')],
]

window = sg.Window('Interactive Command Prompt', layout, finalize=True)

# Redirect stderr to stdout for the shell process
shell.stderr.close()
shell.stderr = shell.stdout

# Create a thread to read output from the shell process
output_thread = threading.Thread(target=read_output, args=(shell, window), daemon=True)
output_thread.start()

while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == 'Execute':
        cmd = values['input']
        if cmd:
            send_command(shell, cmd)
    elif event == 'output':
        print(values[event])

# Close the shell process before closing the window
send_command(shell, 'exit')
shell.wait()
window.close()
