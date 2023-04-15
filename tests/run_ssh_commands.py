import subprocess
import threading
import queue

def enqueue_output(stream_type, stream, out_queue):
    for line in iter(stream.readline, b''):
        out_queue.put((stream_type, line.decode()))
    stream.close()

def run_ssh_commands(ssh_details, commands, output_callback):
    # Prepare the ssh command
    ssh_cmd = f'ssh -i {ssh_details["key"]} -oStrictHostKeyChecking=no {ssh_details["user"]}@{ssh_details["host"]} -p {ssh_details["port"]}'

    # Run the ssh command using subprocess
    p = subprocess.Popen(ssh_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Send the commands to the remote server
    for cmd in commands:
        p.stdin.write((cmd + '\n').encode())
        p.stdin.flush()

    # Create a queue and threads to read the output and error output
    output_queue = queue.Queue()
    stdout_thread = threading.Thread(target=enqueue_output, args=("stdout", p.stdout, output_queue))
    stderr_thread = threading.Thread(target=enqueue_output, args=("stderr", p.stderr, output_queue))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

    # Read and call output_callback with the output and error output
    while p.poll() is None or stdout_thread.is_alive() or stderr_thread.is_alive():
        while not output_queue.empty():
            stream_type, output = output_queue.get_nowait()
            if output:
                output_callback(stream_type, output.strip())

    # Read any remaining output and error output after the process has ended
    while not output_queue.empty():
        stream_type, output = output_queue.get_nowait()
        if output:
            output_callback(stream_type, output.strip())
