#!/usr/bin/env python

import secrets
import string
import subprocess

# Generate a random password of length 12
alphabet = string.ascii_letters + string.digits
password = ''.join(secrets.choice(alphabet) for i in range(12)) # for a 12-character password

# Name of the secret
secret_name = "grader-api-postgresql"

# Check if the secret already exists
get_secret_command = ["kubectl", "get", "secret", secret_name]
get_secret_process = subprocess.run(get_secret_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# If the secret does not exist, create it
if get_secret_process.returncode != 0:
    create_secret_command = [
        "kubectl", 
        "create", 
        "secret", 
        "generic", 
        secret_name, 
        "--from-literal=postgres-password={}".format(password)
    ]
    subprocess.run(create_secret_command, check=True)
else:
    print("Secret '{}' already exists. Not creating.".format(secret_name))
