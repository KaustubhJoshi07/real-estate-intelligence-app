CREATE VIEW default.pbi_zip_scores AS
WITH
  ranked AS (
   SELECT
     *
   , (PERCENT_RANK() OVER (PARTITION BY state ORDER BY COALESCE(appreciation_5yr_pct, 0) ASC) * 100) appreciation_rank
   , (PERCENT_RANK() OVER (PARTITION BY state ORDER BY COALESCE(yoy_growth_pct, 0) ASC) * 100) growth_rank
   , (PERCENT_RANK() OVER (PARTITION BY state ORDER BY current_home_value ASC) * 100) price_rank
   FROM
     pbi_zip_latest
) 
, scored AS (
   SELECT
     *
   , ROUND((((appreciation_rank * 5E-1) + (growth_rank * 3E-1)) + ((100 - price_rank) * 2E-1)), 2) investment_score
   , ROUND(((((100 - price_rank) * 5E-1) + (appreciation_rank * 3E-1)) + (growth_rank * 2E-1)), 2) family_stability_score
   FROM
     ranked
) 
, final AS (
   SELECT
     *
   , (CASE WHEN (investment_score >= family_stability_score) THEN 'Investment' ELSE 'Family Stability' END) better_use_case
   FROM
     scored
) 
SELECT *
FROM
  final
