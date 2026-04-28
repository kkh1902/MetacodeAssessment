#!/bin/bash
# PostgreSQL 초기화: 테스트 테이블 생성 + 샘플 데이터 삽입
# 사용법: ./init_db.sh

set -e

DB_HOST="localhost"
DB_PORT="5432"
DB_USER="airflow"
DB_PASS="airflow"
DB_NAME="airflow"

echo "=== PostgreSQL 초기화 ==="

PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME <<'SQL'
-- 테스트 테이블 생성
CREATE TABLE IF NOT EXISTS sample_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    value INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 샘플 데이터 삽입
INSERT INTO sample_table (name, value) VALUES
    ('test_entry_1', 42),
    ('test_entry_2', 78),
    ('test_entry_3', 15)
ON CONFLICT DO NOTHING;

-- 확인
SELECT * FROM sample_table;
SQL

echo ""
echo "=== DB 초기화 완료 ==="
echo "host:     $DB_HOST:$DB_PORT"
echo "user:     $DB_USER"
echo "database: $DB_NAME"
echo "table:    sample_table"
