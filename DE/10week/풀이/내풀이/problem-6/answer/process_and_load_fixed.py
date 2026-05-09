"""
문제 6 - 풀이 (버그 수정)

[BUG 수정]
  원인: JDBC URL에 socketTimeout=5000 설정
        파티션 데이터 양이 많을 때 write 시간이 5초를 초과
        → PSQLException: SocketTimeoutException → task 실패
        → 파티션 크기가 실행마다 달라지므로 3~4/10 간헐적 실패

  수정: socketTimeout, connectTimeout 제거
        (PostgreSQL 기본값 사용, 타임아웃 없음)
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import BooleanType

PG_URL_READ  = "jdbc:postgresql://postgres:5432/airflow"
# FIX: socketTimeout 제거
PG_URL_WRITE = "jdbc:postgresql://postgres:5432/airflow"
PG_PROPS = {"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}

spark = SparkSession.builder \
    .appName("ProcessAndLoadFixed") \
    .config("spark.sql.shuffle.partitions", "8") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df = spark.read.jdbc(PG_URL_READ, "staging_sales", properties=PG_PROPS)

print(f"[Spark] staging_sales 읽기 완료: {df.count()} rows")

@udf(BooleanType())
def is_valid_amount(amount):
    if amount is None:
        return False
    return float(amount) > 0

df_valid = df.filter(is_valid_amount(col("amount")))

print(f"[Spark] 유효 데이터: {df_valid.count()} rows")

df_valid.select("order_id", "user_id", "amount", "partition_date") \
    .write \
    .mode("append") \
    .jdbc(PG_URL_WRITE, "daily_sales_final", properties=PG_PROPS)

print("[Spark] daily_sales_final 적재 완료")
spark.stop()
