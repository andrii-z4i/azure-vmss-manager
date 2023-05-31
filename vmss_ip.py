import json
import subprocess
import argparse


def request_instances_names(resource_group: str, vmss_name: str) -> dict:
    command = f'az vmss list-instances --resource-group {resource_group} --name {vmss_name}'
    try:
        response = subprocess.check_output(command.split())
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)
        return None

    d_response = json.loads(response)
    vm_instances = []
    for vm_instance in d_response:
        vm_instances.append(vm_instance['name'])
    return vm_instances

def request_vm_details(resource_group: str, vm_name: str) -> dict:
    command = f'az vm show --resource-group {resource_group} --name {vm_name}'

    try:
        response = subprocess.check_output(command.split())
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)
        return None
    
    d_response = json.loads(response)
    return d_response


def does_vm_have_tag_set(vm_details: dict, tag_name: str, tag_value: str) -> bool:
    if 'tags' not in vm_details:
        return False
    if not vm_details['tags']:
        return False
    if tag_name not in vm_details['tags']:
        return False
    if vm_details['tags'][tag_name] != tag_value:
        return False
    return True

def extract_public_ips(d_response):
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

def get_vm_public_ip(resource_group: str, vm_name: str) -> str:
    command = f'az vm list-ip-addresses --resource-group {resource_group} --name {vm_name}'
    
    try:
        response = subprocess.check_output(command.split())
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)
        return None
    
    d_response = json.loads(response)
    return extract_public_ips(d_response)

def get_vmss_public_ips(resource_group: str, vmss_name: str, tag_name: str = None, tag_value: str = None) -> list:
    vms_ips = {}
    vm_names = request_instances_names(resource_group, vmss_name)
    for vm_name in vm_names:
        vm_details = request_vm_details(resource_group, vm_name)
        
        if tag_name and \
            tag_value and \
            not does_vm_have_tag_set(vm_details, tag_name, tag_value):
                continue # skip this vm
        vms_ips[vm_name] = get_vm_public_ip(resource_group, vm_name)
    return vms_ips


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--resource-group', required=True)
    args.add_argument('--vmss-name', required=True)
    args.add_argument('--tag-name', required=False)
    args.add_argument('--tag-value', required=False)

    args = args.parse_args()
    vms_ips = get_vmss_public_ips(args.resource_group, args.vmss_name, args.tag_name, args.tag_value)
    
    print(json.dumps(vms_ips, indent=4))

