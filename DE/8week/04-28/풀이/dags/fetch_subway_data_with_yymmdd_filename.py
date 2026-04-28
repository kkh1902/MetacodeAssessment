from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import boto3
import os
import json


default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}


def fetch_and_store_to_s3(templates_dict, **kwargs):
    api_key = " "
    aws_access_key = " "
    aws_secret_key = " "
    aws_region = "ap-northeast-2"

    api_date = templates_dict['api_date']
    yyyymmdd = templates_dict['yyyymmdd']
    yymmdd = templates_dict['yymmdd']

    # API 호출
    url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/CardSubwayStatsNew/1/1000/{api_date}"
    print(f"Requesting: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        raise

    # JSON 파싱
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Response text: {response.text[:500]}")
        raise

    # 응답 유효성 확인
    if 'CardSubwayStatsNew' not in data:
        print(f"Invalid response: {json.dumps(data, ensure_ascii=False)[:500]}")
        raise ValueError("API response does not contain 'CardSubwayStatsNew'")

    print(f"Fetched {len(data.get('CardSubwayStatsNew', {}).get('row', []))} records")

    # S3 저장
    s3_bucket = "subway-assignment-meta"
    s3_key = f"subway/source_data/{yyyymmdd}/{yymmdd}.json"

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )

        json_body = json.dumps(data, ensure_ascii=False)
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=json_body.encode('utf-8'),
            ContentType='application/json',
        )
        print(f"Uploaded to s3://{s3_bucket}/{s3_key}")
    except Exception as e:
        print(f"S3 upload failed: {e}")
        raise


