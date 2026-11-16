-- 03_audit.sql: periodic exposure review. Run before each quarter-end or on a schedule.
-- Verified on a live account 2026-11-15 (see docs/verification-notes.md).

-- 1. Which roles can share artifacts? After 01_rbac.sql, REPORT ARTIFACTS should list
--    ACCOUNTADMIN and REPORT_PUBLISHER only, not PUBLIC.
--    MANAGE ARTIFACT PUBLICATION is a legacy dashboard-publishing privilege; its BCR was
--    canceled and Snowflake says it will be removed. It's listed for visibility only.
SHOW GRANTS ON ACCOUNT
->> SELECT
    "privilege",
    "grantee_name",
    "granted_by",
    "created_on"
FROM $1
WHERE
    "privilege" ILIKE 'MANAGE ACCESS ON % ARTIFACTS'
    OR "privilege" = 'MANAGE ARTIFACT PUBLICATION'
ORDER BY "privilege", "grantee_name";

-- 2. Is account-wide artifact sharing on? (value = true means sharing is enabled)
SHOW PARAMETERS LIKE 'ENABLE_SNOWFLAKE_INTELLIGENCE_ARTIFACT_SHARING' IN ACCOUNT;

-- 3. Which users hold REPORT_PUBLISHER directly? (ACCOUNT_USAGE latency applies)
SELECT
    grantee_name AS user_name,
    role,
    created_on
FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_USERS
WHERE role = 'REPORT_PUBLISHER' AND deleted_on IS NULL
ORDER BY created_on DESC;
