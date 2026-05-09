from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType
import pandas as pd

spark = SparkSession.builder.appName("MemoryStress").getOrCreate()

@F.pandas_udf(StringType())
def heavy_transform(s: pd.Series) -> pd.Series:
    # 대용량 pandas 연산 → Python 프로세스 off-heap 메모리 다량 사용
    expanded = s.apply(lambda x: str(x) * 8000)
    df = pd.DataFrame({"a": expanded, "b": expanded.str.upper(), "c": expanded.str.lower()})
    return df["a"] + df["b"]

df = spark.range(0, 500000).toDF("id")
df = df.withColumn("result", heavy_transform(F.col("id").cast("string")))
df.cache()
count = df.count()
print(f"[MemoryStress] count: {count}")
spark.stop()
