# Changelog
## [0.1.0] - 2026-11-15
### Added
- RBAC, snapshot view and audit SQL.
- CSP-safe FinOps sample report.
- `validate_report.py` pre-publish gate, with tests and CI.
- Snowflake Chronicles article, Medium article and LinkedIn post.
### Fixed (fact-check 2026-11-15)
- `03_audit.sql`: RESULT_SCAN filter replaced with the `->>` pipe operator (the old version failed if run out of sequence).
- `01_rbac.sql`: GRANT/REVOKE syntax verified by execution.
- Removed sqlfluff: it can't parse verified Snowflake syntax (`->>`, artifact privileges).
- Documented the legacy `MANAGE ARTIFACT PUBLICATION` privilege.
