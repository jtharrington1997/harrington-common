# Direct GitHub Changes with ChatGPT Connectors - Template

This document captures the workflow used in the March 27, 2026 `harrington-pax-americana` session as a reusable template for making direct GitHub changes with ChatGPT when GitHub connectors are enabled.

## Purpose

Use this workflow when you want ChatGPT to:
- inspect a repository through the GitHub connector
- propose or directly implement changes
- create commits without using your local shell
- optionally open a PR
- optionally merge the connector-driven changes back into `main`

This is most useful when:
- the repo is public or connector-accessible
- the task is documentation, UI, refactor, or configuration work
- you want an auditable repo-level artifact of the session

---

## What happened in the reference session

The reference conversation followed this pattern:

1. Inspect the target repo and its current files.
2. Review the current implementation before editing.
3. Create a working branch from the relevant base commit.
4. Add or replace files by creating blobs and trees through the connector.
5. Create connector-side commits.
6. Update the working branch reference.
7. Open a draft PR for review.
8. Continue polishing on the branch.
9. Apply the finalized tree onto the current `main` tip.
10. Update `main` so the repo returns to a single canonical branch state.

Important: this is a connector-side GitHub workflow. It is not the same thing as running local `git` commands on the desktop. It can change repository state directly, but it does not by itself prove that the code was run locally or passed runtime validation.

---

## Recommended prompting pattern

Use a prompt with four parts:

### 1. State the repo and desired result
Example:
> Work on `jtharrington1997/harrington-pax-americana`. I want the private theory workspace hidden behind admin and I want multimodal ingest for uploads and public links.

### 2. Authorize direct connector changes
Example:
> Use the GitHub connector directly. Make the changes in the repo.

### 3. Specify branch/merge expectations
Example:
> Start on a working branch, keep the history readable, and in the end I want it merged back into one branch.

### 4. Set documentation expectations
Example:
> Update the README and operator docs so the repo status and TODOs match the new implementation.

---

## Practical connector workflow

### Step 1 - inspect before editing
Ask ChatGPT to fetch:
- `README.md`
- `app/streamlit_app.py`
- the relevant page/module files
- the current admin/access-control code
- any ingest, IO, or config modules that will be touched

This keeps the changes grounded in the actual repo instead of memory alone.

### Step 2 - identify the smallest safe first change
Start with one focused goal:
- admin gating
- README refresh
- one new ingest mode
- one new UI control
- one broken workflow repair

Do not start by asking for a full rewrite unless the repo actually needs one.

### Step 3 - branch before editing
Ask for a named feature branch.
Good examples:
- `feature/admin-ingest-theory-portal`
- `docs/readme-refresh`
- `fix/zscan-propagation`

### Step 4 - make repo-side changes incrementally
A safe connector pattern is:
- fetch file
- create replacement blob(s)
- create tree
- create commit
- update branch ref

This is more reliable than trying to jump directly to a huge all-at-once rewrite.

### Step 5 - open a draft PR
Even if you plan to merge the work manually, the PR is useful because it:
- captures the diff
- gives a review handle
- preserves the branch work as a visible artifact

### Step 6 - continue polishing after the first PR
Use the PR as a checkpoint, not the end of the session.
Typical second-pass work:
- restore trimmed controls
- improve wording and UX
- fix documentation drift
- tighten naming and comments
- correct status/TODO sections

### Step 7 - merge back cleanly
When the goal is a single canonical branch:
- make sure the final tree is applied against the latest `main`
- avoid leaving the real state stranded only on a feature branch
- note whether the merge was PR-based or connector-side direct integration

---

## Guardrails

### Guardrail 1 - do not confuse connector changes with local validation
A connector commit means the repository changed.
It does **not** mean:
- the app was run on the desktop
- Streamlit was launched
- tests passed locally
- imports were validated in the real runtime environment

Always include a post-merge local verification step.

### Guardrail 2 - keep commit messages readable
Bad:
- `update stuff`
- `fix things`

Good:
- `docs: refresh README for current admin and ingest workflow`
- `feat: add admin-gated theory workspace`
- `refactor: normalize external ingest path`

### Guardrail 3 - separate structural changes from status documentation when possible
If the code path is changing and the README is changing, it is often cleaner to:
- land the code first
- then land the documentation refresh
or at least keep those concerns clearly described in the commit/PR body.

### Guardrail 4 - do not overclaim in README updates
Use language like:
- `current focus`
- `active migration`
- `working baseline`
- `next priority`

Avoid claiming something is production-ready if the session only proved that the files were changed.

---

## Post-merge checklist

After connector-side repo changes, run a local validation pass:

```text
1. git fetch origin
2. git checkout main
3. git pull
4. python -m compileall ...
5. uv run streamlit run ...
6. exercise the changed page(s)
7. correct any runtime issues in a follow-up commit
```

For multi-page Streamlit apps, also verify:
- navigation still works
- access control still behaves correctly
- session state keys do not collide
- new tabs/pages do not break existing imports
- README reflects the actual page structure

---

## Reusable prompt template

Copy/paste this block and replace the bracketed fields.

```text
Work on `[owner/repo]` through the GitHub connector.

Goal:
- [primary repo change]
- [secondary repo change]
- [documentation requirement]

Constraints:
- inspect the current files first
- make direct GitHub changes through the connector
- keep commits readable
- use a working branch first
- in the end I want the final state merged back into one canonical branch

Also:
- update the root README so current status, current focus, and TODOs are accurate
- be explicit about anything that still needs local runtime validation
```

---

## Reusable documentation block for README updates

This pattern works well in root README files:

```text
## Current status
- what is implemented now
- what was recently changed
- what is transitional

## Current focus
- the one or two active engineering priorities

## TODO
- short concrete items that could become issues or next-session tasks
```

---

## Recommended operator note to include after connector merges

Use wording like this in the session summary or commit note:

> The repository changes were applied through the GitHub connector and merged back to `main`. Local desktop/runtime validation is still required before treating the change as fully verified.

---

## Bottom line

The best connector workflow is:

- inspect first
- branch first
- change incrementally
- open a draft PR early
- continue polishing
- merge back cleanly
- verify locally afterward

That is the template established by the March 27, 2026 Pax Americana admin/ingest/theory session.
