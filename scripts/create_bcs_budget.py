import argparse
import json
import sys
import logging
import os
import random
import string
import requests

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
    bcs_username = os.environ.get('BCS_USERNAME')
    bcs_password = os.environ.get('BCS_PASSWORD')
    bcs_token = os.environ.get('BCS_TOKEN')
    if bcs_username and bcs_password:
        bcs_token = create_bcs_api_token(bcs_username, bcs_password)
    
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
        logging.error(f"Error adding project or budget to BCS: {e}")
