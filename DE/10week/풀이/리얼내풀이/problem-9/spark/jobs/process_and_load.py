"""
문제 9 - 참조 코드 (버그 포함)

파이프라인 구조:
  [staging_sales] → [이 Spark Job: 변환 + 검증] → [daily_sales_final]

증상:
  - 10회 실행 중 3~4회 실패
  - 실패 시점마다 에러 메시지가 다름
  - 로그에 ConnectionTimeout / OOM / TaskNotSerializable 혼재

BUG: JDBC URL에 socketTimeout=5000 (5초) 설정
     → 파티션 크기가 크면 (대량 데이터 처리 시) write 소요 시간이 5초를 초과
     → org.postgresql.util.PSQLException: SocketTimeoutException 발생
     → 파티션 크기가 작을 때는 정상 완료 → 간헐적 실패

로그 트랩:
  - java.lang.OutOfMemoryError: GC overhead limit exceeded
      → spark-worker GC 로그에서 나오는 경고 (메모리 부족으로 인한 실패가 아님)
      → GC 압박이 있어도 작업은 완료됨
  - org.apache.spark.SparkException: Task not serializable
      → amount_validator UDF 정의 시 발생하는 Spark 내부 최적화 경고
      → try/except로 잡혀서 실제 실패 원인이 아님
  - PSQLException: An I/O error occurred ... SocketTimeoutException ← 진짜 원인
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import BooleanType

PG_URL_READ  = "jdbc:postgresql://postgres:5432/airflow"
# BUG: socketTimeout=5000 → 5초 초과 write 시 SocketTimeoutException
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

# 금액 검증 UDF (정상 코드, 직렬화 경고가 뜰 수 있으나 실패 원인 아님)
@udf(BooleanType())
def is_valid_amount(amount):
    if amount is None:
        return False
    return float(amount) > 0

df_valid = df.filter(is_valid_amount(col("amount")))

print(f"[Spark] 유효 데이터: {df_valid.count()} rows")

# daily_sales_final에 적재
# BUG: PG_URL_WRITE에 socketTimeout=5000 → 대량 파티션 처리 시 타임아웃
df_valid.select("order_id", "user_id", "amount", "partition_date") \
    .write \
    .mode("append") \
    .jdbc(PG_URL_WRITE, "daily_sales_final", properties=PG_PROPS)

print("[Spark] daily_sales_final 적재 완료")
spark.stop()
