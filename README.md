# Jira Transition Action

Github action for transitioning a single issue in Jira. Suiteable to run when a pull request is open to visualize it's corresponding issue is ready for code review.

## Usage

Set the required inputs for the action and token is required to be in the environment:

```yaml
name: 'Jira GitHub Actions'
on:
  pull_request:
    types: [opened]

jobs:
  release:
    name: 'Jira Transition'
    runs-on: ubuntu-latest
    steps:
      - name: 'Checkout'
        uses: actions/checkout@master
        ## Run checks on change...
      - name: 'test'
        ## Place issue in code review column
      - name: 'Jira transition'
        uses: velith/jira-transition-action@v1
        with:
          jira_project_key: "MYPROJ"
          jira_hostname: "jira.example.com"
          jira_transition_id: "71" # The ID is unqiue to your Jira instance for the status
        env:
          TOKEN: ${{ secrets.JIRA_TOKEN }}
```

### How it works

It will take the name of the branch as input to which issue that will perform the transition. The branch name has to contain either the whole ID like `MYPROJ-0001` or just a 4 digit number e.g. `feature/1234_make_something_awesome`. Without the issue number in the branch name, nothing will happen.

## Inputs

Inputs configure Terraform GitHub Actions to perform different actions.

* `jira_project_key` - (Required) Project key in Jira.
* `jira_hostname` - (Required) Hostname of the Jira software.
* `jira_transition_id` - (Required) ID for status to transition Jira issues during release.

## Outputs

There are no outputs of this action.
