"""
Q05 — Spark Streaming 실시간 로그 분석
조건:
  - TCP 소켓으로 들어오는 로그 데이터
  - 오류 로그(예: "ERROR") 개수 실시간 집계
  - 결과를 콘솔에 출력
  - Spark Structured Streaming 사용

테스트 방법:
  터미널 A) nc -lk 9999
  터미널 B) spark-submit stream_log_processor.py
"""
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

HOST = os.environ.get("STREAM_HOST", "localhost")
PORT = int(os.environ.get("STREAM_PORT", "9999"))


def main():
    spark = (
        SparkSession.builder.appName("stream_log_processor")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    lines = (
        spark.readStream.format("socket")
        .option("host", HOST)
        .option("port", PORT)
        .load()
    )

    error_count = lines.filter(col("value").contains("ERROR")).groupBy().count()

    query = (
        error_count.writeStream.outputMode("complete")
        .format("console")
        .option("truncate", False)
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
