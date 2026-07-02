# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-cloud-resource-manager",
# ]
# ///

import argparse
import json
import sys
import logging
import os
from google.cloud import resourcemanager_v3
from google.cloud.resourcemanager_v3 import types


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

    print(f"Received payload: {args['payload']}")
    print(f"Received namedPipe: {args['jecNamedPipe']}")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    gcp_creds = json.loads(open(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')).read())
    
    print(f"GCP Credentials: {gcp_creds}")
    client = resourcemanager_v3.ProjectsClient()
    print(f"Resource Manager client initialized: {client}")
    if 'jecNamedPipe' in args:
        payload = json.loads(args['payload'])
        try:
            with open(args['jecNamedPipe'], 'w', encoding="utf-8") as pipe:
                pipe.write(json.dumps(payload))
                print("Payload written to named pipe successfully.")
                #logging.info(f"Message written to named pipe at {args['jecNamedPipe']}")
        except Exception as e:
            print(f"Error writing to named pipe {args['jecNamedPipe']} with exception: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
