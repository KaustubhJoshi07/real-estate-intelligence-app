import sys
import re
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, expr, to_date, coalesce

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

input_path = "s3://real-estate-economic-intelligence-kj/raw/zillow/zhvi_zip/zhvi_data.csv"
output_path = "s3://real-estate-economic-intelligence-kj/curated/zillow/zhvi_zip_long/"

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "false") \
    .option("quote", '"') \
    .option("escape", '"') \
    .option("multiLine", "true") \
    .csv(input_path)

print("COLUMNS DETECTED:")
print(df.columns)

id_columns = [
    "RegionID",
    "SizeRank",
    "RegionName",
    "RegionType",
    "StateName",
    "State",
    "City",
    "Metro",
    "CountyName"
]

date_pattern_1 = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")
date_pattern_2 = re.compile(r"^\d{4}-\d{2}-\d{2}$")

date_columns = [
    c for c in df.columns
    if date_pattern_1.match(c) or date_pattern_2.match(c)
]

print("DATE COLUMNS FOUND:")
print(len(date_columns))
print(date_columns[:10])

if len(date_columns) == 0:
    raise Exception(f"No date columns found. Columns detected: {df.columns}")

stack_items = ", ".join([f"'{c}', `{c}`" for c in date_columns])

stack_expression = f"stack({len(date_columns)}, {stack_items}) as (report_date_raw, home_value)"

long_df = df.select(
    *[col(c) for c in id_columns if c in df.columns],
    expr(stack_expression)
)

clean_df = long_df.withColumn(
    "report_date",
    coalesce(
        to_date(col("report_date_raw"), "M/d/yyyy"),
        to_date(col("report_date_raw"), "yyyy-MM-dd")
    )
).withColumn(
    "zip_code",
    col("RegionName").cast("string")
).withColumn(
    "home_value",
    col("home_value").cast("double")
).drop("report_date_raw")

final_df = clean_df.select(
    col("RegionID").alias("region_id"),
    col("SizeRank").alias("size_rank"),
    col("zip_code"),
    col("RegionType").alias("region_type"),
    col("StateName").alias("state_name"),
    col("State").alias("state"),
    col("City").alias("city"),
    col("Metro").alias("metro"),
    col("CountyName").alias("county_name"),
    col("report_date"),
    col("home_value")
)

final_df = final_df.filter(
    col("report_date").isNotNull() &
    col("home_value").isNotNull()
)

final_df.write.mode("overwrite").option("header", "true").csv(output_path)

job.commit()
