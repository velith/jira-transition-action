import json
import logging
import os
import re
import requests

API_TOKEN       = "TOKEN"
PROJECT         = "JIRA_PROJECT_KEY"
HOSTNAME        = "JIRA_HOSTNAME"
TRANSITION_ID   = "JIRA_TRANSITION_ID"
VERSION         = "JIRA_VERSION"
BRANCH          = "GITHUB_BRANCH"
GITHUB_REF      = "GITHUB_REF"

def _check_env_vars(vars):
  for var in vars:
    if not os.environ.get(var):
      logging.exception(f"Required env var '{var}' not set")
      exit(1)

def _extract_issue_id(branch, project_key):
  id = ""
  issue_pattern = "^(?!sentry).*((%s-)?[0-9]{4}).*"%(project_key.lower())
  result = re.match(issue_pattern, branch.lower()) 

  if result:
    id = result.group(1)
    logging.info(f"Found issue number: {id}")
  else:
    logging.warn(f"Could not extract issue number from '{branch}'")

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

def _set_jira_version(jira_host, headers, issue_id):
  version_name = os.environ.get(VERSION)
  if not version_name:
    return False

  url = f"https://{jira_host}/rest/api/2/issue/{issue_id}"

  payload = json.dumps({
    "fields": {
      "fixVersions": [
        {
          "name": version_name
        }
      ]
    }
  })

  res = requests.put(url,
                  headers=headers,
                  data=payload
                  )

  if res.status_code not in [200, 204]:
    logging.warning(f"Failed to update issue {issue_id} with version {version_name}")
    logging.warning(json.loads(res.text))

  return True

def main(request):
  _check_env_vars([API_TOKEN, PROJECT, HOSTNAME, TRANSITION_ID, GITHUB_REF])

  logging.basicConfig(level=logging.INFO)

  jira_host = os.environ.get(HOSTNAME)
  request_headers = {
    "Authorization": f"Bearer {os.environ.get(API_TOKEN)}",
    "Accept": "application/json",
    "Content-Type": "application/json"
  }

  branch = os.environ.get(BRANCH)
  if not branch:
    branch = os.environ.get(GITHUB_REF)

  issue = _get_jira_issue(jira_host, 
                          request_headers,
                          os.environ.get(PROJECT),
                          branch
                        )

  if issue:
    issue_id = issue["id"]
    transition_id = os.environ.get(TRANSITION_ID)
    _transition_jira_issue(jira_host, request_headers, issue_id, transition_id)
    _set_jira_version(jira_host, request_headers, issue_id)
  else:
    logging.info("No issue found to transition")

if __name__ == "__main__":
    main(None)