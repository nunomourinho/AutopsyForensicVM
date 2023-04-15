import subprocess
import threading
import queue

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line.decode())
    out.close()

def run_ssh_commands(ssh_details, commands):
    # Prepare the ssh command
    ssh_cmd = f'ssh -i {ssh_details["key"]} -oStrictHostKeyChecking=no {ssh_details["user"]}@{ssh_details["host"]} -p {ssh_details["port"]}'

    # Run the ssh command using subprocess
    p = subprocess.Popen(ssh_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Send the commands to the remote server
    for cmd in commands:
        p.stdin.write((cmd + '\n').encode())
        p.stdin.flush()

    # Create a queue and a thread to read the output
    output_queue = queue.Queue()
    output_thread = threading.Thread(target=enqueue_output, args=(p.stdout, output_queue))
    output_thread.daemon = True
    output_thread.start()

    # Read and print the output
    while p.poll() is None:
        while not output_queue.empty():
            output = output_queue.get_nowait()
            if output:
                print(output.strip())

    # Read any remaining output after the process has ended
    while not output_queue.empty():
        output = output_queue.get_nowait()
        if output:
            print(output.strip())

if __name__ == "__main__":
    ssh_details = {
        "key": "mykey",
        "user": "forensicinvestigator",
        "host": "85.240.2.211",
        "port": 8228
    }

    # Add the commands you want to run on the remote server
    commands = [
        "ls -al",
        "ps -ef",
        "ls -alh"
    ]

    run_ssh_commands(ssh_details, commands)
