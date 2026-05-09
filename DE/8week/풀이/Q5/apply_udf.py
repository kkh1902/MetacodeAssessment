"""Q5 — Spark UDF 적용 + 결과 저장"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType


def extract_initial(name: str) -> str:
    if not name:
        return ""
    parts = name.strip().split()
    return "".join(p[0].upper() for p in parts if p) if len(parts) > 1 else name[0]


def main():
    spark = SparkSession.builder.appName("Q5-ApplyUDF").getOrCreate()
    data = [("홍길동", 25), ("김철수", 31), ("John Doe", 40), ("Jane Smith", 28)]
    df = spark.createDataFrame(data, ["name", "age"])

    initial_udf = udf(extract_initial, StringType())
    out = df.withColumn("initial", initial_udf(df["name"]))
    out.show(truncate=False)

    out.write.mode("overwrite").csv("./result", header=True)
    print("[Q5] saved to ./result")
    spark.stop()


if __name__ == "__main__":
    main()
