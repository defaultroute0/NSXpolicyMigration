import csv
import requests
from requests.auth import HTTPBasicAuth

# NSX-T Manager details
NSX_MANAGER = 'nsxm.vcnlab01.eng.vmware.com'
USERNAME = 'admin'
PASSWORD = 'XXXX'

# Disable SSL warnings if using self-signed certificates (optional)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# API URL for NSX-T security tags and VMs
tags_url = f"https://{NSX_MANAGER}/policy/api/v1/infra/tags"
vms_url = f"https://{NSX_MANAGER}/api/v1/fabric/virtual-machines"

def get_security_tags():
    print("Connecting to NSX-T Manager...")

    # Make API request to retrieve security tags
    response = requests.get(tags_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)

    if response.status_code == 200:
        print("Successfully connected to NSX-T Manager and retrieved security tags.")
        return response.json()
    else:
        print(f"Failed to retrieve security tags. Status code: {response.status_code}, Response: {response.text}")
        return None

def get_vms():
    """Fetch all VMs and their tags from NSX-T"""
    print("Fetching VM information from NSX-T Manager...")

    response = requests.get(vms_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)

    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Failed to retrieve VMs. Status code: {response.status_code}, Response: {response.text}")
        return []

def find_vms_with_tag(vms, scope, tag_value):
    """Check if VMs have a specific tag and scope."""
    tagged_vms = []
    for vm in vms:
        vm_tags = vm.get('tags', [])
        for tag in vm_tags:
            if tag.get('scope') == scope and tag.get('tag') == tag_value:
                tagged_vms.append({'vm_name': vm.get('display_name', ''), 'vm_id': vm.get('external_id', '')})
    return tagged_vms

def find_vms_without_tags(vms):
    """Find all VMs that don't have any tags applied."""
    vms_without_tags = []
    for vm in vms:
        if not vm.get('tags', []):  # If VM has no tags
            vms_without_tags.append({'vm_name': vm.get('display_name', ''), 'vm_id': vm.get('external_id', '')})
    return vms_without_tags

def write_tags_to_csv(tags_data, vms, csv_file):
    print(f"Writing security tags and associated VMs to CSV file: {csv_file}...")

    # Define strings to exclude in Tag Scope or Tag Value
    filter_strings = ["dis:", "ncp", "vsvip"]

    rows = []

    # Filter out tags that contain any of the filter strings in the scope or tag value
    filtered_tags = [tag for tag in tags_data['results']
                     if not any(exclusion in tag.get('scope', '') for exclusion in filter_strings) and
                     not any(exclusion in tag.get('tag', '') for exclusion in filter_strings)]

    total_filtered_tags = len(filtered_tags)
    print(f"Total tags after filtering: {total_filtered_tags}")

    for index, tag in enumerate(filtered_tags):
        scope = tag.get('scope', '')
        tag_value = tag.get('tag', '')
        description = tag.get('description', '')

        # Find VMs associated with the current tag
        tagged_vms = find_vms_with_tag(vms, scope, tag_value)

        if tagged_vms:
            for vm in tagged_vms:
                rows.append([scope, tag_value, description, vm['vm_name'], vm['vm_id']])
        else:
            # Add tag details without VMs if no VMs are found
            rows.append([scope, tag_value, description, '', ''])

        # Print progress for every 10 tags processed
        if (index + 1) % 10 == 0 or (index + 1) == total_filtered_tags:
            print(f"Processed {index + 1}/{total_filtered_tags} tags.")

    # Now add the VMs without any tags
    vms_without_tags = find_vms_without_tags(vms)
    if vms_without_tags:
        print(f"Found {len(vms_without_tags)} VM(s) without any NSX security tags applied:")
        for vm in vms_without_tags:
            print(f"VM Name: {vm['vm_name']}, VM ID: {vm['vm_id']}")
            # Add VMs without any tags
            rows.append(['', '', '', vm['vm_name'], vm['vm_id']])

    # Sort the rows by the "VM Name" column (index 3)
    rows = sorted(rows, key=lambda x: x[3])

    # Writing the sorted rows to CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write CSV headers
        writer.writerow(['Tag Scope', 'Tag Value', 'Tag Description', 'VM Name', 'VM ID'])
        # Write all sorted rows
        writer.writerows(rows)

    print(f"Security tags and associated VMs have been successfully written to {csv_file}")

def main():
    # Retrieve security tags from NSX-T Manager
    tags_data = get_security_tags()

    # Retrieve VM details from NSX-T Manager
    vms = get_vms()

    if tags_data and vms:
        # CSV file path
        csv_file = 'nsx_security_tags_and_vms.csv'

        # Write tags and associated VMs to CSV file
        write_tags_to_csv(tags_data, vms, csv_file)

if __name__ == "__main__":
    main()
