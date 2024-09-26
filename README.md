# NSX Policy Migration Scripts

These files are base script examples to be able to move VM's to a blank/new NSX Manager environment. They dont move the VM's themselves, but rather store NSX security tag(s) to VM infomation in a CSV, then allow you to play that back at the new environment, applying the tags if the VM name matches. They also do the same with NSX Security Policy Groups. These should be done first, in order, ahead of any DFW export / import as exporting firewall configuration will export only the firewall rules definition but not the groups and other objects.

# Files

Use these in order to extract tag , vm name and vm-id. 
Then push these onto the VM's once they exist with the same name in new environment

Then groups can be extracted and pushed next, as if groups referencetags that arent yet created it will fail

 - Naturally, replace NSX-T Manager details to suit.  
 - Tested against NSX-T API 4.1.2.3 and python 3.11

**Note:** *The material embodied in this repo is provided to you "as-is" and without warranty of any kind, express, implied or otherwise, including without limitation, any warranty of security and or fitness for a particular purpose. It is an example only, to be used in non-production environments only.*

## tagspullwithvm.py

This will extract VMs and their associated **tag value**, **tag scope**, **tag descr**, **VM name**, and **VM ID** and create a csv file

 - Orders the csv file based on VM Name
 - Will create multiple rows for VM's with more than
   one tag pair
 - Will leave csv cells blank if VM's have no tags     
 - Caters for exact match exclusion of string matching to tag value OR tag scope

## tagspushwithvm.py

This will use the csv data, and push the tags onto any VM's match on the same **VM Name**
*(not VM ID, as this would of changed with vMotion into new vCenter domain)*

 - Will overwrite any existing tags which may be applied to the VM
 - Will send multiple tags into VM in one API call

### Example csv for tags pull/push 

| Tag Scope | Tag Value | Tag Descr | VM Name | VM ID |
|--|--|--|--|--|
| security | high888 |  | Kali | 503e0c93-840c-1a9e-f6b3-57a78210a55b |
| security | high999 |  | Kali | 503e0c93-840c-1a9e-f6b3-57a78210a55b |
| env | prod |  | ubuntu01 | 503e8ea4-d5f5-f667-b703-03bc3aa6a2c6 |

## groupspull.py

Pulls the NSX Security Group and its related matching criteria, tags, ipsets etc

 - Allows exclusion strings
 - Will ask for groups in single API call, and store them in a csv file

## groupspush.py

Pushes the NSX Security Groups from csv and its related matching criteria, tags, ipsets etc

 - Checks if Group exists by name, if so will skip adding it
 - The group name may contain spaces etc which API doesnt like, so underscore is added just like adding it via UI anyways

### Example csv for groups pull/push 

