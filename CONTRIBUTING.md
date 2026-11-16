# Contributing
- Branch from `main` and open a PR. CI must pass.
- Every new report goes under `reports/<name>/report.html` and must pass `scripts/validate_report.py`.
- Reports may query only `REPORTING` schema views (see `sql/02_snapshot_views.sql`). Don't embed raw tables.
- Don't commit credentials, account locators in URLs, or PII sample rows.
- Use Conventional Commits (`feat:`, `fix:`, `docs:`).
