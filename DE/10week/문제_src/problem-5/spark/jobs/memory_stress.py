from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MemoryStress").getOrCreate()
sc = spark.sparkContext

def oom_task(x):
    # executor Python 프로세스에서 700MB 직접 할당 → container limit(576m) 초과 → OOMKilled
    buf = bytearray(700 * 1024 * 1024)
    buf[:] = bytes(700 * 1024 * 1024)  # 모든 페이지 강제 커밋
    return x

result = sc.parallelize(range(2), 2).map(oom_task).collect()
print(f"[MemoryStress] result: {result}")
spark.stop()
