"""
Q7 silver_spark.py — Bronze XML → 정제 → 평당가/평형 UDF → parquet (snappy + partitionBy)

사용법:
  spark-submit --packages com.databricks:spark-xml_2.12:0.18.0 silver_spark.py <yyyymm>
"""
import sys
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, regexp_replace, trim, lit, when, udf
)
from pyspark.sql.types import DoubleType, StringType


# 채점자가 환경변수로 주입
AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION            = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
S3_BUCKET             = os.getenv("S3_BUCKET", "realestate-홍길동")

S3_BRONZE = f"s3a://{S3_BUCKET}/bronze"
S3_SILVER = f"s3a://{S3_BUCKET}/silver"


# ── UDF (1) 평당가 (만원/평) ─────────────────────────
@udf(returnType=DoubleType())
def price_per_pyeong(deal_amount: float, area_m2: float):
    if deal_amount is None or area_m2 is None or area_m2 == 0:
        return None
    pyeong = area_m2 / 3.3058
    return float(deal_amount) / pyeong


# ── UDF (2) 평형 분류 ────────────────────────────────
@udf(returnType=StringType())
def size_category(area_m2: float):
    if area_m2 is None:
        return None
    if area_m2 < 60:
        return "소형"
    if area_m2 < 85:
        return "중소형"
    if area_m2 < 135:
        return "중대형"
    return "대형"


def main(yyyymm: str):
    spark = (
        SparkSession.builder
        .appName("Q7-SilverTransform")
        .config("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY_ID)
        .config("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        .config("spark.hadoop.fs.s3a.endpoint.region", AWS_REGION)
        .getOrCreate()
    )

    # 1. Bronze XML 로딩 (spark-xml)
    df = (
        spark.read
        .format("xml")
        .option("rowTag", "item")
        .load(f"{S3_BRONZE}/{yyyymm}/*.xml")
    )

    # 입력 스키마가 한글/영문 버전 둘 다 가능하므로 컬럼명을 정규화
    amount_col = "거래금액" if "거래금액" in df.columns else "dealAmount"
    area_col = "전용면적" if "전용면적" in df.columns else "excluUseAr"
    district_col = "법정동" if "법정동" in df.columns else ("umdNm" if "umdNm" in df.columns else "sggCd")

    # 2. 결측치 제거
    df = df.filter(col(amount_col).isNotNull() & col(area_col).isNotNull())

    # 3. 거래금액 콤마/공백 제거 후 정수 변환 (만원 단위)
    df = df.withColumn(
        "거래금액",
        regexp_replace(trim(col(amount_col).cast("string")), ",", "").cast("long")
    )
    df = df.filter(col("거래금액").isNotNull())

    # 4. 시군구 컬럼 (법정동 시군구코드 기준)
    df = df.withColumn("시군구", col(district_col).cast("string"))

    # 5. UDF 적용
    df = df.withColumn(
        "평당가",
        price_per_pyeong(col("거래금액").cast("double"), col(area_col).cast("double"))
    )
    df = df.withColumn("평형", size_category(col(area_col).cast("double")))

    # 6. IQR 1.5배 밖 평당가 이상치 제거
    # (실행 안정성을 위해 전체 분포 기준으로 한 번 계산)
    q = df.approxQuantile("평당가", [0.25, 0.75], 0.05)
    if q and len(q) == 2 and q[0] is not None and q[1] is not None and q[1] >= q[0]:
        q1, q3 = q
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        df = df.filter((col("평당가") >= lo) & (col("평당가") <= hi))

    df = df.withColumn("yyyymm", lit(yyyymm))

    # 7. 저장 (parquet + snappy + partitionBy)
    (
        df.write
        .mode("overwrite")
        .partitionBy("시군구", "yyyymm")
        .option("compression", "snappy")
        .parquet(f"{S3_SILVER}/")
    )
    print(f"[Q7] silver written: {S3_SILVER}/시군구=*/yyyymm={yyyymm}")
    spark.stop()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "202601")
