-- 문제 8 참조 스키마
-- 문제 6~7에서 확보한 파이프라인에 staging → final 레이어 추가

-- Spark가 Kafka 데이터를 적재하는 staging 테이블
CREATE TABLE IF NOT EXISTS staging_sales (
    id             SERIAL PRIMARY KEY,
    order_id       VARCHAR(50) NOT NULL,
    user_id        INTEGER NOT NULL,
    amount         NUMERIC(10, 2) NOT NULL,
    partition_date DATE NOT NULL,
    loaded_at      TIMESTAMP DEFAULT NOW()
);

-- Airflow DAG이 staging → final로 이관하는 최종 테이블
CREATE TABLE IF NOT EXISTS daily_sales_final (
    id             SERIAL PRIMARY KEY,
    order_id       VARCHAR(50) NOT NULL,
    user_id        INTEGER NOT NULL,
    amount         NUMERIC(10, 2) NOT NULL,
    partition_date DATE NOT NULL,
    transferred_at TIMESTAMP DEFAULT NOW()
);

-- staging 샘플 데이터 (2025-04-01 기준, 100건 — Spark가 적재한 것으로 가정)
INSERT INTO staging_sales (order_id, user_id, amount, partition_date)
SELECT
    'ORD-' || LPAD(gs::TEXT, 5, '0'),
    (RANDOM() * 999 + 1)::INTEGER,
    ROUND((RANDOM() * 99000 + 1000)::NUMERIC, 2),
    '2025-04-01'
FROM generate_series(0, 99) AS gs;
