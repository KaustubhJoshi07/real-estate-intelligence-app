CREATE VIEW default.school_family_scores AS
WITH
  base AS (
   SELECT
     state
   , zip
   , school_count
   , elementary_schools
   , middle_schools
   , high_schools
   , total_enrollment
   , (((((school_count * 2) + (elementary_schools * 3)) + (middle_schools * 2)) + (high_schools * 2)) + (LOG10(GREATEST(total_enrollment, 1)) * 10)) raw_school_strength
   FROM
     school_zip_scores_clean
) 
, ranked AS (
   SELECT
     *
   , PERCENT_RANK() OVER (PARTITION BY state ORDER BY raw_school_strength ASC) school_rank
   FROM
     base
) 
SELECT
  state
, zip
, school_count
, elementary_schools
, middle_schools
, high_schools
, total_enrollment
, ROUND((school_rank * 100), 2) school_score
FROM
  ranked
