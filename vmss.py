import argparse
import paramiko
import kv
import vmss_ip


def ssh_to_vm(public_ip: str, username: str, private_key_path: str):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(public_ip, username=username, key_filename=private_key_path)
    return ssh

def broadcast_command(ssh_connections: list, command: str):
    for ssh in ssh_connections:
        stdin, stdout, stderr = ssh.exec_command(command)
        print(stdout.readlines())
    
def close_ssh_connections(ssh_connections: list):
    for ssh in ssh_connections:
        ssh.close()

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

    private_key = kv.get_secret(args.vault_name, args.secret_name)
    vms_ips = vmss_ip.get_vmss_public_ips(args.resource_group, args.vmss_name, args.tag_name, args.tag_value)
    
    ssh_connection = []

    for vm_name, public_ip in vms_ips.items():
        print(f'VM name: {vm_name}, public IP: {public_ip}')    
        ssh_connection.append(ssh_to_vm(public_ip, args.user_name, private_key))

    broadcast_command(ssh_connection, 'sudo apt-get update')
    close_ssh_connections(ssh_connection)


    
    
