import os
import paramiko

# Generate SSH key pair
###ssh_key = paramiko.rsakey.RSAKey.generate(2048)

# Save private key to disk
private_key_path = os.path.expanduser("mykey")
print(private_key_path)
###ssh_key.write_private_key_file(private_key_path)

# Save public key to disk
###public_key_path = f"{private_key_path}.pub"
###with open(public_key_path, "w") as public_key_file:
    ###public_key_file.write(f"{ssh_key.get_name()} {ssh_key.get_base64()}")

# Connect to remote host using SSH key authentication
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('85.240.2.211', username='forensicinvestigator', key_filename=private_key_path, port=8228)

# Run a command on the remote host and print the output
stdin, stdout, stderr = ssh.exec_command('ls -al')
for line in stdout:
    print(line.strip())

# Close the SSH connection
ssh.close()
