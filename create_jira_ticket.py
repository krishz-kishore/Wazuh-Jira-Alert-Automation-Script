#!/usr/bin/env python3

import sys
import json
import requests

# Jira project settings
project_key = 'Enter the Jira Key'
issue_type_name = 'Submit a request or incident'
custom_value = "custom_value"  # Your exact customfield value

def create_jira_description(alert_json):
    """Create detailed Jira description in Atlassian Document Format (ADF) with separate tables for each section and a bold, large heading for the title."""
    def heading(text, level=2):
        return {
            "type": "heading",
            "attrs": {"level": level},
            "content": [{"type": "text", "text": text}]
        }

    def table_row(cells):
        return {
            "type": "tableRow",
            "content": [
                {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": str(cell)}]}]} for cell in cells
            ]
        }

    def make_table(rows):
        return {
            "type": "table",
            "content": rows
        }

    content = []

    # Title as bold, large heading (Heading 2)
    summary = alert_json.get('rule', {}).get('description', 'SIEM Alert')
    content.append(heading(f"SIEM Alert: {summary}", 2))

    # Alert Details Table
    alert_details = [
        ("Rule ID", alert_json.get('rule', {}).get('id', 'N/A')),
        ("Level", alert_json.get('rule', {}).get('level', 'N/A')),
        ("Description", alert_json.get('rule', {}).get('description', 'N/A')),
        ("Timestamp", alert_json.get('timestamp', 'N/A')),
        ("Rule Groups", ', '.join(alert_json.get('rule', {}).get('groups', [])) if 'groups' in alert_json.get('rule', {}) else 'N/A'),
        ("Rule Fired Times", alert_json.get('rule', {}).get('firedtimes', 'N/A')),
        ("Rule Info", alert_json.get('rule', {}).get('info', 'N/A'))
    ]
    rows = [table_row(["Field", "Value"])]
    for field, value in alert_details:
        if value and value != 'N/A':
            rows.append(table_row([field, value]))
    content.append(heading("Alert Details", 3))
    content.append(make_table(rows))

    # Agent Information Table
    agent = alert_json.get('agent', {})
    agent_details = [
        ("Agent Name", agent.get('name', 'N/A')),
        ("Agent ID", agent.get('id', 'N/A')),
        ("Agent IP", agent.get('ip', 'N/A')),
        ("Agent Version", agent.get('version', 'N/A'))
    ]
    rows = [table_row(["Field", "Value"])]
    for field, value in agent_details:
        if value and value != 'N/A':
            rows.append(table_row([field, value]))
    content.append(heading("Agent Information", 3))
    content.append(make_table(rows))

    # Manager Information Table
    if 'manager' in alert_json:
        manager = alert_json['manager']
        manager_details = [("Manager Name", manager.get('name', 'N/A'))]
        rows = [table_row(["Field", "Value"])]
        for field, value in manager_details:
            if value and value != 'N/A':
                rows.append(table_row([field, value]))
        content.append(heading("Manager Information", 3))
        content.append(make_table(rows))

    # Source/Destination Information Table
    src_dst_details = []
    if 'srcip' in alert_json:
        src_dst_details.append(("Source IP", alert_json.get('srcip', 'N/A')))
    if 'srcport' in alert_json:
        src_dst_details.append(("Source Port", alert_json.get('srcport', 'N/A')))
    if 'dstip' in alert_json:
        src_dst_details.append(("Destination IP", alert_json.get('dstip', 'N/A')))
    if 'dstport' in alert_json:
        src_dst_details.append(("Destination Port", alert_json.get('dstport', 'N/A')))
    if src_dst_details:
        rows = [table_row(["Field", "Value"])]
        for field, value in src_dst_details:
            if value and value != 'N/A':
                rows.append(table_row([field, value]))
        content.append(heading("Source/Destination Information", 3))
        content.append(make_table(rows))

    # Event Data Table
    if 'data' in alert_json:
        event_items = alert_json['data'].items()
        rows = [table_row(["Field", "Value"])]
        for key, value in event_items:
            if value:
                rows.append(table_row([key, value]))
        content.append(heading("Event Data", 3))
        content.append(make_table(rows))

    # Tags Table
    if 'tags' in alert_json:
        tags = ', '.join(alert_json['tags'])
        rows = [table_row(["Field", "Value"]), table_row(["Tags", tags])]
        content.append(heading("Tags", 3))
        content.append(make_table(rows))

    # Full Log Table
    if 'full_log' in alert_json:
        rows = [table_row(["Field", "Value"]), table_row(["Full Log", str(alert_json['full_log'])])]
        content.append(heading("Full Log", 3))
        content.append(make_table(rows))

    # Location Table
    if 'location' in alert_json:
        rows = [table_row(["Field", "Value"]), table_row(["Location", str(alert_json['location'])])]
        content.append(heading("Location", 3))
        content.append(make_table(rows))

    # Additional Context Table
    analyst_fields = []
    if 'user' in alert_json:
        analyst_fields.append(("User", alert_json['user']))
    if 'process' in alert_json:
        analyst_fields.append(("Process", alert_json['process']))
    if 'file' in alert_json:
        analyst_fields.append(("File", alert_json['file']))
    if 'url' in alert_json:
        analyst_fields.append(("URL", alert_json['url']))
    if analyst_fields:
        rows = [table_row(["Field", "Value"])]
        for field, value in analyst_fields:
            if value:
                rows.append(table_row([field, value]))
        content.append(heading("Additional Context", 3))
        content.append(make_table(rows))

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
