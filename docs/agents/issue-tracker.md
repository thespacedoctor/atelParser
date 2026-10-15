# Issue tracker: Linear

This repo keeps its issues and specs in Linear, in team **thespacedoctor** and project **atelParser**. Use the Linear MCP tools for all issue operations.

## Conventions

- **Create an issue**: `create_issue` with `team: thespacedoctor`, `project: atelParser`, a title, a Markdown description, and the status `Triage`, unless the skill says a different state.
- **Read an issue**: `get_issue` with the identifier (for example `ENG-123`), then `list_comments` for the conversation. Read the status and labels from the issue.
- **List issues**: `list_issues` with `project: atelParser`. Filter by `state` for triage states and by `label` for categories.
- **Comment on an issue**: `create_comment` with the issue ID and a Markdown body.
- **Set a triage state**: `update_issue` with `state: <status name>`. Triage states are Linear statuses, never labels. See `triage-labels.md`.
- **Apply or remove labels**: `update_issue` with the full label list. Use labels only for categories (`bug`, `enhancement`) and `wayfinder:*`.
- **Close**: post the reason with `create_comment`, then set the status to `wontfix` (rejected) or `Done` (implemented).

## Pull requests

Put the Linear issue ID in the branch name (for example `feature/ENG-123-short-name`) and in the PR title or body, so Linear links the PR to the issue.

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests. `/triage` reads this flag.)_

When set to `yes`, triage external PRs with the `gh pr` commands. Record their triage state on a Linear issue that links to the PR.

## When a skill says "publish to the issue tracker"

Create a Linear issue in project **atelParser**.

## When a skill says "fetch the relevant ticket"

Run `get_issue` with the identifier, then `list_comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a parent issue, and each ticket is a **child** sub-issue.

- **Map**: a single issue with the label `wayfinder:map`. Its description holds the Notes, Decisions so far, and Fog sections.
- **Child ticket**: a sub-issue of the map (set `parentId` to the map's ID), with the label `wayfinder:<type>` (`research`, `prototype`, `grilling`, or `task`). After a ticket is claimed, it is assigned to the driving developer.
- **Blocking**: use Linear's native "blocked by" relation. A ticket is unblocked when every blocking issue is `Done` or `wontfix`.
- **Frontier query**: list the map's open children, then drop any that have an open blocker or an assignee. The first child in map order wins.
- **Claim**: `update_issue` with `assignee: me` and `state: In Progress`. This is the session's first write.
- **Resolve**: `create_comment` with the answer, set the status to `Done`, then add a context pointer (gist and link) to the map's Decisions so far.
