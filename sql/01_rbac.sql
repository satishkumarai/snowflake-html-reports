-- 01_rbac.sql: least-privilege roles for HTML Report artifacts.
-- Review before running. Run as SECURITYADMIN (roles) / ACCOUNTADMIN (account privileges).
--
-- Verified 2026-11-15 on a live account: every statement in this file ran successfully
-- (against throwaway role names, then dropped). PUBLIC holds MANAGE ACCESS ON REPORT ARTIFACTS
-- by default. The REVOKE below changes who can share in your account, so review before running.

USE ROLE SECURITYADMIN;

-- Authors build reports. They query only curated REPORTING views and can't share.
CREATE ROLE IF NOT EXISTS REPORT_AUTHOR;
-- Publishers can share report artifacts. Keep this group small and reviewed.
CREATE ROLE IF NOT EXISTS REPORT_PUBLISHER;
-- Audience roles that receive READ on specific artifacts (granted per artifact in the Share dialog).
CREATE ROLE IF NOT EXISTS REPORT_VIEWER_FINANCE;
CREATE ROLE IF NOT EXISTS REPORT_VIEWER_EXEC;

GRANT ROLE REPORT_AUTHOR TO ROLE REPORT_PUBLISHER;
GRANT ROLE REPORT_PUBLISHER TO ROLE SYSADMIN;
GRANT ROLE REPORT_VIEWER_FINANCE TO ROLE SYSADMIN;
GRANT ROLE REPORT_VIEWER_EXEC TO ROLE SYSADMIN;

-- Restrict who can share reports. Order matters: revoke from PUBLIC first, then grant.
USE ROLE ACCOUNTADMIN;
REVOKE MANAGE ACCESS ON REPORT ARTIFACTS ON ACCOUNT FROM ROLE PUBLIC;
GRANT MANAGE ACCESS ON REPORT ARTIFACTS ON ACCOUNT TO ROLE REPORT_PUBLISHER;

-- Kill switch (account-wide): stop all artifact sharing during an incident.
-- ALTER ACCOUNT SET ENABLE_SNOWFLAKE_INTELLIGENCE_ARTIFACT_SHARING = FALSE;
