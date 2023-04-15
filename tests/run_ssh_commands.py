import subprocess
import threading
import queue

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line.decode())
    out.close()

def run_ssh_commands(ssh_details, commands, output_callback):
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

    # Read and call output_callback with the output
    while p.poll() is None:
        while not output_queue.empty():
            output = output_queue.get_nowait()
            if output:
                output_callback(output.strip())

    # Read any remaining output after the process has ended
    while not output_queue.empty():
        output = output_queue.get_nowait()
        if output:
            output_callback(output.strip())
