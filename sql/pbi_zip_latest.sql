CREATE VIEW default.pbi_zip_latest AS
WITH
  ranked AS (
   SELECT
     *
   , ROW_NUMBER() OVER (PARTITION BY state, zip_code ORDER BY report_date DESC) rn
   FROM
     pbi_zip_growth
) 
SELECT
  zip_code
, state
, state_name
, city
, metro
, county_name
, report_date
, home_value current_home_value
, yoy_growth_pct
, appreciation_5yr_pct
FROM
  ranked
WHERE (rn = 1)
