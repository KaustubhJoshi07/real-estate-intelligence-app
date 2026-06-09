CREATE VIEW default.crime_family_scores AS
SELECT
  state_name
, city
, population
, violent_crime_rate
, property_crime_rate
, ROUND(GREATEST(0, LEAST(100, ((100 - (violent_crime_rate * 8E-2)) - (property_crime_rate * 1E-2)))), 2) city_safety_indicator
, 'City-level crime indicator' safety_data_level
FROM
  crime_scores_base