| Group Name | Description | Members | Tags |
|--|--|--|--|
| Others_Internet-vRNI-Import-Tier| N/A|"[{'ip_addresses': ['192.169.0.0-198.17.255.255', '192.0.3.0-192.88.98.255', '129.0.0.0-169.253.255.255', '172.32.0.0-191.0.1.255', '1.0.0.0-9.255.255.255', '192.88.100.0-192.167.255.255', '11.0.0.0-126.255.255.255', '198.20.0.0-223.255.255.255'], 'resource_type': 'IPAddressExpression', 'id': 'eb15fee8-662d-4071-b500-aff6a1e775ac', 'path': '/infra/domains/default/groups/Others_Internet-vRNI-Import-Tier/ip-address-expressions/eb15fee8-662d-4071-b500-aff6a1e775ac', 'relative_path': 'eb15fee8-662d-4071-b500-aff6a1e775ac', 'parent_path': '/infra/domains/default/groups/Others_Internet-vRNI-Import-Tier', 'remote_path': '', 'marked_for_delete': False, 'overridden': False, '_protection': 'NOT_PROTECTED'}]",No Tags|
Ping Test| N/A| "[{'member_type': 'VirtualMachine', 'key': 'Tag', 'operator': 'EQUALS', 'scope_operator': 'EQUALS', 'value': 'OS Steve Windows', 'resource_type': 'Condition', 'id': 'f27838fb-23d7-40e4-bdee-59bbbf63f880', 'path': '/infra/domains/default/groups/Ping_Test/condition-expressions/f27838fb-23d7-40e4-bdee-59bbbf63f880', 'relative_path': 'f27838fb-23d7-40e4-bdee-59bbbf63f880', 'parent_path': '/infra/domains/default/groups/Ping_Test', 'remote_path': '', 'marked_for_delete': False, 'overridden': False, '_protection': 'NOT_PROTECTED'}, {'conjunction_operator': 'OR', 'resource_type': 'ConjunctionOperator', 'id': 'e7b6515f-2f88-4fb8-ab8c-9e6cafbe1e4d', 'path': '/infra/domains/default/groups/Ping_Test/conjunction-expressions/e7b6515f-2f88-4fb8-ab8c-9e6cafbe1e4d', 'relative_path': 'e7b6515f-2f88-4fb8-ab8c-9e6cafbe1e4d', 'parent_path': '/infra/domains/default/groups/Ping_Test', 'remote_path': '', 'marked_for_delete': False, 'overridden': False, '_protection': 'NOT_PROTECTED'}, {'member_type': 'VirtualMachine', 'key': 'Tag', 'operator': 'EQUALS', 'scope_operator': 'EQUALS', 'value': 'PRD Shared_Services', 'resource_type': 'Condition', 'id': 'b1d71220-f1d3-4b92-b6de-3d537c51a2d3', 'path': '/infra/domains/default/groups/Ping_Test/condition-expressions/b1d71220-f1d3-4b92-b6de-3d537c51a2d3', 'relative_path': 'b1d71220-f1d3-4b92-b6de-3d537c51a2d3', 'parent_path': '/infra/domains/default/groups/Ping_Test', 'remote_path': '', 'marked_for_delete': False, 'overridden': False, '_protection': 'NOT_PROTECTED'}, {'conjunction_operator': 'OR', 'resource_type': 'ConjunctionOperator', 'id': '9bef6fe7-eb6c-429e-bba4-1a94b58d559f', 'path': '/infra/domains/default/groups/Ping_Test/conjunction-expressions/9bef6fe7-eb6c-429e-bba4-1a94b58d559f', 'relative_path': '9bef6fe7-eb6c-429e-bba4-1a94b58d559f', 'parent_path': '/infra/domains/default/groups/Ping_Test', 'remote_path': '', 'marked_for_delete': False, 'overridden': False, '_protection': 'NOT_PROTECTED'}, {'ip_addresses': ['1.1.1.1/32', '2.2.2.2/32'], 'resource_type': 'IPAddressExpression', 'id': '7eea02ed-0037-4004-91eb-28a9e9629895', 'path': '/infra/domains/default/groups/Ping_Test/ip-address-expressions/7eea02ed-0037-4004-91eb-28a9e9629895', 'relative_path': '7eea02ed-0037-4004-91eb-28a9e9629895', 'parent_path': '/infra/domains/default/groups/Ping_Test', 'remote_path': '', 'marked_for_delete': False, 'overridden': False, '_protection': 'NOT_PROTECTED'}]",No Tags  |
CHILDgroup | N/A| "[{'member_type': 'VirtualMachine', 'key': 'Tag', 'operator': 'EQUALS', 'scope_operator': 'EQUALS', 'value': 'OS Steve Windows', 'resource_type': 'Condition', 'id': 'e78826cb-e27d-40a5-83b3-7b17ca7c401f', 'path': '/infra/domains/default/groups/CHILDgroup/condition-expressions/e78826cb-e27d-40a5-83b3-7b17ca7c401f', 'relative_path': 'e78826cb-e27d-40a5-83b3-7b17ca7c401f', 'parent_path': '/infra/domains/default/groups/CHILDgroup', 'remote_path': '', 'marked_for_delete': False, 'overridden': False, '_protection': 'NOT_PROTECTED'}, {'conjunction_operator': 'OR', 'resource_type': 'ConjunctionOperator', 'id': '4d0be740-6bda-4050-b5e3-e5462d1fec24', 'path': '/infra/domains/default/groups/CHILDgroup/conjunction-expressions/4d0be740-6bda-4050-b5e3-e5462d1fec24', 'relative_path': '4d0be740-6bda-4050-b5e3-e5462d1fec24', 'parent_path': '/infra/domains/default/groups/CHILDgroup', 'remote_path': '', 'marked_for_delete': False, 'overridden': False, '_protection': 'NOT_PROTECTED'}, {'ip_addresses': ['66.66.66.66/32'], 'resource_type': 'IPAddressExpression', 'id': 'cc625a51-fe45-4d20-8d3d-e86390336d37', 'path': '/infra/domains/default/groups/CHILDgroup/ip-address-expressions/cc625a51-fe45-4d20-8d3d-e86390336d37', 'relative_path': 'cc625a51-fe45-4d20-8d3d-e86390336d37', 'parent_path': '/infra/domains/default/groups/CHILDgroup', 'remote_path': '', 'marked_for_delete': False, 'overridden': False, '_protection': 'NOT_PROTECTED'}]",No Tags|
PARENTgroup|N/A|"[{'paths': ['/infra/domains/default/groups/CHILDgroup'], 'resource_type': 'PathExpression', 'id': 'eadbdd88-b7a3-477c-9c12-450f978563b8', 'path': '/infra/domains/default/groups/PARENTgroup/path-expressions/eadbdd88-b7a3-477c-9c12-450f978563b8', 'relative_path': 'eadbdd88-b7a3-477c-9c12-450f978563b8', 'parent_path': '/infra/domains/default/groups/PARENTgroup', 'remote_path': '', 'marked_for_delete': False, 'overridden': False, '_protection': 'NOT_PROTECTED'}]",No Tags
