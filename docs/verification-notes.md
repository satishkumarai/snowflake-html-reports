# Verification notes (fact-check run 2026-11-15, account dk58429)

**Release:** HTML reports, Public Preview, release note dated Nov 4, 2026 (from the official release note supplied with the brief).

## SQL: executed on a live account
| File | How it was verified | Result |
|---|---|---|
| `sql/01_rbac.sql` | Every statement run in an anonymous block with throwaway role names (`ZZ_FC_*`), then dropped | Succeeded |
| `sql/01_rbac.sql` GRANT/REVOKE `MANAGE ACCESS ON REPORT ARTIFACTS ON ACCOUNT` | Run against a throwaway role, then dropped | Succeeded |
| `sql/02_snapshot_views.sql` | Run end-to-end with a throwaway database; secure view queried | Succeeded, 70 rows |
| `sql/02` as SYSADMIN | `SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY` as SYSADMIN | Succeeded |
| `sql/03_audit.sql` query 1 (`SHOW GRANTS ->> SELECT`) | Executed | 13 rows |
| `sql/03_audit.sql` query 2 | Executed | `true` (sharing on) |
| `sql/03_audit.sql` query 3 | Executed | 0 rows (role not yet created) |

**Not executed on purpose:** `REVOKE ... FROM ROLE PUBLIC` and `ALTER ACCOUNT SET ENABLE_SNOWFLAKE_INTELLIGENCE_ARTIFACT_SHARING = FALSE`. Both change sharing for the whole account.

## Fixed during the fact-check
- `03_audit.sql` used `RESULT_SCAN(LAST_QUERY_ID())`, which fails if any statement runs between it and the SHOW. It now uses the `->>` pipe operator, which was verified.
- sqlfluff (Snowflake dialect) can't parse `->>` or `REVOKE MANAGE ACCESS ON REPORT ARTIFACTS`, so it was removed from CI and pre-commit.
- The validator line count was corrected (112 lines, not "about 100").
- The claim that CSP failures "surface as a blank chart" was softened. Blocking is documented; publish-time behavior wasn't tested.

## Verified against Snowflake docs
- `MANAGE ACCESS ON REPORT ARTIFACTS` is required to share Report artifacts.
- The five `MANAGE ACCESS ON <type> ARTIFACTS` privileges are granted to PUBLIC by default (BCR). Confirmed live: PUBLIC holds all five, granted 2026-10-20.
- Report, File and Thread artifacts are static snapshots. Dashboard and Chart artifacts run with caller's rights.
- `ENABLE_SNOWFLAKE_INTELLIGENCE_ARTIFACT_SHARING` turns all artifact sharing on or off. When it's off, only owners can open artifacts.
- `MANAGE ARTIFACT PUBLICATION` (also on PUBLIC) belongs to a **canceled** BCR for dashboard publishing and is documented as slated for removal. It isn't a report-sharing control.
- READ = Can view; WRITE = Can publish, without source-file access.

## Code: executed
- `pytest`: 11/11 pass. `ruff check` (E, F, I, B, UP): clean. `pip install -e ".[dev]"`: succeeds.
- `validate_report.py --strict` on the sample report: 0 findings.

## Sample report data
The snapshot was taken 2026-11-15: COMPUTE_WH 15.82, SEARCH_APP_WH 0.53, PUQ_TEST_WH 0.43, CLOUD_SERVICES_ONLY 0.02 (16.80 total). The window is a rolling 30 days, so a later re-run returned slightly different values (for example COMPUTE_WH 15.69). That's expected snapshot behavior, not an error.

## Assumptions (couldn't verify from this sandbox)
- Vendored library paths (`/libs/chart.js@4.4.4/...`) come from CoCo's HTML authoring guidance; rendering in a published artifact wasn't checked.
- Pre-commit hook revision `ruff-pre-commit v0.6.9`: there's no GitHub access from this sandbox to confirm the tag.
- The GitHub Actions workflow hasn't run on GitHub yet, because the repo isn't pushed.
- The 5 MB validator budget is a local default, not Snowflake's limit.

No performance or cost benchmarks were measured.
