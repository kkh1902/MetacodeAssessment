#!/bin/bash
# LocalStack S3 초기화: 버킷 생성 + 테스트 데이터 업로드
# 사용법: ./init_s3.sh

set -e

ENDPOINT="http://localhost:4566"
BUCKET="subway-assignment-meta"
DATA_CSV="../문제/data/data.csv"

echo "=== LocalStack S3 초기화 ==="

# 1. 버킷 생성
echo "[1/3] 버킷 생성: $BUCKET"
aws --endpoint-url=$ENDPOINT s3 mb s3://$BUCKET 2>/dev/null || echo "  → 이미 존재"

# 2. data.csv 업로드 (과제2: s3_download_dag에서 다운로드할 파일)
echo "[2/3] data.csv 업로드"
if [ -f "$DATA_CSV" ]; then
    aws --endpoint-url=$ENDPOINT s3 cp "$DATA_CSV" s3://$BUCKET/data.csv
    echo "  → s3://$BUCKET/data.csv 업로드 완료"
else
    echo "  → 경고: $DATA_CSV 파일 없음. 샘플 생성"
    echo "name,age,city" > /tmp/data.csv
    echo "Kim MinSu,25,Seoul" >> /tmp/data.csv
    echo "Lee JiYoung,30,Busan" >> /tmp/data.csv
    echo "Park SungHoon,28,Daegu" >> /tmp/data.csv
    aws --endpoint-url=$ENDPOINT s3 cp /tmp/data.csv s3://$BUCKET/data.csv
    echo "  → 샘플 data.csv 업로드 완료"
fi

# 3. 확인
echo "[3/3] 버킷 내용 확인"
aws --endpoint-url=$ENDPOINT s3 ls s3://$BUCKET/ --recursive

echo ""
echo "=== S3 초기화 완료 ==="
echo "endpoint: $ENDPOINT"
echo "bucket:   $BUCKET"