def analyze_and_store_to_s3(templates_dict, **kwargs):
    import boto3
    import json
    import os
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import explode, col, sum as spark_sum, desc

    yyyymmdd = templates_dict['yyyymmdd']
    yymmdd = templates_dict['yymmdd']

    aws_access_key = " "
    aws_secret_key = " "
    aws_region = "ap-northeast-2"
    s3_bucket = "subway-assignment-meta"
    s3_input_key = f"subway/source_data/{yyyymmdd}/{yymmdd}.json"
    s3_output_key = f"subway/analysis/{yyyymmdd}.json"
    local_input_path = f"/tmp/{yymmdd}.json"

    # 1. S3에서 원본 데이터 다운로드
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_input_key)
        content = response['Body'].read().decode('utf-8')
        with open(local_input_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Downloaded s3://{s3_bucket}/{s3_input_key} -> {local_input_path}")
    except Exception as e:
        print(f"S3 download failed: {e}")
        raise

    # 2. PySpark SQL 기반 분석
    spark = None
    try:
        spark = SparkSession.builder \
            .appName(f"SubwayAnalysis_{yyyymmdd}") \
            .master("local[*]") \
            .getOrCreate()

        raw_df = spark.read.option("multiLine", "true").json(local_input_path)

        # 중첩 구조 해제
        exploded_df = raw_df.select(
            explode(col("CardSubwayStatsNew.row")).alias("row")
        )

        flat_df = exploded_df.select(
            col("row.LINE_NUM").alias("line_num"),
            col("row.SUB_STA_NM").alias("station_name"),
            col("row.RIDE_PASGR_NUM").cast("long").alias("ride_count"),
            col("row.ALIGHT_PASGR_NUM").cast("long").alias("alight_count"),
            col("row.USE_DT").alias("use_date"),
        )

        flat_df.createOrReplaceTempView("subway_data")

        # 분석 1: 노선별 총 이용자 수
        line_usage = spark.sql("""
            SELECT line_num,
                   SUM(ride_count) as total_ride,
                   SUM(alight_count) as total_alight,
                   SUM(ride_count + alight_count) as total_usage
            FROM subway_data
            GROUP BY line_num
            ORDER BY total_usage DESC
        """)
        print("=== Line Usage ===")
        line_usage.show(truncate=False)
        line_usage_list = [row.asDict() for row in line_usage.collect()]

        # 분석 2: 역별 승차 수 및 하차 수
        station_usage = spark.sql("""
            SELECT station_name,
                   SUM(ride_count) as total_ride,
                   SUM(alight_count) as total_alight
            FROM subway_data
            GROUP BY station_name
            ORDER BY total_ride DESC
        """)
        print("=== Station Usage ===")
        station_usage.show(20, truncate=False)
        station_usage_list = [row.asDict() for row in station_usage.collect()]

        # 분석 3: 승하차 비율 상위/하위 역
        ratio_analysis = spark.sql("""
            SELECT station_name,
                   SUM(ride_count) as total_ride,
                   SUM(alight_count) as total_alight,
                   ROUND(SUM(ride_count) / NULLIF(SUM(alight_count), 0), 4) as ride_alight_ratio
            FROM subway_data
            GROUP BY station_name
            HAVING SUM(alight_count) > 0
            ORDER BY ride_alight_ratio DESC
        """)
        top_ratio = [row.asDict() for row in ratio_analysis.limit(5).collect()]
        bottom_ratio = [row.asDict() for row in ratio_analysis.orderBy("ride_alight_ratio").limit(5).collect()]

        # 분석 4: 가장 많이 이용된 역 TOP 5
        top5_stations = spark.sql("""
            SELECT station_name,
                   SUM(ride_count + alight_count) as total_usage
            FROM subway_data
            GROUP BY station_name
            ORDER BY total_usage DESC
            LIMIT 5
        """)
        print("=== Top 5 Stations ===")
        top5_stations.show(truncate=False)
        top5_list = [row.asDict() for row in top5_stations.collect()]

        # 결과 정리
        analysis_result = {
            "analysis_date": yyyymmdd,
            "line_usage": line_usage_list,
            "top5_stations": top5_list,
            "ride_alight_ratio_top5": top_ratio,
            "ride_alight_ratio_bottom5": bottom_ratio,
            "total_stations_analyzed": len(station_usage_list),
        }

    except Exception as e:
        print(f"PySpark analysis failed: {e}")
        raise
    finally:
        if spark:
            spark.stop()

    # 3. 분석 결과를 JSON으로 S3에 저장 (메모리에서 직접 업로드)
    try:
        result_json = json.dumps(analysis_result, ensure_ascii=False, default=str)
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_output_key,
            Body=result_json.encode('utf-8'),
            ContentType='application/json',
        )
        print(f"Analysis result uploaded to s3://{s3_bucket}/{s3_output_key}")
    except Exception as e:
        print(f"S3 upload of analysis result failed: {e}")
        raise


# -------------------------
# DAG 정의 및 Task 구성
# -------------------------

with DAG(
    dag_id='fetch_subway_data_with_yymmdd_filename',
    default_args=default_args,
    schedule='@daily',
    catchup=True,
    tags=['subway', 's3', 'api'],
    description='서울시 지하철 데이터를 yymmdd 형식 파일로 S3에 저장',
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_and_store_to_s3',
        python_callable=fetch_and_store_to_s3,
        templates_dict={
            'api_date': "{{ macros.ds_format(macros.ds_add(ds, -7), '%Y-%m-%d', '%Y%m%d') }}",
            'yyyymmdd': "{{ macros.ds_format(macros.ds_add(ds, -7), '%Y-%m-%d', '%Y%m%d') }}",
            'yymmdd': "{{ macros.ds_format(macros.ds_add(ds, -7), '%Y-%m-%d', '%y%m%d') }}",
        },
    )

    analyze_task = PythonOperator(
        task_id='analyze_and_store_to_s3',
        python_callable=analyze_and_store_to_s3,
        templates_dict={
            'yyyymmdd': "{{ macros.ds_format(macros.ds_add(ds, -7), '%Y-%m-%d', '%Y%m%d') }}",
            'yymmdd': "{{ macros.ds_format(macros.ds_add(ds, -7), '%Y-%m-%d', '%y%m%d') }}",
        },
    )

    # Task 연결
    fetch_task >> analyze_task
