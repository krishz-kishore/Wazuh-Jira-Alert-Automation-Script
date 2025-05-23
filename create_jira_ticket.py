#!/usr/bin/env python3

import sys
import json
import requests

# Jira project settings
project_key = 'Enter the Jira Key'
issue_type_name = 'Submit a request or incident'
custom_value = "custom_value"  # Your exact customfield value

def create_jira_description(alert_json):
    """Create detailed Jira description in Atlassian Document Format (ADF) from alert data."""
    content = []

    def paragraph(text):
        return {
            "type": "paragraph",
            "content": [{"type": "text", "text": text}]
        }

    # Alert Details section
    content.append(paragraph("*Alert Details:*"))
    content.append(paragraph(f"- Rule ID: {alert_json['rule']['id']}"))
    content.append(paragraph(f"- Level: {alert_json['rule']['level']}"))
    content.append(paragraph(f"- Description: {alert_json['rule']['description']}"))
    content.append(paragraph(f"- Timestamp: {alert_json['timestamp']}"))

    # Agent Information
    content.append(paragraph("\n*Agent Information:*"))
    content.append(paragraph(f"- Agent Name: {alert_json['agent']['name']}"))
    content.append(paragraph(f"- Agent ID: {alert_json['agent']['id']}"))

    # Optional fields
    if 'full_log' in alert_json:
        content.append(paragraph("\n*Full Log:*"))
        content.append(paragraph(alert_json['full_log']))

    if 'location' in alert_json:
        content.append(paragraph(f"\n*Location:* {alert_json['location']}"))

    # Return Atlassian Document format
    return {
        "type": "doc",
        "version": 1,
        "content": content
    }

def main():
    if len(sys.argv) < 2:
        print("Error: Alert JSON file argument missing")
        sys.exit(1)

    # Load alert JSON from file passed as argument
    alert_file_path = sys.argv[1]
    with open(alert_file_path, 'r') as f:
        alert_json = json.load(f)

    # Jira auth and endpoint
    jira_user = "***"  # Replace with your Jira email
    jira_api_token = "*****"    # Replace with your API token
    jira_url = "https://***.atlassian.net/rest/api/3/issue"

    # Build request payload with your required fields
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": f"SIEM Alert: {alert_json['rule']['description']}",
            "description": create_jira_description(alert_json),
            "issuetype": {"name": issue_type_name},
            "customfield_***": [   # custom name as array of objects
                {"value": custom_value}
            ],
            "assignee": {"id": "*****"},
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Make POST request to Jira API
    response = requests.post(
        jira_url,
        auth=(jira_user, jira_api_token),
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code in (200, 201):
        print(f"Successfully created Jira issue: {response.json().get('key')}")
        sys.exit(0)
    else:
        print(f"Failed to create Jira issue. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
