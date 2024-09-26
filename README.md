# NSX Policy Migration Scripts

These files are base script examples to be able to move VM's to a blank/new NSX Manager environment. They dont move the VM's themselves, but rather store NSX security tag(s) to VM infomation in a CSV, then allow you to play that back at the new environment, applying the tags if the VM name matches

# Files

Use these in order to extract tag , vm name and vm-id. 
Replace NSX-T Manager details to suit. 
Tested against NSX-T API 4.1.2 and python 3.11

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

## Example csv 

| Tag Scope | Tag Value | Tag Descr | VM Name | VM ID |
|--|--|--|--|--|
| security | high888 |  | Kali | 503e0c93-840c-1a9e-f6b3-57a78210a55b |
| security | high999 |  | Kali | 503e0c93-840c-1a9e-f6b3-57a78210a55b |
| env | prod |  | ubuntu01 | 503e8ea4-d5f5-f667-b703-03bc3aa6a2c6 |

