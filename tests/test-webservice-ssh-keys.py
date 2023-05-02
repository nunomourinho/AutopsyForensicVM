import requests

import os
import requests
import paramiko

# def send_public_key(baseurl, api_key, public_key):
#     # Send public key to server
#     url = baseurl + '/api/add-public-key/'
#     headers = {
#         'X-Api-Key': api_key
#     }
#
#     data = {
#         'public_key': public_key
#     }
#
#     response = requests.post(url, headers=headers, data=data)
#
#     if response.status_code == 200:
#         return 'Public key added to authorized keys'
#     else:
#         return 'Failed to add public key to authorized keys'

def generate_and_send_public_key(baseurl, api_key, ssh_dir):
    # Generate SSH key pair

    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir)

    private_key_path = os.path.join(ssh_dir, 'mykey')
    public_key_path = os.path.join(ssh_dir, 'mykey.pub')

    if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(private_key_path)
        #key.write_public_key_file(public_key_path)
        # Save public key to disk
        public_key_path = f"{private_key_path}.pub"
        with open(public_key_path, "w") as public_key_file:
            public_key_file.write(f"{key.get_name()} {key.get_base64()}")

    with open(public_key_path, 'r') as f:
        public_key = f.read().strip()

    # Send public key to server
    url = baseurl + '/api/create-ssh-keys/'
    headers = {
        'X-Api-Key': api_key
    }

    data = {
        'public_key': public_key
    }

    response = requests.post(url, headers=headers, data=data)

    # if response.status_code == 200:
    #     return 'Public key added to authorized keys'
    # else:
    #     return 'Failed to add public key to authorized keys'
    return response.json().get('message'), response.status_code

# Main function
if __name__ == '__main__':
    ssh_dir = os.path.expanduser('ssh_keys')
    # Send public key to server
    api_key = 'd0397945-5c8b-432c-8cbf-010d4b8fc7fb'
    server_path = 'http://85.240.2.211:8000'
    message, status_code = generate_and_send_public_key(server_path, api_key, ssh_dir)

    print(message)
    print(status_code)


