"""
Q04 — Spark UDF 적용
조건:
  - 예시: 이름 컬럼 → 이니셜 추출
  - PySpark UDF 등록 후 데이터 처리
  - 처리 결과 저장
"""
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

INPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "/opt/airflow/data/data.csv"
OUTPUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "./output"


@udf(returnType=StringType())
def initial_udf(name: str) -> str:
    if name is None or len(name) == 0:
        return ""
    return name[0].upper()


def main():
    spark = SparkSession.builder.appName("apply_udf").getOrCreate()

    df = spark.read.csv(INPUT_PATH, header=True, inferSchema=True)
    df_with_initial = df.withColumn("initial", initial_udf(df["name"]))
    df_with_initial.show()

    df_with_initial.write.mode("overwrite").csv(OUTPUT_DIR, header=True)
    print(f"saved -> {OUTPUT_DIR}")

    spark.stop()


if __name__ == "__main__":
    main()
