from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, window, col

spark = SparkSession.builder \
    .appName("Streaming Log Processor") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# TCP 소켓에서 스트림 읽기 (nc -lk 9999 로 로그 전송)
lines = spark.readStream \
    .format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .load()

# ERROR 로그 필터링 및 집계
error_lines = lines.filter(col("value").contains("ERROR"))

error_counts = error_lines.groupBy(
    window(col("timestamp"), "30 seconds"),
).count().select("window.start", "window.end", "count")

# 콘솔 출력
query = error_counts.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime="10 seconds") \
    .start()

print("Streaming started. Send logs to localhost:9999")
print("Example: nc -lk 9999  then type lines like 'ERROR something happened'")

query.awaitTermination()
