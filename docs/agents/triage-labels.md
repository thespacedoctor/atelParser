# Triage states and labels

The skills use five canonical triage state roles and two category roles. In this repo, the state roles are Linear workflow statuses in team **thespacedoctor**, and the category roles are Linear labels.

## State roles are Linear statuses

| Role in mattpocock/skills | Linear status | Linear type | Meaning |
| --- | --- | --- | --- |
| `needs-triage` | `Triage` | triage | Maintainer needs to evaluate this issue |
| `needs-info` | `needs-info` | backlog | Waiting on the reporter for more information |
| `ready-for-agent` | `ready-for-agent` | unstarted | Fully specified, ready for an AFK agent |
| `ready-for-human` | `ready-for-dave` | unstarted | Needs Dave to implement |
| `wontfix` | `wontfix` | canceled | Will not be actioned |

When a skill says "apply the `<role>` label" for a state role, set the Linear status with `update_issue` (`state: <status>`). Do not add a label. An issue has one status only, so setting a new state replaces the old one.

The team also has two statuses that are not triage roles:

- `In Progress` (started): someone has claimed the work.
- `Done` (completed): the work is merged. Set it when the linked PR merges.

## Category roles are labels

| Role in mattpocock/skills | Linear label | Meaning |
| --- | --- | --- |
| `bug` | `bug` | Something is broken |
| `enhancement` | `enhancement` | New feature or improvement |

Every triaged issue has exactly one category label. Other labels, such as `wayfinder:*`, stay as labels.
