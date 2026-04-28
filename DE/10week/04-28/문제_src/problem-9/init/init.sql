-- 문제 9: 초기 데이터

CREATE TABLE IF NOT EXISTS staging_sales (
    id             SERIAL PRIMARY KEY,
    order_id       VARCHAR(50) NOT NULL,
    user_id        INTEGER NOT NULL,
    amount         NUMERIC(10, 2) NOT NULL,
    partition_date DATE NOT NULL,
    loaded_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_sales_final (
    id             SERIAL PRIMARY KEY,
    order_id       VARCHAR(50) NOT NULL,
    user_id        INTEGER NOT NULL,
    amount         NUMERIC(10, 2) NOT NULL,
    partition_date DATE NOT NULL,
    transferred_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO staging_sales (order_id, user_id, amount, partition_date)
SELECT
    'ORD-' || LPAD(gs::TEXT, 6, '0'),
    (RANDOM() * 999 + 1)::INTEGER,
    ROUND((RANDOM() * 99000 + 1000)::NUMERIC, 2),
    '2025-04-01'::DATE + ((gs % 30) * INTERVAL '1 day')
FROM generate_series(1, 50000) AS gs;
