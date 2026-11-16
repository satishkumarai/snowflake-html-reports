# Architecture

## Before: how teams shared "a report" without HTML reports
```mermaid
flowchart LR
  T[(Tables)] --> Q[Worksheet / notebook]
  Q --> X[CSV / screenshot export]
  X --> S[Slides / Confluence / email]
  S --> R[Readers]
```
Every hop is outside Snowflake: there's no grant model, no single URL, and stale copies are everywhere.

## Option B: caller's-rights dashboards
```mermaid
flowchart LR
  T[(Tables)] -->|viewer's role, at open time| D[Dashboard artifact] --> R[Readers need data access + warehouse]
```

## After: HTML Report artifact
```mermaid
flowchart LR
  subgraph Governed
    T[(Tables)] --> V[REPORTING views]
  end
  V -->|author's role, at build time| H[.html in Workspace]
  H --> G{CI validator}
  G --> A[[Report artifact: static snapshot]]
  A -->|artifact READ grant| R[Readers: no warehouse, no table access]
```

The architectural delta is **when and as whom** data access is evaluated:

| | Dashboard / Chart artifact | Report artifact |
|---|---|---|
| Executes SQL on open | Yes (caller's rights) | No |
| Viewer needs source access | Yes | No |
| Viewer needs a warehouse | Yes | No |
| Data freshness | Live | Snapshot at last refresh |
| Access boundary | Table/row/column policies | Artifact grant |
