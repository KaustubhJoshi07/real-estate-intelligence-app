CREATE VIEW default.zip_intelligence_master AS
SELECT
  LPAD(CAST(z.zip_code AS VARCHAR), 5, '0') zip_code
, z.state
, z.state_name
, z.city
, z.metro
, z.county_name
, z.report_date
, z.current_home_value
, z.yoy_growth_pct
, z.appreciation_5yr_pct
, z.appreciation_rank
, z.growth_rank
, z.price_rank
, z.investment_score base_investment_score
, ROUND((((((100 - z.price_rank) * 5) + (z.appreciation_rank * 3)) + (z.growth_rank * 2)) / 10), 2) base_family_stability_score
, c.city_safety_indicator
, c.safety_data_level
, s.school_score
, z.better_use_case
FROM
  (((pbi_zip_scores z
LEFT JOIN us_state_map m ON (UPPER(trim(BOTH FROM z.state)) = UPPER(trim(BOTH FROM m.state_abbr))))
LEFT JOIN crime_family_scores c ON ((UPPER(trim(BOTH FROM z.city)) = UPPER(trim(BOTH FROM c.city))) AND (UPPER(trim(BOTH FROM m.state_full)) = UPPER(trim(BOTH FROM c.state_name)))))
LEFT JOIN school_family_scores s ON ((LPAD(CAST(z.zip_code AS VARCHAR), 5, '0') = LPAD(CAST(s.zip AS VARCHAR), 5, '0')) AND (UPPER(trim(BOTH FROM z.state)) = UPPER(trim(BOTH FROM s.state)))))
