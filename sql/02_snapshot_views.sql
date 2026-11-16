-- 02_snapshot_views.sql: the only objects reports are allowed to embed.
-- Verified 2026-11-15: ran end-to-end on a live account (throwaway names; view returned 70 rows).
-- SYSADMIN was separately confirmed to have SELECT on SNOWFLAKE.ACCOUNT_USAGE in that account.
-- Principle: aggregate before you embed. A report snapshot can't apply masking or row
-- access policies for the viewer, so the view has to be safe for the widest intended audience.

USE ROLE SYSADMIN;
CREATE DATABASE IF NOT EXISTS REPORTING_DB;
CREATE SCHEMA IF NOT EXISTS REPORTING_DB.REPORTING;

-- Example: daily warehouse credits (no user names, no query text).
CREATE OR REPLACE SECURE VIEW REPORTING_DB.REPORTING.V_WAREHOUSE_CREDITS_DAILY
    COMMENT = 'Report-safe: aggregated credits per warehouse per day'
AS
SELECT
    warehouse_name,
    DATE_TRUNC('day', start_time) AS usage_date,
    ROUND(SUM(credits_used), 4) AS credits_used
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD('day', -90, CURRENT_TIMESTAMP())
GROUP BY warehouse_name, DATE_TRUNC('day', start_time);

GRANT USAGE ON DATABASE REPORTING_DB TO ROLE REPORT_AUTHOR;
GRANT USAGE ON SCHEMA REPORTING_DB.REPORTING TO ROLE REPORT_AUTHOR;
GRANT SELECT ON ALL VIEWS IN SCHEMA REPORTING_DB.REPORTING TO ROLE REPORT_AUTHOR;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA REPORTING_DB.REPORTING TO ROLE REPORT_AUTHOR;
