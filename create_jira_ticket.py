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
    content.append(paragraph(f"- Rule ID: {alert_json['rule'].get('id', 'N/A')}"))
    content.append(paragraph(f"- Level: {alert_json['rule'].get('level', 'N/A')}"))
    content.append(paragraph(f"- Description: {alert_json['rule'].get('description', 'N/A')}"))
    content.append(paragraph(f"- Timestamp: {alert_json.get('timestamp', 'N/A')}"))
    content.append(paragraph(f"- Rule Groups: {', '.join(alert_json['rule'].get('groups', [])) if 'groups' in alert_json['rule'] else 'N/A'}"))
    content.append(paragraph(f"- Rule Fired Times: {alert_json['rule'].get('firedtimes', 'N/A')}"))
    content.append(paragraph(f"- Rule Info: {alert_json['rule'].get('info', 'N/A')}"))

    # Agent Information
    content.append(paragraph("\n*Agent Information:*"))
    content.append(paragraph(f"- Agent Name: {alert_json['agent'].get('name', 'N/A')}"))
    content.append(paragraph(f"- Agent ID: {alert_json['agent'].get('id', 'N/A')}"))
    content.append(paragraph(f"- Agent IP: {alert_json['agent'].get('ip', 'N/A')}"))
    content.append(paragraph(f"- Agent Version: {alert_json['agent'].get('version', 'N/A')}"))

    # Manager Information
    if 'manager' in alert_json:
        content.append(paragraph("\n*Manager Information:*"))
        content.append(paragraph(f"- Manager Name: {alert_json['manager'].get('name', 'N/A')}"))

    # Source Information
    if 'srcip' in alert_json:
        content.append(paragraph(f"- Source IP: {alert_json.get('srcip', 'N/A')}"))
    if 'srcport' in alert_json:
        content.append(paragraph(f"- Source Port: {alert_json.get('srcport', 'N/A')}"))
    if 'dstip' in alert_json:
        content.append(paragraph(f"- Destination IP: {alert_json.get('dstip', 'N/A')}"))
    if 'dstport' in alert_json:
        content.append(paragraph(f"- Destination Port: {alert_json.get('dstport', 'N/A')}"))

    # Event Data
    if 'data' in alert_json:
        content.append(paragraph("\n*Event Data:*"))
        for key, value in alert_json['data'].items():
            content.append(paragraph(f"- {key}: {value}"))

    # Tags
    if 'tags' in alert_json:
        content.append(paragraph(f"\n*Tags:* {', '.join(alert_json['tags'])}"))

    # Optional fields
    if 'full_log' in alert_json:
        content.append(paragraph("\n*Full Log:*"))
        content.append(paragraph(str(alert_json['full_log'])))

    if 'location' in alert_json:
        content.append(paragraph(f"\n*Location:* {alert_json['location']}"))

    # Additional context for analysts
    if 'user' in alert_json:
        content.append(paragraph(f"\n*User:* {alert_json['user']}"))
    if 'process' in alert_json:
        content.append(paragraph(f"\n*Process:* {alert_json['process']}"))
    if 'file' in alert_json:
        content.append(paragraph(f"\n*File:* {alert_json['file']}"))
    if 'url' in alert_json:
        content.append(paragraph(f"\n*URL:* {alert_json['url']}"))

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
