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



def run_command(command):
    global shell

    # Set the encoding for the subprocess
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'cp1252'

    remote_command = "ssh -i mykey -oStrictHostKeyChecking=no " \
                     "forensicinvestigator@85.240.2.211 -p 8228 -R 4451:localhost:445 "

    shell = subprocess.Popen(
        remote_command +
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, env=env)

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
    # Create a thread to read output from the shell process
    output_thread = threading.Thread(target=read_output, args=(shell, windowCommand), daemon=True)
    output_thread.start()
    while True:
        event, values = windowCommand.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == 'Execute':
            cmd = values['input']
            if cmd:
                send_command(shell, cmd)
        elif event == 'output':
            print(values[event])
    # Close the shell process before closing the windowCommand
    send_command(shell, 'exit')
    shell.wait()
    windowCommand.close()
    windowCommand.__del__()



run_command("ls -alh; ls -alh /;ps -ef; netstat -tupl")
run_command("ls -alh; ls -alh /;ps -ef; netstat -tupl")