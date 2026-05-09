"""Q8 gold_spark_sql.py — Silver parquet → 5종 집계 → PostgreSQL 적재"""
import sys
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, lit, lag, round as _round
)
from pyspark.sql.window import Window
from pyspark.sql.types import IntegerType


# ─── 환경 변수 (제출 시 빈 문자열) ─────────────────────────────────
AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION            = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
S3_BUCKET             = os.getenv("S3_BUCKET", "realstate-meta-s3")
PG_URL                = "jdbc:postgresql://postgres:5432/airflow"
PG_USER               = "airflow"
PG_PASSWORD           = "airflow"

S3_SILVER = f"s3a://{S3_BUCKET}/silver"


def make_spark():
    spark = (
        SparkSession.builder
        .appName("gold_realestate_aggregate")
        .config("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY_ID)
        .config("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        .config("spark.hadoop.fs.s3a.endpoint.region", AWS_REGION)
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def write_postgres(df, table_name):
    df.write.format("jdbc").mode("overwrite") \
        .option("url", PG_URL) \
        .option("dbtable", table_name) \
        .option("user", PG_USER) \
        .option("password", PG_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .save()
    print(f"[gold] saved → {table_name}")


def main(yyyymm: str):
    spark = make_spark()

    # silver parquet 로드 (시군구·yyyymm 파티션)
    df = (
        spark.read.parquet(S3_SILVER)
        .filter(col("yyyymm").cast(IntegerType()) <= int(yyyymm))
    )
    # Q7 컬럼 기준: 평당가/평형/거래금액/시군구 + 원본 aptNm, buildYear 등
    df = df.withColumn("평당가", col("평당가").cast("double")) \
           .withColumn("거래금액", col("거래금액").cast("double")) \
           .withColumn("yyyymm", col("yyyymm").cast("string"))
    df.createOrReplaceTempView("silver")

    # ── 1) 시군구별 평균 거래가·평당가 (월별) ───────────────
    sql1 = """
        SELECT `시군구`,
               yyyymm,
               ROUND(AVG(`거래금액`), 0)        AS avg_deal_price_manwon,
               ROUND(AVG(`평당가`),0) AS avg_price_per_pyeong
        FROM silver
        GROUP BY `시군구`, yyyymm
        ORDER BY `시군구`, yyyymm
    """
    write_postgres(spark.sql(sql1), "gold_realestate_district_avg")

    # ── 2) 평당가 TOP 10 단지 ────────────────────────────
    sql2 = """
        SELECT `시군구` AS district, umdNm AS dong, aptNm AS apt_name, excluUseAr AS area_m2, `평당가` AS price_per_pyeong
        FROM silver
        WHERE yyyymm = '{ym}'
        ORDER BY `평당가` DESC
        LIMIT 10
    """.format(ym=yyyymm)
    write_postgres(spark.sql(sql2), "gold_realestate_top10")

    # ── 3) 평형 분류별 거래량 분포 ───────────────────────
    sql3 = """
        SELECT `평형` AS size_category,
               yyyymm,
               COUNT(*)                       AS deal_count,
               ROUND(AVG(`평당가`),0) AS avg_price_per_pyeong
        FROM silver
        GROUP BY `평형`, yyyymm
        ORDER BY yyyymm, `평형`
    """
    write_postgres(spark.sql(sql3), "gold_realestate_size_dist")

    # ── 4) 건축연식 카테고리별 평당가 ────────────────────
    df_age = df.withColumn(
        "age_category",
        when(col("buildYear").isNull(), lit("미상"))
        .when((lit(2026) - col("buildYear")) <= 5, lit("신축"))
        .when((lit(2026) - col("buildYear")) <= 15, lit("준신축"))
        .otherwise(lit("구축"))
    )
    df_age.createOrReplaceTempView("silver_with_age")
    sql4 = """
        SELECT age_category,
               yyyymm,
               COUNT(*)                       AS deal_count,
               ROUND(AVG(`평당가`),0) AS avg_price_per_pyeong
        FROM silver_with_age
        GROUP BY age_category, yyyymm
        ORDER BY yyyymm, age_category
    """
    write_postgres(spark.sql(sql4), "gold_realestate_age_avg")

    # ── 5) 전월 대비 거래량·평당가 변화율 (LAG window) ────
    monthly = (
        spark.sql("""
            SELECT `시군구`,
                   yyyymm,
                   COUNT(*)                       AS deal_count,
                   ROUND(AVG(`평당가`),0) AS avg_ppp
            FROM silver
            GROUP BY `시군구`, yyyymm
        """)
    )
    w = Window.partitionBy("시군구").orderBy("yyyymm")
    mom = (
        monthly
        .withColumn("prev_count",  lag("deal_count").over(w))
        .withColumn("prev_ppp",    lag("avg_ppp").over(w))
        .withColumn(
            "count_change_pct",
            _round((col("deal_count") - col("prev_count")) / col("prev_count") * 100, 2),
        )
        .withColumn(
            "ppp_change_pct",
            _round((col("avg_ppp") - col("prev_ppp")) / col("prev_ppp") * 100, 2),
        )
        .filter(col("prev_count").isNotNull())
        .select("시군구", "yyyymm", "deal_count", "avg_ppp",
                "count_change_pct", "ppp_change_pct")
    )
    write_postgres(mom, "gold_realestate_mom_change")

    spark.stop()
    print("[gold] all 5 aggregations written to PostgreSQL")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: gold_spark_sql.py <yyyymm>")
    main(sys.argv[1])
