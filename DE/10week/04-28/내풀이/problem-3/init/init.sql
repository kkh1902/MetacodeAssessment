-- 원본 데이터 테이블 (Producer가 적재)
CREATE TABLE IF NOT EXISTS raw_sales (
    id          SERIAL PRIMARY KEY,
    order_id    VARCHAR(50) NOT NULL,
    user_id     INTEGER NOT NULL,
    amount      NUMERIC(10, 2) NOT NULL,
    event_time  TIMESTAMP NOT NULL  -- UTC 기준
);

-- DAG가 집계하여 적재하는 테이블
CREATE TABLE IF NOT EXISTS daily_sales (
    id          SERIAL PRIMARY KEY,
    order_id    VARCHAR(50) NOT NULL,
    user_id     INTEGER NOT NULL,
    amount      NUMERIC(10, 2) NOT NULL,
    event_time  TIMESTAMP NOT NULL
);

-- 샘플 데이터 (2025-04-01 UTC 기준, 100건)
INSERT INTO raw_sales (order_id, user_id, amount, event_time)
SELECT
    'ORD-' || LPAD(gs::TEXT, 5, '0'),
    (RANDOM() * 999 + 1)::INTEGER,
    ROUND((RANDOM() * 99000 + 1000)::NUMERIC, 2),
    TIMESTAMP '2025-04-01 00:00:00' + (gs * INTERVAL '14 minutes')
FROM generate_series(0, 99) AS gs;
