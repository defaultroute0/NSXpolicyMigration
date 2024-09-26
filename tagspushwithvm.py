import csv
import requests
from requests.auth import HTTPBasicAuth
from collections import defaultdict

# NSX-T Manager details
NSX_MANAGER = 'nsxm.vcnlab01.eng.vmware.com'
USERNAME = 'admin'
PASSWORD = 'XXXX'

# Disable SSL warnings if using self-signed certificates (optional)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# API URL to retrieve VMs and apply tags
vms_url = f"https://{NSX_MANAGER}/api/v1/fabric/virtual-machines"
tagging_url_template = f"https://{NSX_MANAGER}/policy/api/v1/infra/realized-state/virtual-machines/{{vm_id}}/tags"

# Tags or tag values to exclude from applying (case-sensitive, exact match)
exclude_tags = ["admin:", "ncp", "vsvip", "ariaauto01"]


def get_vms():
    """Fetch all VMs from NSX-T Manager"""
    print("Fetching all VMs from NSX-T Manager...")

    response = requests.get(vms_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)

    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Failed to retrieve VMs. Status code: {response.status_code}, Response: {response.text}")
        return []


def find_vm_by_name(vms, vm_name):
    """Find VM by name from the list of VMs."""
    for vm in vms:
        if vm.get('display_name') == vm_name:
            return vm
    return None


def apply_tags_to_vm(vm_id, vm_name, tags):
    """Apply tags to the VM using POST"""
    url = tagging_url_template.format(vm_id=vm_id)
    print(f"Applying tags to VM '{vm_name}' (ID: {vm_id})")  # Debug: Print VM Name and ID

    # Display all tags being applied to this VM
    for tag in tags:
        print(f"Tag - Scope: {tag['scope']}, Tag: {tag['tag']}")

    response = requests.post(url, json={"tags": tags}, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)

    # Log the request URL and status
    print(f"Request URL: {url}")
    print(f"Response Status Code: {response.status_code}")

    if response.status_code == 204:
        print(f"Successfully applied tags to VM '{vm_name}' (ID: {vm_id}).")
        print(f"")
    else:
        print(
            f"Failed to apply tags to VM '{vm_name}' (ID: {vm_id}). Status code: {response.status_code}, Response: {response.text}")


def should_exclude_tag(tag_scope, tag_value):
    """Check if the tag scope or tag value matches any of the excluded strings (case-sensitive, exact match)."""
    return tag_scope in exclude_tags or tag_value in exclude_tags


def process_csv_and_apply_tags(csv_file):
    """Process the CSV and apply tags to the VMs based on VM name."""
    # Retrieve all VMs from NSX-T Manager
    vms = get_vms()

    if not vms:
        print("No VMs retrieved. Exiting.")
        return

    # Dictionary to accumulate tags for each VM
    vm_tags = defaultdict(list)

    # Open the CSV and process each row
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            tag_scope = row['Tag Scope']
            tag_value = row['Tag Value']
            vm_name = row['VM Name']

            # Exclude tags if the scope or value exactly matches any of the excluded strings
            if should_exclude_tag(tag_scope, tag_value):
                print(f"Excluding tag with scope: {tag_scope}, value: {tag_value} for VM: {vm_name}")
                continue

            # Find the VM by name
            vm = find_vm_by_name(vms, vm_name)

            if vm:
                vm_id = vm.get('external_id')
                new_tag = {
                    "scope": tag_scope,
                    "tag": tag_value
                }

                # Accumulate tags for each VM
                vm_tags[(vm_name, vm_id)].append(new_tag)
            else:
                print(f"VM '{vm_name}' not found. Skipping.")

    # Now apply tags in one API call per VM
    for (vm_name, vm_id), tags in vm_tags.items():
        apply_tags_to_vm(vm_id, vm_name, tags)


def main():
    # Path to the CSV file
    csv_file = 'nsx_security_tags_and_vms.csv'

    # Process the CSV and apply tags to VMs
    process_csv_and_apply_tags(csv_file)


if __name__ == "__main__":
    main()
