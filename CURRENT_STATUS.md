# Current Status

## Repo role

Shared presentation, compute, reporting, and admin infrastructure for the Harrington application ecosystem.

## Current state

- Americana theme and shared layout primitives are active across the suite.
- Compute backend dispatch remains the common acceleration layer.
- Reporting and admin-support utilities remain centralized here.
- This repo is the correct home for reusable UI, formatting, and cross-app scaffolding rather than domain-specific logic.

## TODO

- Centralize more shared Streamlit widgets currently duplicated in app repos.
- Standardize report-generation interfaces across the suite.
- Add a cleaner shared admin/settings module.
- Add reusable file-ingest and artifact-export helpers.
- Expand operator documentation for backup, restore, and private sync workflows.
