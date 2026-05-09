"""
문제 9 - 참조 코드

파이프라인 구조:
  [staging_sales] → [이 Spark Job: 변환 + 검증] → [daily_sales_final]

증상:
  - 10회 실행 중 3~4회 실패
  - 실패 시점마다 에러 메시지가 다름
  - 로그에 ConnectionTimeout / OOM / TaskNotSerializable 혼재
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import BooleanType

PG_URL_READ  = "jdbc:postgresql://postgres:5432/airflow"
PG_URL_WRITE = (
    "jdbc:postgresql://postgres:5432/airflow"
    "?socketTimeout=5000"
    "&connectTimeout=3000"
)
PG_PROPS = {"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}

spark = SparkSession.builder \
    .appName("ProcessAndLoad") \
    .config("spark.sql.shuffle.partitions", "8") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# staging_sales 읽기
df = spark.read.jdbc(PG_URL_READ, "staging_sales", properties=PG_PROPS)

print(f"[Spark] staging_sales 읽기 완료: {df.count()} rows")

# 금액 검증 UDF
@udf(BooleanType())
def is_valid_amount(amount):
    if amount is None:
        return False
    return float(amount) > 0

df_valid = df.filter(is_valid_amount(col("amount")))

print(f"[Spark] 유효 데이터: {df_valid.count()} rows")

# daily_sales_final에 적재
df_valid.select("order_id", "user_id", "amount", "partition_date") \
    .write \
    .mode("append") \
    .jdbc(PG_URL_WRITE, "daily_sales_final", properties=PG_PROPS)

print("[Spark] daily_sales_final 적재 완료")
spark.stop()
