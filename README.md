
# 📘 Jira Alert Automation Script

This Python script automatically creates Jira issues from alert JSON files. It converts alert data into the Atlassian Document Format (ADF) to create structured, human-readable Jira tickets.

## 🚀 Features

- Converts SIEM alert JSON into rich-text Jira issue descriptions.
- Authenticates using basic auth with Jira API token.
- Automatically fills in project, issue type, assignee, and custom fields.

## 🛠️ Requirements

- Python 3.x
- `requests` library  
  Install with:  
  ```bash
  pip install requests
  ```

## 📥 Installation

Download the script:

```bash
wget https://your-repo-url/create_jira_ticket.py
chmod +x create_jira_ticket.py
```

> Or directly: [Download create_jira_ticket.py](create_jira_ticket.py)

## ⚙️ Configuration

Edit the script to set your Jira settings:

```python
project_key = 'YOUR_PROJECT_KEY'
issue_type_name = 'Submit a request or incident'
custom_value = "Your_Custom_Field_Value"

jira_user = "your-email@example.com"
jira_api_token = "your-api-token"
jira_url = "https://yourdomain.atlassian.net/rest/api/3/issue"
```

Update the custom field and assignee ID accordingly:

```python
"customfield_XXXXX": [{"value": custom_value}],
"assignee": {"id": "your-user-id"},
```

## 📄 Input Format

Your JSON file must follow this schema:

```json
{
  "rule": {
    "id": "900001",
    "level": 10,
    "description": "Suspicious activity detected"
  },
  "timestamp": "2025-05-22T12:34:56Z",
  "agent": {
    "name": "agent01",
    "id": "001"
  },
  "full_log": "Detailed log text...",
  "location": "/var/log/syslog"
}
```

## 🚀 Usage

```bash
./create_jira_ticket.py alert.json
```

## ✅ Output

On success, it will print:

```
Successfully created Jira issue: ABC-123
```

## ❌ Error Handling

- If the JSON file is missing or malformed, the script exits with an error.
- Jira API response errors are shown in detail.
