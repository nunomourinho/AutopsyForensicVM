import time
import subprocess
import PySimpleGUI as sg
import os
import threading
import sys
import queue

def send_command(proc, command):
    proc.stdin.write(command + '\n')
    proc.stdin.flush()

def read_output(proc, output_queue):
    while True:
        output = proc.stdout.readline()
        if output:
            output_queue.put(output.strip())
        else:
            time.sleep(0.1)  # Add a small delay to avoid high CPU usage

def run_commands(commands):
    global shell

    # Set the encoding for the subprocess
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'cp1252'

    remote_command = "ssh -i mykey -oStrictHostKeyChecking=no " \
                     "forensicinvestigator@85.240.2.211 -p 8228 -R 4451:localhost:445 "

    shell = subprocess.Popen(
        remote_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, env=env)

    layoutCommand = [
        [sg.Text('Interactive Command Prompt')],
        [sg.Output(size=(80, 20))],
        [sg.InputText(key='input', size=(80, 1)), sg.Button('Execute')],
        [sg.Button('Exit')],
    ]
    windowCommand = sg.Window('Interactive Command Prompt', layoutCommand, finalize=True)
    # Redirect stderr to stdout for the shell process
    shell.stderr.close()
    shell.stderr = shell.stdout

    output_queue = queue.Queue()

    # Create a thread to read output from the shell process
    output_thread = threading.Thread(target=read_output, args=(shell, output_queue), daemon=True)
    output_thread.start()

    # Add this line at the end of the function to trigger the initial commands
    windowCommand.write_event_value('run_initial_commands', commands)

    while True:
        event, values = windowCommand.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == 'Execute':
            cmd = values['input']
            if cmd:
                send_command(shell, cmd)
        # Add this block to handle the new event
        elif event == 'run_initial_commands':
            for command in values[event]:
                send_command(shell, command)

        # Add this block to handle the output from the queue
        while not output_queue.empty():
            print(output_queue.get())


    # Remove the shell.wait() line
    send_command(shell, 'exit')
    windowCommand.close()
    windowCommand.__del__()

commands = [
    "ls -alh",
    "ls -alh /",
    "ps -ef",
    "netstat -tupl"
]

run_commands(commands)
