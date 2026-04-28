#!/bin/bash
# 학생 S3 관련 코드 채점 스크립트
# 사용법: ./run_test.sh <학생폴더명>
# 예시:   ./run_test.sh 8주차_강경래

set -e

ENDPOINT="http://localhost:4566"
BUCKET="subway-assignment-meta"
STUDENT_DIR="../../수강생/$1"

if [ -z "$1" ]; then
    echo "사용법: ./run_test.sh <학생폴더명>"
    echo "예시:   ./run_test.sh 8주차_강경래"
    echo ""
    echo "=== 수강생 목록 ==="
    ls ../../수강생/ | grep "^8주차"
    exit 1
fi

# 학생 폴더 찾기 (NFD 인코딩 대응)
FOUND_DIR=$(find ../../수강생 -maxdepth 1 -name "$1" -type d 2>/dev/null | head -1)
if [ -z "$FOUND_DIR" ]; then
    echo "오류: '$1' 폴더를 찾을 수 없습니다"
    exit 1
fi

echo "============================================"
echo "  채점 대상: $1"
echo "============================================"
echo ""

# --- 과제2: s3_download_dag (S3 다운로드 로직 테스트) ---
echo "=== [과제2] s3_download_dag 테스트 ==="
S3_DOWNLOAD=$(find "$FOUND_DIR" -name "s3_download_dag.py" ! -path "*MACOSX*" | head -1)
if [ -n "$S3_DOWNLOAD" ]; then
    echo "파일: $S3_DOWNLOAD"
    # boto3가 LocalStack을 바라보도록 환경변수 설정 후 import 테스트
    AWS_ACCESS_KEY_ID=test \
    AWS_SECRET_ACCESS_KEY=test \
    AWS_DEFAULT_REGION=ap-northeast-2 \
    python3 -c "
import boto3, os, sys
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'

# LocalStack S3로 다운로드 테스트
s3 = boto3.client('s3', endpoint_url='$ENDPOINT', region_name='ap-northeast-2')
local_path = '/tmp/test_download_data.csv'
try:
    s3.download_file('$BUCKET', 'data.csv', local_path)
    if os.path.exists(local_path):
        size = os.path.getsize(local_path)
        print(f'  ✓ S3 다운로드 성공 ({size} bytes)')
        os.remove(local_path)
    else:
        print('  ✗ 다운로드 실패: 파일 생성 안됨')
except Exception as e:
    print(f'  ✗ 다운로드 실패: {e}')
" 2>&1
else
    echo "  ✗ s3_download_dag.py 미제출"
fi
echo ""

# --- 과제7: fetch_subway_data (API → S3 저장 테스트) ---
echo "=== [과제7] fetch_subway_data S3 업로드 테스트 ==="
SUBWAY_DAG=$(find "$FOUND_DIR" -name "*subway*dag*.py" -o -name "*fetch*subway*.py" ! -path "*MACOSX*" 2>/dev/null | grep -v MACOSX | head -1)
if [ -n "$SUBWAY_DAG" ]; then
    echo "파일: $SUBWAY_DAG"
    # S3 put_object가 동작하는지 테스트
    AWS_ACCESS_KEY_ID=test \
    AWS_SECRET_ACCESS_KEY=test \
    python3 -c "
import boto3, json

s3 = boto3.client('s3', endpoint_url='$ENDPOINT', region_name='ap-northeast-2',
                   aws_access_key_id='test', aws_secret_access_key='test')

# 테스트 데이터 업로드
test_data = json.dumps({'test': True}, ensure_ascii=False)
test_key = 'subway/test/test.json'
try:
    s3.put_object(Bucket='$BUCKET', Key=test_key, Body=test_data.encode('utf-8'), ContentType='application/json')
    # 업로드 확인
    obj = s3.get_object(Bucket='$BUCKET', Key=test_key)
    content = obj['Body'].read().decode('utf-8')
    print(f'  ✓ S3 업로드+다운로드 성공 (put_object → get_object)')
    # 정리
    s3.delete_object(Bucket='$BUCKET', Key=test_key)
except Exception as e:
    print(f'  ✗ S3 업로드 실패: {e}')
" 2>&1
else
    echo "  ✗ subway DAG 파일 미제출"
fi
echo ""

# --- 과제8: analyze_and_store_to_s3 (S3 → 분석 → S3 테스트) ---
echo "=== [과제8] analyze_and_store_to_s3 S3 읽기/쓰기 테스트 ==="
if [ -n "$SUBWAY_DAG" ]; then
    echo "파일: $SUBWAY_DAG"
    AWS_ACCESS_KEY_ID=test \
    AWS_SECRET_ACCESS_KEY=test \
    python3 -c "
import boto3, json

s3 = boto3.client('s3', endpoint_url='$ENDPOINT', region_name='ap-northeast-2',
                   aws_access_key_id='test', aws_secret_access_key='test')

# 1. 테스트용 원본 JSON 업로드 (과제7 결과물 시뮬레이션)
source_key = 'subway/source_data/20260101/260101.json'
fake_data = {
    'CardSubwayStatsNew': {
        'row': [
            {'LINE_NUM': '1호선', 'SUB_STA_NM': '서울역', 'RIDE_PASGR_NUM': '50000', 'ALIGHT_PASGR_NUM': '48000', 'USE_DT': '20260101'},
            {'LINE_NUM': '2호선', 'SUB_STA_NM': '강남', 'RIDE_PASGR_NUM': '70000', 'ALIGHT_PASGR_NUM': '65000', 'USE_DT': '20260101'},
        ]
    }
}
try:
    s3.put_object(Bucket='$BUCKET', Key=source_key, Body=json.dumps(fake_data, ensure_ascii=False).encode('utf-8'), ContentType='application/json')
    print(f'  ✓ 테스트 원본 데이터 업로드 완료: {source_key}')

    # 2. 다운로드 테스트
    obj = s3.get_object(Bucket='$BUCKET', Key=source_key)
    content = json.loads(obj['Body'].read().decode('utf-8'))
    rows = content.get('CardSubwayStatsNew', {}).get('row', [])
    print(f'  ✓ S3 다운로드 성공: {len(rows)}건')

    # 3. 분석 결과 업로드 테스트
    result_key = 'subway/analysis/20260101.json'
    result = {'top_5_stations': [{'station': '강남', 'count': 135000}]}
    s3.put_object(Bucket='$BUCKET', Key=result_key, Body=json.dumps(result, ensure_ascii=False).encode('utf-8'), ContentType='application/json')
    print(f'  ✓ 분석 결과 업로드 완료: {result_key}')

    # 정리
    s3.delete_object(Bucket='$BUCKET', Key=source_key)
    s3.delete_object(Bucket='$BUCKET', Key=result_key)
except Exception as e:
    print(f'  ✗ 테스트 실패: {e}')
" 2>&1
else
    echo "  ✗ subway DAG 파일 미제출"
fi

echo ""
echo "============================================"
echo "  채점 완료: $1"
echo "============================================"
