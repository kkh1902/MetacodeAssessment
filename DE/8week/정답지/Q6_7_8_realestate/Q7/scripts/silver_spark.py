"""
Q07 — Silver: PySpark 정제 + UDF 2개
입력: s3://realestate-{이름}/bronze/{yyyymm}/{LAWD_CD}.xml
출력: s3://realestate-{이름}/silver/{시군구}/yyyymm=XXXXXX/  (parquet, snappy, partitionBy)
"""
import sys
import xml.etree.ElementTree as ET
import boto3
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf, col, regexp_replace
from pyspark.sql.types import StringType, FloatType

S3_BUCKET = sys.argv[1] if len(sys.argv) > 1 else "realestate-홍길동"
YYYYMM = sys.argv[2] if len(sys.argv) > 2 else "202401"

# 시군구 코드 → 한글 이름 매핑
LAWD_NAME = {
    "11680": "강남구", "11650": "서초구", "11710": "송파구",
    "11440": "마포구", "11170": "용산구", "11200": "성동구",
}


@udf(returnType=FloatType())
def price_per_pyeong(price, area):
    if price is None or area is None or area == 0:
        return None
    return float(price) / (float(area) / 3.3058)


@udf(returnType=StringType())
def size_category(area):
    if area is None:
        return "unknown"
    a = float(area)
    if a < 60: return "소형"
    if a < 85: return "중소형"
    if a < 135: return "중대형"
    return "대형"


def parse_xml_rows(xml_text: str, lawd_cd: str):
    """국토부 RTMS XML → row 리스트"""
    rows = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return rows
    for item in root.iter("item"):
        def g(tag):
            el = item.find(tag)
            return el.text.strip() if el is not None and el.text else None
        rows.append(Row(
            lawd_cd=lawd_cd,
            sigungu=LAWD_NAME.get(lawd_cd, lawd_cd),
            apt_name=g("aptNm"),
            dong=g("umdNm"),
            area=g("excluUseAr"),
            price_str=g("dealAmount"),
            built_year=g("buildYear"),
            deal_year=g("dealYear"),
            deal_month=g("dealMonth"),
            deal_day=g("dealDay"),
        ))
    return rows


def main():
    spark = (
        SparkSession.builder.appName("silver_realestate_transform")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate()
    )

    s3 = boto3.client("s3")
    prefix = f"bronze/{YYYYMM}/"
    objects = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix).get("Contents", [])

    all_rows = []
    for obj in objects:
        key = obj["Key"]
        lawd_cd = key.rsplit("/", 1)[-1].replace(".xml", "")
        xml_text = s3.get_object(Bucket=S3_BUCKET, Key=key)["Body"].read().decode("utf-8")
        all_rows.extend(parse_xml_rows(xml_text, lawd_cd))

    if not all_rows:
        print("no rows")
        spark.stop()
        return

    df = spark.createDataFrame(all_rows)

    # 결측 제거 + 가격 콤마 제거 후 정수 변환
    df = df.dropna(subset=["price_str", "area"])
    df = df.withColumn("price", regexp_replace("price_str", "[ ,]", "").cast("long"))
    df = df.withColumn("area_f", col("area").cast(FloatType()))

    # UDF 적용
    df = df.withColumn("price_per_pyeong", price_per_pyeong(col("price"), col("area_f")))
    df = df.withColumn("size_category", size_category(col("area_f")))

    # IQR 1.5배 밖 평당가 이상치 제거 (시군구별)
    quantiles = (
        df.groupBy("sigungu")
        .agg({"price_per_pyeong": "collect_list"})
        .collect()
    )
    bounds = {}
    for row in quantiles:
        vals = sorted([v for v in row[1] if v is not None])
        if len(vals) < 4:
            bounds[row["sigungu"]] = (None, None)
            continue
        q1 = vals[len(vals) // 4]
        q3 = vals[3 * len(vals) // 4]
        iqr = q3 - q1
        bounds[row["sigungu"]] = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)

    def in_bounds(sigungu, ppp):
        lo, hi = bounds.get(sigungu, (None, None))
        if lo is None or ppp is None:
            return True
        return lo <= ppp <= hi

    in_bounds_udf = udf(in_bounds)
    df = df.filter(in_bounds_udf(col("sigungu"), col("price_per_pyeong")))

    # 파티션 키 추가
    df = df.withColumn("yyyymm", col("deal_year") * 100 + col("deal_month").cast("int"))

    out_path = f"s3a://{S3_BUCKET}/silver/"
    (
        df.write.mode("overwrite")
        .partitionBy("sigungu", "yyyymm")
        .option("compression", "snappy")
        .parquet(out_path)
    )
    print(f"silver written -> {out_path}")

    spark.stop()


if __name__ == "__main__":
    main()
