from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType


def extract_initials(name):
    """이름에서 이니셜 추출 (예: 'Kim MinSu' -> 'K.M.')"""
    if not name:
        return ''
    parts = name.strip().split()
    return '.'.join([p[0].upper() for p in parts if p]) + '.'


spark = SparkSession.builder \
    .appName("Apply UDF - Extract Initials") \
    .master("local[*]") \
    .getOrCreate()

# 샘플 데이터 생성
data = [
    (1, "Kim MinSu", 25),
    (2, "Lee JiYoung", 30),
    (3, "Park SungHoon", 28),
    (4, "Choi YuNa", 22),
    (5, "Jung DaeHyun", 35),
]
df = spark.createDataFrame(data, ["id", "name", "age"])

print("=== Original Data ===")
df.show()

# UDF 등록
extract_initials_udf = udf(extract_initials, StringType())

# UDF 적용
result_df = df.withColumn("initials", extract_initials_udf(col("name")))

print("=== After UDF (Initials Extracted) ===")
result_df.show()

# 결과 저장
output_path = "/opt/spark-data/udf_result"
result_df.write.mode("overwrite").csv(output_path, header=True)
print(f"Result saved to {output_path}")

spark.stop()
