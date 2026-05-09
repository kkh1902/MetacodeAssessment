-- 문제 7: Timezone 혼재 데이터 정합성
CREATE TABLE IF NOT EXISTS partitioned_sales (
    id             SERIAL PRIMARY KEY,
    order_id       VARCHAR(50),
    user_id        VARCHAR(50),
    amount         NUMERIC(10, 2),
    event_time     TIMESTAMP,
    partition_date DATE
);
