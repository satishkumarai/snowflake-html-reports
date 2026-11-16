# Security model

## Trust boundary
The author's role is evaluated **once**, when CoCo runs the queries. After publishing, the only control is the artifact's grants. Masking policies and row access policies **don't re-evaluate per viewer**, because the snapshot already holds whatever the author could see.

## Controls (in order of leverage)
1. **Who can share**: `MANAGE ACCESS ON REPORT ARTIFACTS`. Granted to `PUBLIC` by default, so restrict it with `sql/01_rbac.sql`.
2. **What can be embedded**: authors use `REPORT_AUTHOR`, which can read only `REPORTING` views. Data is aggregated before it's embedded.
3. **What gets published**: the CI validator plus human review of the embedded rows.
4. **Who can view**: per-artifact READ grants to audience roles. Avoid `PUBLIC` (READ to PUBLIC = the whole account).
5. **Kill switch**: `ENABLE_SNOWFLAKE_INTELLIGENCE_ARTIFACT_SHARING = FALSE` (only owners can open artifacts while it's off).

## Access levels
- READ (Can view): opens the artifact.
- WRITE (Can publish): can publish updates. **Doesn't** grant access to the source workspace file.

## Things the docs imply but are easy to miss
- The author's role choice is a data-classification decision. Building a report as ACCOUNTADMIN and sharing it widely is a privilege escalation path.
- Unpublished edits are invisible to readers, and so is unpublished *removal* of sensitive data. Fixing the source file isn't remediation until you republish (or revoke).
