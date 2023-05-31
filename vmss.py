import argparse
import paramiko
import kv
import vmss_ip


def ssh_to_vm(public_ip: str, username: str, private_key: str):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(public_ip, username=username, key_filename=private_key)
    return ssh

def broadcast_command(ssh_connections: list, command: str):
    for ssh in ssh_connections:
        stdin, stdout, stderr = ssh_connections[ssh].exec_command(command)
        for line in stdout.readlines():
            print(f'{ssh} -- {line.strip()}')
    
def close_ssh_connections(ssh_connections: dict):
    for ssh in ssh_connections:
        ssh_connections[ssh].close()

def save_private_key_to_file(private_key: str, file_name: str):
    with open(file_name, 'w') as f:
        f.write(private_key)

def remove_private_key_file(file_name: str):
    import os
    os.remove(file_name)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get VMSS details')
    parser.add_argument('--resource-group', type=str, help='Resource group name', required=True)
    parser.add_argument('--vmss-name', type=str, help='VMSS name', required=True)
    parser.add_argument('--tag-name', type=str, help="Tag name to filter by", required=False)
    parser.add_argument('--tag-value', type=str, help="Tag value to filter by", required=False)
    parser.add_argument('--user-name', type=str, help='VM user name', default='azureuser')
    parser.add_argument('--vault-name', type=str, help="Vault name with private key stored", required=True)
    parser.add_argument('--secret-name', type=str, help="Secret name with private key stored", required=True)
    
    args = parser.parse_args()

    ssh_connection = {}
    private_key = kv.get_secret(args.vault_name, args.secret_name)
    save_private_key_to_file(private_key, 'private_key.pem')

    try:
        vms_ips = vmss_ip.get_vmss_public_ips(args.resource_group, args.vmss_name, args.tag_name, args.tag_value)
        
        for vm_name, public_ip in vms_ips.items():
            if not public_ip or not len(public_ip):
                continue
            print(f'VM name: {vm_name}, public IP: {public_ip[0]}') 
            ssh_connection[public_ip[0]] = ssh_to_vm(public_ip[0], args.user_name, 'private_key.pem')
        broadcast_command(ssh_connection, 'sudo apt-get update')
    except Exception as e:
        print(e)
    finally:
        close_ssh_connections(ssh_connection)
        remove_private_key_file('private_key.pem')


    
    
