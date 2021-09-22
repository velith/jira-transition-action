import json
import logging
import os
import re
import requests

API_TOKEN       = "TOKEN"
PROJECT         = "JIRA_PROJECT_KEY"
HOSTNAME        = "JIRA_HOSTNAME"
TRANSITION_ID   = "JIRA_TRANSITION_ID"
BRANCH          = "GITHUB_REF"

def _check_env_vars(vars):
  for var in vars:
    if not os.environ.get(var):
      logging.exception(f"Required env var '{var}' not set")
      exit(1)

def _extract_issue_id(branch, project_key):
  id = ""
  issue_pattern = f"^(?!sentry).*(({project_key.lower()}-)?[0-9]{4}).*"
  result = re.match(issue_pattern, branch.lower()) 

  if result:
    id = result.group(1)

  return id

def _get_jira_issue(jira_host, headers, project_key, branch):
  issue_id = _extract_issue_id(branch, project_key)
  if not issue_id:
    return ""

  issue_url = f"https://{jira_host}/rest/api/2/issue/{project_key.upper()}-{issue_id}"

  params = {
    "fields": "id"
  }

  resp = requests.get(
    issue_url,
    headers=headers,
    params=params
  )

  if resp.status_code == 200:
    return resp.json()
  else:
    return ""

def _transition_jira_issue(jira_host, headers, issue_id, transition_id): 
  payload = json.dumps({
    "transition": {
      "id": transition_id
    }
  })

  transition_url = f"https://{jira_host}/rest/api/2/issue/{issue_id}/transitions"

  resp = requests.post(
    transition_url,
    headers=headers,
    data=payload
  )

  return resp.status_code == 200

def main(request):
  _check_env_vars([API_TOKEN, PROJECT, HOSTNAME, TRANSITION_ID, BRANCH])

  logging.basicConfig(level=logging.INFO)

  jira_host = os.environ.get(HOSTNAME)
  request_headers = {
    "Authorization": f"Bearer {os.environ.get(API_TOKEN)}",
    "Accept": "application/json",
    "Content-Type": "application/json"
  }

  issue = _get_jira_issue(jira_host, 
                          request_headers,
                          os.environ.get(PROJECT),
                          os.environ.get(BRANCH)
                        )

  if issue:
    issue_id = issue["id"]
    transition_id = os.environ.get(TRANSITION_ID)
    if _transition_jira_issue(jira_host, request_headers, issue_id, transition_id) != 200:
      logging.warn("Transition ID not found, ticket not moved")
  else:
    logging.info("No issue found to transition")

if __name__ == "__main__":
    main(None)