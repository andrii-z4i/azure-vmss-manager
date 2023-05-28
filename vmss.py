# This python script will be responsible for fetching the VMSS details from the Azure subscription
# and will provide the names of VM machines by tags (like: role, environment, etc.)
# Resource Group, and VMSS name will be stored in the .config.json file

import json
import subprocess
import argparse
from types import NoneType


_DEBUG_MODE = False

def ddprint(string: str, *args, **kwargs):
    if not _DEBUG_MODE:
        return
    print(string, *args, **kwargs)
    

def request_list_instances(resource_group: str, vmss_name: str) -> dict:
    command = f'az vmss list-instances --resource-group {resource_group} --name {vmss_name}'
    try:
        response = subprocess.check_output(command.split())
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)
        return None

    d_response = json.loads(response)
    return d_response

def request_vm_details(resource_group: str, vm_name: str) -> dict:
    ddprint(f'Getting details for {vm_name}')
    command = f'az vm show --resource-group {resource_group} --name {vm_name}'

    try:
        response = subprocess.check_output(command.split())
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)
        return None
    
    d_response = json.loads(response)
    return d_response

def does_vm_have_tag_set(vm_details: dict, tag_name: str) -> bool:
    if 'tags' not in vm_details:
        return False
    ddprint(f'VM tags: {vm_details["tags"]}')
    if type(vm_details['tags']) == NoneType:
        return False
    if not len(vm_details['tags']):
        return False
    if tag_name not in vm_details['tags']:
        return False
    return True

def get_vm_public_ip(resource_group: str, vm_name: str) -> str:
    command = f'az vm list-ip-addresses --resource-group {resource_group} --name {vm_name}'
    try:
        response = subprocess.check_output(command.split())
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)
        return None
    d_response = json.loads(response)
    public_ips = []
    for vm in d_response:
        if not 'virtualMachine' in vm:
            continue
        if not 'network' in vm['virtualMachine']:
            continue
        if not 'publicIpAddresses' in vm['virtualMachine']['network']:
            continue
        if not len(vm['virtualMachine']['network']['publicIpAddresses']):
            continue
        for ip in vm['virtualMachine']['network']['publicIpAddresses']:
            public_ips.append(ip['ipAddress'])
        
    return public_ips


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get VMSS details')
    parser.add_argument('--resource-group', type=str, help='Resource group name', required=True)
    parser.add_argument('--vmss-name', type=str, help='VMSS name', required=True)
    parser.add_argument('--vm-role', type=str, choices=['node', 'control_plane'], help='VM role', default='node')
    parser.add_argument('--vm-operation', type=str, choices=['ssh',], help='VM operation to perform', default='ssh')
    parser.add_argument('--debug', action='store_true', help='Debug mode', default=False)
    args = parser.parse_args()

    resource_group = args.resource_group
    vmss_name = args.vmss_name
    vm_role = args.vm_role
    vm_operation = args.vm_operation
    _DEBUG_MODE = args.debug

    vm_instances = request_list_instances(resource_group, vmss_name)
    for instance in vm_instances:
        vm_details = request_vm_details(resource_group, instance['name'])
        if not does_vm_have_tag_set(vm_details, 'role'):
            ddprint(f"VM {vm_details['name']} does not have role tag set... skipping")
            continue
        _vm_role = vm_details['tags']['role']
        ddprint(f"VM {vm_details['name']} has role {_vm_role}")
        if _vm_role != vm_role:
            ddprint(f"VM {vm_details['name']} does not have role {vm_role}... skipping")
            continue
        if not vm_operation == 'ssh':
            continue
        public_ips = get_vm_public_ip(resource_group, vm_details['name'])
        
        if not len(public_ips):
            ddprint(f"VM {vm_details['name']} does not have public IP... skipping")
            continue

        print(f'ssh -i ~/.ssh/dev-wallet.pem azureuser@{public_ips[0]}')
    
