#!/usr/bin/env -S uv run --script
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

    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        logging.error("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        sys.exit(1)
    org_client = resourcemanager_v3.OrganizationsClient()
    org_search = resourcemanager_v3.SearchOrganizationsRequest()
    org_id = next(iter(org_client.search_organizations(request=org_search), None)).name

    # Initialize logging
    logging.basicConfig(stream=sys.stdout, level=args['logLevel'])

    logging.info(f"Payload: {args['payload']}")
    payload = json.loads(args['payload'])

    client = resourcemanager_v3.ProjectsClient()
    derived_project_id = f'{payload["requestor"].split(" ")[1]}{payload["project_short_name"]}-{payload["request_id"]}'
    target_folder = org_id
    
    cloud_use_case = payload["cloud_use_case"].lower()
    if cloud_use_case == "departmental":
        folders_client = resourcemanager_v3.FoldersClient()
        folder_search = resourcemanager_v3.SearchFoldersRequest(query=f"displayName={payload['brown_department']}")
        folder_response = folders_client.search_folders(request=folder_search)
        target_folder = next(folder_response, None)
        if target_folder is not None:
            target_folder = target_folder.name
        else:
            logging.warning(f"Folder with displayName={payload['brown_department']} not found, using org_id as parent folder")
            target_folder = org_id
  
    project = types.Project(
        display_name=payload['project_name'],
        project_id=derived_project_id,
        parent=target_folder,
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

    if 'jecNamedPipe' in args:
        try:
            with open(args['jecNamedPipe'], 'w', encoding="utf-8") as pipe:
                pipe.write(json.dumps({
                    "project_id": response.project_id,
                    "project_name": response.display_name,
                    "cloud_use_case": cloud_use_case,
                    "parent": target_folder
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
