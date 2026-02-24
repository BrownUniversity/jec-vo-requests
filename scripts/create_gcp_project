# /// script
# requires-python = ">=3.9"
# dependencies = ["google-cloud-resource-manager>=1.14.2"]
# ///

import argparse
import json
import sys
import logging
import os
import random
import string
import requests
import datetime
from google.cloud import resourcemanager_v3
from google.cloud.resourcemanager_v3 import types
#from bcs_functions import create_bcs_api_token, get_bcs_department_id, create_bcs_token, add_bcs_project, add_bcs_project_budget, get_bcs_project_budgets
def create_bcs_api_token(username, password):
    """
    Creates a BCS API token using the provided username and password.
    """
    try:
        response = requests.post('https://api.bcs.burwood.com/token', auth=(username, password), verify=False)
    except Exception as e:
        logging.error(f"Error creating BCS API token: {e}")
    return response.json().get('token')

def get_bcs_department_id(token, group_name, department_name):
    """
    Retrieves the BCS department ID based on the provided department name.
    """
    auth_header = {'x-access-token': token}
    try:
        group_hierarchy = requests.get('https://api.bcs.burwood.com/api/group_hierarchy', 
                                       headers=auth_header).json()
    except Exception as e:
        logging.error(f"Error retrieving BCS group hierarchy: {e}")
        return None
    for group in group_hierarchy:
        if group['groupname'] == group_name:
            for department in group.get('departments', []):
                if department['departmentname'] == department_name:
                    return department['departmentid']
    return None

def get_bcs_project_budgets(token, project_id):
    """
    Retrieves the budgets associated with a BCS project.
    """
    auth_header = {'x-access-token': token}
    try:
        budgets = requests.get(f'https://api.bcs.burwood.com/api/project/{project_id}', 
                               headers=auth_header).json()
    except Exception as e:
        logging.error(f"Error retrieving BCS project budgets: {e}")
        return None
    return budgets

def add_bcs_project_budget(token, project_id, **kwargs):
    """
    Adds a budget to a BCS project.
    """
    auth_header = {'x-access-token': token}
    add_budget_schema = {
        "ponumber": kwargs.get("ponumber", None),
        "grant": kwargs.get("grant", None),
        "amount": kwargs.get("amount", 1),
        "billingaccountid": kwargs.get("billingaccountid", None),
        "expirationdate": kwargs.get("expirationdate", None),
        "recurring": kwargs.get("recurring", False),
        "state": kwargs.get("state", "Active")
        }
    try:
        response = requests.post(f'https://api.bcs.burwood.com/api/project/{project_id}/add_budget', 
                                 headers=auth_header, json=add_budget_schema)
    except Exception as e:
        logging.error(f"Error adding budget to BCS project: {e}")
        return None
    return response.json()

def add_bcs_project(token, project_id, **kwargs):
    """
    Adds a new project to BCS.
    """
    auth_header = {'x-access-token': token}
    add_project_schema = {
        "departmentid": kwargs.get("departmentid", None),
        "primarycontactemail": kwargs.get("primarycontactemail", None),
        "billingcontactemail": kwargs.get("billingcontactemail", None),
        "aftercredits": kwargs.get("aftercredits", "Suspend"),
        "aftercreditsaccount": kwargs.get("aftercreditsaccount", None),
        "aftercreditspo": kwargs.get("aftercreditspo", None),
        "recurringbudget": kwargs.get("recurringbudget", False),
        "paidbillingaccount": kwargs.get("paidbillingaccount", None),
        "projectname": kwargs.get("projectname", None),
        }
    try:
        response = requests.post(f'https://api.bcs.burwood.com/api/project/{project_id}', 
                                 headers=auth_header, json=add_project_schema)
    except Exception as e:
        logging.error(f"Error adding BCS project: {e}")
        return None
    return response.json()

def main():
    # Initialize argument parser and dictionary-ize arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-payload', help='Payload from queue', required=True)
    parser.add_argument('-apiKey', help='The apiKey of the integration', required=True)
    parser.add_argument('-jsmUrl', help='The url', required=True)
    parser.add_argument('-logLevel', help='Level of log', required=True)
    parser.add_argument('--jecNamedPipe', help='Path of a pipe object you can use to send data back to the caller', required=False)
    args, unknown = parser.parse_known_args()
    args = vars(args)

    gcp_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    bcs_username = os.environ.get('BCS_USERNAME')
    bcs_password = os.environ.get('BCS_PASSWORD')
    bcs_token = os.environ.get('BCS_TOKEN')
            
    if bcs_username and bcs_password:
        bcs_token = create_bcs_api_token(bcs_username, bcs_password)

    # Initialize logging
    logging.basicConfig(stream=sys.stdout, level=args['logLevel'])

    logging.info(f"Payload: {args['payload']}")
    payload = json.loads(args['payload'])

    client = resourcemanager_v3.ProjectsClient()
    derived_project_id = f'{payload["cloud_use_case"]}{payload["requestor"].split(" ")[1]}-{payload["request_id"]}'
    project = types.Project(
        display_name=payload['project_name'],
        project_id=derived_project_id,
        parent=payload['parent_id'],
        labels={
            "created_by": "jec-vo-team",
            "request_id": payload['request_id'].lower(),
            "requestor": payload["requestor"].lower().replace(" ","_")
        }
    )
    # The creation request returns a long-running operation
    operation = client.create_project(project=project)
    print(f"Waiting for project creation operation: {operation.operation.name}")

    try:
        # Wait for the operation to complete
        response = operation.result()
        logging.info(f"Created project: {response.display_name} (ID: {response.project_id})")
    except Exception as e:
        print(f"Failed to create project: {e}")

    group_name_lookup = {
        'CCV': ('CCV Research Pilots','Unaffiliated CCV Research Pilots'),
        'OIT': ('Brown University','Unaffiliated Projects'),
        'Computer Science': ('Computer Science','Unaffiliated Computer Science')
    }
    group_name = group_name_lookup.get(payload['group_name'])[0]
    department_name = group_name_lookup.get(payload['group_name'])[1]

    try:
        department_id = get_bcs_department_id(bcs_token, group_name, department_name)
        add_bcs_project(token=bcs_token, project_id=response.project_id,
                        department_id=department_id)
        budget = add_bcs_project_budget(token=bcs_token, project_id=response.project_id,
                    amount=1, billingaccountid=payload['billing_account_id'],
                    expirationdate="2026-02-18",
                    ponumber=payload['po_number'],
                    recurring=False, state="Active")
    except Exception as e:
        logging.error(f"Error adding project to BCS: {e}")

    if 'jecNamedPipe' in args:
        try:
            with open(args['jecNamedPipe'], 'w', encoding="utf-8") as pipe:
                pipe.write(json.dumps({
                    "project_id": response.project_id,
                    "project_name": response.display_name,
                    "department_name": department_name,
                    "budget": budget
                    }))
                logging.info(f"Message written to named pipe at {args['jecNamedPipe']}")
        except Exception as e:
            logging.error(f"Error writing to named pipe {args['jecNamedPipe']} with exception: {e}")
            sys.exit(1)

def generate_random_string(length):
    """
    Generates a random alphanumeric string of a specified length.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string

if __name__ == "__main__":
    main()
