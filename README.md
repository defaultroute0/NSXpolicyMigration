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

## Example csv for tags pull/push 

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
