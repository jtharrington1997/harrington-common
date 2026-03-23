# Harrington Suite Platform Spec

## Purpose

The Harrington suite is a unified platform of domain applications built on shared
presentation, compute, reporting, and administrative primitives.

The suite is not a collection of unrelated apps. Each app should present the same
interaction grammar while delegating domain-specific logic to its own engine layer.

## Platform Layers

### 1. Shared Platform (`harrington-common`)
Owns cross-domain primitives that should behave the same in every app:
- Theme and visual language
- Layout and panel grammar
- Compute backend selection and diagnostics
- Reporting primitives and metadata
- Reusable domain-context schema
- Reusable derived-input / basis-resolution primitives

### 2. Domain Application
Each app owns:
- Domain models
- Domain engines and formulas
- Data ingestion/parsing
- App-specific pages and workflows
- Domain-specific report sections

Examples:
- `harrington-health`: clinical risk scores and lab interpretation
- `harrington-labs`: photonics and LMI simulation engines
- `harrington-wealth-management`: financial simulations and tracking
- `harrington-pax-americana`: geopolitical thesis and evidence analysis
- `harrington-automation-station`: instrumentation and measurement workflows

## Uniform Design Rules

### Context
Every app should expose structured context rather than hardcoded scattered strings.

Context should answer:
- What is the current state?
- What is the relevant historical state?
- What assumptions, constraints, or prior protocols matter?
- What is user-reported versus engine-derived?

### Derived Inputs
If a page pre-fills inputs from historical series, it should use the same conceptual model:
- Raw measured values remain primary
- Derived/default values are explicit
- Basis selection is visible and labeled
- The domain formula itself remains unchanged

Supported basis methods:
- `latest`
- `recent_mean`
- `ewma`

### Evidence
Whenever a derived/default value is shown, the app should be able to explain:
- which basis was used
- the resolved value
- the latest raw value
- sample count or similar support

### Reports
Reports should carry:
- context metadata
- basis metadata for derived values when relevant
- timestamps
- source attribution
- app/domain identifiers

## Ownership Boundaries

### Put in `harrington-common`
- Generic context schema
- Generic basis-resolution primitives
- Generic evidence-summary primitives
- Reusable UI renderers for context/evidence panels
- Report metadata helpers

### Keep in domain apps
- Clinical formulas such as MELD, Child-Pugh, APRI, FIB-4
- Physics engines and beam propagation models
- Finance withdrawal/simulation logic
- Geopolitical thesis scoring logic
- Hardware-specific orchestration

## First Reusable Version

The first reusable version in `harrington-common` includes:

1. `context_schema.py`
   - dataclasses for app context, sections, and items

2. `series_basis.py`
   - generic basis configuration
   - latest / recent mean / EWMA resolution
   - summary/evidence object

This keeps the shared pattern small and dependency-light. Domain apps can adopt it
incrementally without restructuring their engines all at once.

## Migration Path

1. Add shared primitives to `harrington-common`
2. Adopt them in `harrington-health`
3. Reuse them in `harrington-labs` for simulation defaults and evidence summaries
4. Reuse them in finance, geopolitics, and automation apps
5. Add shared UI renderers after the data contracts stabilize

## Non-Goals

The shared platform must not contain:
- clinical claims
- physics-specific formulas
- financial recommendations
- geopolitical conclusions
- device-specific driver logic

It should only contain reusable contracts and helpers.
