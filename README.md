# azure-vmss-manager

## Overview
This repository is intended to help managing of Azure Virtual Machine Scale Sets (VMSS) using Azure CLI 2.0. It is a collection of scripts that can be used to perform various operations on VMSS.

## Prerequisites
* Azure CLI 2.0
* Azure Subscription
* Created VMSS

## Usage

The main use case for this repository is to perform operations on VMSS. The following operations are supported:
* connecting to VMSS instances via SSH
* executing commands on VMSS instances
* filtering VMSS instances by tags to perform operations on specific instances

### Connecting to VMSS instances via SSH

To connect to VMSS instances via SSH, use the following command:

```
vmss.py --resource-group <rg> --vmss-name <vmss-name>  --vault-name <kv> --secret-name <secret> --tag-name <user-defined-tag> --tag-value <user-defined-value>
```

If connection to VMSS instances is successful, the script will print out the following message:

```
VM name: dev-vmss_d5d91752, public IP: 4.246.207.2
Enter command:
```

Command will be executed on all VMSS instances that match the provided tag name and value. If no tag name and value are provided, command will be executed on all VMSS instances.

```
VM name: dev-vmss_7560ad4b, public IP: 4.246.207.1
VM name: dev-vmss_d5d91752, public IP: 4.246.207.2
VM name: dev-vmss_de3db832, public IP: 4.246.207.3
Enter command: mkdir prj
Executing command on 4.246.207.1 -- mkdir prj
Executing command on 4.246.207.2 -- mkdir prj
Executing command on 4.246.207.3 -- mkdir prj
Enter command: ls
Executing command on 4.246.207.1 -- ls
[4.246.207.1] -- prj
Executing command on 4.246.207.2 -- ls
[4.246.207.2] -- prj
Executing command on 4.246.207.3 -- ls
[4.246.207.3] -- prj
```

To finish execution of the script, type `exit` and press `Enter`.

### Warning

During the execution of the script, the secret is stored in a temporary file. The file is deleted after the script finishes execution. However, if the script is interrupted, the file will not be deleted. In this case, the file should be deleted manually.