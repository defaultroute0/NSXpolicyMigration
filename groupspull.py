import csv
import requests
from requests.auth import HTTPBasicAuth

# NSX-T Manager details
NSX_MANAGER = 'nsxm.vcnlab01.eng.vmware.com'
USERNAME = 'admin'
PASSWORD = 'XXXX'

# Disable SSL warnings if using self-signed certificates (optional)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# API URL to retrieve NSX Security Policy Groups
groups_url = f"https://{NSX_MANAGER}/policy/api/v1/infra/domains/default/groups"

# Array of partial strings to exclude certain NSX Security Groups by name (case insensitive)
exclude_group_strings = ["exclude", "NSGroup"]  # Example partial strings to exclude


def get_nsx_security_groups():
    """Fetch all NSX Security Policy Groups from NSX-T Manager"""
    print("Fetching NSX Security Policy Groups from NSX-T Manager...")

    response = requests.get(groups_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)

    if response.status_code == 200:
        print("Successfully retrieved security policy groups.")
        return response.json().get('results', [])
    else:
        print(f"Failed to retrieve groups. Status code: {response.status_code}, Response: {response.text}")
        return []


def should_exclude_group(group_name):
    """Check if the group name contains any of the exclude strings."""
    for exclude_string in exclude_group_strings:
        if exclude_string.lower() in group_name.lower():
            return True
    return False


def process_groups_and_store_in_csv(groups, csv_file):
    """Process the group information and store it in a CSV."""
    if not groups:
        print("No groups to process.")
        return

    # Open the CSV file for writing
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the CSV headers
        writer.writerow(['Group Name', 'Description', 'Members', 'Tags'])

        # Initialize group counter for progress tracking
        total_groups = len(groups)
        processed_groups = 0
        excluded_groups = 0
        print(f"Processing {total_groups} groups...")

        # Process each group
        for index, group in enumerate(groups, start=1):
            group_name = group.get('display_name', 'N/A')

            # Check if the group name contains any exclude string
            if should_exclude_group(group_name):
                print(f"Excluding group: {group_name} (matched exclude criteria)")
                excluded_groups += 1
                continue

            # Process the group if not excluded
            description = group.get('description', 'N/A')
            members = group.get('expression', 'N/A')
            tags = group.get('tags', [])

            # Prepare members and tags information for CSV output
            members_str = str(members) if members != 'N/A' else 'No Members Defined'
            tags_str = ', '.join([f"{tag['scope']}: {tag['tag']}" for tag in tags]) if tags else 'No Tags'

            # Write group information to CSV
            writer.writerow([group_name, description, members_str, tags_str])
            processed_groups += 1

            # Display progress message every 5 groups processed
            if processed_groups % 5 == 0 or index == total_groups:
                print(f"Processed {processed_groups}/{total_groups} groups.")

    print(f"Processing complete: {processed_groups} groups processed, {excluded_groups} groups excluded.")
    print(f"CSV file '{csv_file}' created successfully.")


def main():
    # Retrieve NSX Security Policy Groups from NSX-T Manager
    print("Starting the process to retrieve NSX Security Policy Groups...")
    groups = get_nsx_security_groups()

    if groups:
        # Path to the output CSV file
        csv_file = 'nsx_security_policy_groups.csv'

        print(f"Storing the group information into CSV file: {csv_file}")
        # Process the groups and store them in CSV
        process_groups_and_store_in_csv(groups, csv_file)
    else:
        print("No groups retrieved. Exiting.")


if __name__ == "__main__":
    main()
