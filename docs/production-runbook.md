# Production runbook

## Refresh and republish
1. Open the source `.html` in Workspaces and select **Refresh report**. Review the refresh instructions.
2. Diff the embedded data against the previous version in git.
3. Run `python scripts/validate_report.py <file> --strict`.
4. Publish the update. The URL stays the same.
5. Record the snapshot date in the report body. Readers can't otherwise tell how old it is.

There's no scheduled refresh in preview. If a report needs to be "daily", someone owns a daily manual step, or the report is really a dashboard.

## Failure modes
| Symptom | Likely cause | Fix |
|---|---|---|
| Chart blank after publish | CDN script, inline `onclick`, `fetch` | Run the validator; use `/libs/` + `addEventListener` |
| Publish rejected | File exceeds the account artifact size limit | Aggregate harder; compress or remove embedded images |
| Reader can't open link | No grant, wrong account, or sharing disabled | Check the artifact grants and the account parameter |
| Reader sees stale numbers | Source edited but not republished | Republish |
| Sensitive data exposed | Over-broad query or grant | Revoke grants / delete the artifact first, then fix the source |

## Monitor
- Monthly: run `sql/03_audit.sql` and check which roles hold MANAGE ACCESS.
- Per report: owner, audience, snapshot date and source views (kept in the metadata block and the PR).
