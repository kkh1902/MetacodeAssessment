"""Q4-(1) PySpark CSV 분석. spark-submit analyze_csv.py /path/to/data.csv"""
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, max as smax, count, col


def main(csv_path: str):
    spark = SparkSession.builder.appName("Q4-AnalyzeCSV").getOrCreate()
    df = (spark.read.option("header", "true").option("inferSchema", "true").csv(csv_path))
    df.printSchema()

    numeric = [f.name for f in df.schema.fields
               if f.dataType.simpleString() in ("int", "bigint", "double", "float")]
    if not numeric:
        raise ValueError("숫자 컬럼이 없습니다.")
    target = numeric[0]
    print(f"[Q4] target column: {target}")

    df.agg(
        avg(col(target)).alias("avg_v"),
        smax(col(target)).alias("max_v"),
        count("*").alias("row_count"),
    ).show()

    spark.stop()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/opt/airflow/data/data.csv")
