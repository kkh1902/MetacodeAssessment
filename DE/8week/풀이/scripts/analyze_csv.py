from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("CSV Analysis") \
    .master("local[*]") \
    .getOrCreate()

# CSV 파일 로딩
df = spark.read.option("header", "true").option("inferSchema", "true") \
    .csv("/opt/spark-data/data.csv")

print("=== Schema ===")
df.printSchema()

print("=== Row Count ===")
print(f"Total rows: {df.count()}")

print("=== Summary Statistics ===")
df.describe().show()

# 숫자형 컬럼 자동 탐지 후 분석
numeric_cols = [f.name for f in df.schema.fields
                if str(f.dataType) in ('IntegerType()', 'LongType()', 'DoubleType()', 'FloatType()')]

for col_name in numeric_cols:
    stats = df.agg(
        F.avg(col_name).alias("average"),
        F.max(col_name).alias("maximum"),
        F.min(col_name).alias("minimum"),
        F.count(col_name).alias("count"),
    ).collect()[0]
    print(f"\n=== {col_name} ===")
    print(f"  Average: {stats['average']}")
    print(f"  Maximum: {stats['maximum']}")
    print(f"  Minimum: {stats['minimum']}")
    print(f"  Count:   {stats['count']}")

print("\n=== Sample Data (Top 10) ===")
df.show(10)

spark.stop()
