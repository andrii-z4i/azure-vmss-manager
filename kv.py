import json
import subprocess
import argparse

# we will execut az command to fetch the secret in Azure Key Vault
# az keyvault secret show --vault-name <vault-name> --name <secret-name>

def get_secret(vault_name: str, secret_name: str) -> str:
    command = f'az keyvault secret show --vault-name {vault_name} --name {secret_name}'
    try:
        response = subprocess.check_output(command.split())
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)
        return None

    d_response = json.loads(response)
    return d_response['value']

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--vault-name', required=True)
    args.add_argument('--secret-name', required=True)

    args = args.parse_args()

    secret = get_secret(args.vault_name, args.secret_name)
    print(secret)

