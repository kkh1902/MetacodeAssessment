"""
Q08 — Gold: 5종 집계 + PostgreSQL 적재
테이블 5개:
  (1) gold_realestate_district_avg   — 시군구별 평균 거래가·평당가 (월별)
  (2) gold_realestate_top10          — 평당가 TOP 10 단지 (동·아파트명·평당가)
  (3) gold_realestate_size_dist      — 평형 분류별 거래량 분포
  (4) gold_realestate_age_avg        — 건축연식 카테고리별 평당가
  (5) gold_realestate_mom_change     — 전월 대비 거래량·평당가 변화율 (LAG)
"""
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, count, when, lit, lag, round as spark_round
)
from pyspark.sql.window import Window

S3_BUCKET = sys.argv[1] if len(sys.argv) > 1 else "realestate-홍길동"
PG_URL = sys.argv[2] if len(sys.argv) > 2 else "jdbc:postgresql://postgres:5432/airflow"
PG_USER = sys.argv[3] if len(sys.argv) > 3 else "airflow"
PG_PASSWORD = sys.argv[4] if len(sys.argv) > 4 else "airflow"

JDBC_PROPS = {
    "user": PG_USER,
    "password": PG_PASSWORD,
    "driver": "org.postgresql.Driver",
}


def write_pg(df, table):
    df.write.mode("overwrite").jdbc(PG_URL, table, properties=JDBC_PROPS)
    cnt = df.count()
    print(f"[write_pg] {table} rows={cnt}")
    assert cnt > 0, f"{table} row count = 0"


def main():
    spark = (
        SparkSession.builder.appName("gold_realestate_aggregate")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate()
    )

    silver = spark.read.parquet(f"s3a://{S3_BUCKET}/silver/")
    silver.createOrReplaceTempView("silver")

    # (1) 시군구별 평균 거래가·평당가 (월별)
    district_avg = spark.sql("""
        SELECT sigungu, yyyymm,
               AVG(price)            AS avg_price,
               AVG(price_per_pyeong) AS avg_ppp,
               COUNT(*)              AS deal_count
        FROM silver
        GROUP BY sigungu, yyyymm
    """)
    write_pg(district_avg, "gold_realestate_district_avg")

    # (2) 평당가 TOP 10 단지
    top10 = spark.sql("""
        SELECT sigungu, dong, apt_name,
               AVG(price_per_pyeong) AS avg_ppp,
               COUNT(*)              AS deal_count
        FROM silver
        GROUP BY sigungu, dong, apt_name
        ORDER BY avg_ppp DESC
        LIMIT 10
    """)
    write_pg(top10, "gold_realestate_top10")

    # (3) 평형 분류별 거래량 분포
    size_dist = spark.sql("""
        SELECT size_category, COUNT(*) AS deal_count
        FROM silver
        GROUP BY size_category
    """)
    write_pg(size_dist, "gold_realestate_size_dist")

    # (4) 건축연식 카테고리별 평당가
    age_avg = (
        silver.withColumn(
            "age_category",
            when(col("built_year") >= 2020, lit("신축"))
            .when(col("built_year") >= 2010, lit("준신축"))
            .otherwise(lit("구축"))
        )
        .groupBy("age_category")
        .agg(avg("price_per_pyeong").alias("avg_ppp"),
             count("*").alias("deal_count"))
    )
    write_pg(age_avg, "gold_realestate_age_avg")

    # (5) 전월 대비 거래량·평당가 변화율 (LAG window function)
    monthly = (
        silver.groupBy("yyyymm")
        .agg(count("*").alias("deal_count"),
             avg("price_per_pyeong").alias("avg_ppp"))
    )
    w = Window.orderBy("yyyymm")
    mom_change = (
        monthly.withColumn("prev_deal_count", lag("deal_count").over(w))
        .withColumn("prev_avg_ppp", lag("avg_ppp").over(w))
        .withColumn(
            "deal_count_pct",
            spark_round((col("deal_count") - col("prev_deal_count")) / col("prev_deal_count") * 100, 2)
        )
        .withColumn(
            "ppp_pct",
            spark_round((col("avg_ppp") - col("prev_avg_ppp")) / col("prev_avg_ppp") * 100, 2)
        )
    )
    write_pg(mom_change, "gold_realestate_mom_change")

    spark.stop()


if __name__ == "__main__":
    main()
