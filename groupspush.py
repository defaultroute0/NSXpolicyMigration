import csv
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

# NSX-T Manager details
NSX_MANAGER = 'nsxm.vcnlab01.eng.vmware.com'
USERNAME = 'admin'
PASSWORD = 'VMware1!2229'

# Disable SSL warnings if using self-signed certificates (optional)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Set the correct domain (change 'default' if necessary)
base_url = f"https://{NSX_MANAGER}/policy/api/v1/infra/domains/default/groups"


def get_existing_groups():
    """Fetch all existing groups in NSX Manager."""
    print("Fetching all existing groups from NSX Manager...")
    response = requests.get(base_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)

    if response.status_code == 200:
        groups = response.json().get('results', [])
        existing_groups = {group.get('display_name'): group for group in groups}
        print(f"Retrieved {len(existing_groups)} existing groups from NSX Manager.")
        return existing_groups
    else:
        print(f"Error fetching groups from NSX Manager. Status Code: {response.status_code}, Response: {response.text}")
        return {}


def patch_group(group_name, description, members):
    """Update or create a group using PATCH in NSX Manager."""
    # Replace spaces with underscores in the group name for group_id
    group_id = group_name.replace(" ", "_")

    # URL-encode the group ID for the request URL
    group_url = f"{base_url}/{quote(group_id)}"

    # Construct the payload with expressions and description
    group_data = {
        "description": description,
        "display_name": group_name,  # The display_name can still have spaces
        "expression": members,  # Assuming members are passed in the correct structure
        "_revision": 0
    }

    print(f"Attempting to create or update group: {group_name} using PATCH method...")
    response = requests.patch(group_url, json=group_data, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)

    if response.status_code == 200 or response.status_code == 201:
        print(f"Successfully created or updated group: {group_name}")
        return True
    else:
        # Adding debugging information for failed requests
        print(
            f"Failed to create or update group: {group_name}. Status Code: {response.status_code}, Response: {response.text}")
        print(f"Request Payload: {group_data}")
        return False


def process_csv_and_create_groups(csv_file, existing_groups):
    """Process the CSV and create or update groups in NSX Manager."""
    created_groups = []
    skipped_groups = []

    # Open the CSV file and process each row
    print(f"Reading groups from CSV file '{csv_file}'...")
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            group_name = row['Group Name']
            description = row['Description']
            members = row['Members']
            tags = row['Tags']

            # Convert members back into the expected expression format for the API request
            members_expression = []
            if members != 'No Members Defined':
                # Assuming members_expression is passed correctly, modify as needed
                members_expression = eval(members)  # Convert string back to Python object

            # Check if the group already exists in the fetched list
            if group_name in existing_groups:
                skipped_groups.append(group_name)
            else:
                # Create or update the group using PATCH
                if patch_group(group_name, description, members_expression):
                    created_groups.append(group_name)

    return created_groups, skipped_groups


def main():
    # Path to the CSV file containing group data
    csv_file = 'nsx_security_policy_groups.csv'

    print(
        f"Starting the process of reading group data from CSV file: {csv_file} and creating groups in NSX Manager...\n")

    # Fetch all existing groups in one call
    existing_groups = get_existing_groups()

    # Process the CSV and create or update groups
    created_groups, skipped_groups = process_csv_and_create_groups(csv_file, existing_groups)

    # Display summary
    print("\nSummary:")
    print(f"Total groups in CSV: {len(created_groups) + len(skipped_groups)}")
    print(f"Groups created or updated: {len(created_groups)}")
    if created_groups:
        print(f"Created or updated groups: {', '.join(created_groups)}")
    print(f"Groups skipped (already exist): {len(skipped_groups)}")
    if skipped_groups:
        print(f"Skipped groups: {', '.join(skipped_groups)}")

    print("\nProcess completed. All groups have been processed.")


if __name__ == "__main__":
    main()
