"""
Q02_1 — Spark 에서 CSV 파일 분석하기
조건:
  - PySpark 로 로딩
  - 특정 컬럼 기준 평균값/최댓값/개수 계산
  - 결과는 콘솔 또는 파일로 출력
"""
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, max as spark_max, count

INPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "/opt/airflow/data/data.csv"
TARGET_COL = sys.argv[2] if len(sys.argv) > 2 else "age"


def main():
    spark = SparkSession.builder.appName("analyze_csv").getOrCreate()

    df = spark.read.csv(INPUT_PATH, header=True, inferSchema=True)
    print("=== schema ===")
    df.printSchema()

    summary = df.agg(
        avg(TARGET_COL).alias("average_age"),
        spark_max(TARGET_COL).alias("max_age"),
        count(TARGET_COL).alias("count"),
    )
    summary.show()

    spark.stop()


if __name__ == "__main__":
    main()
