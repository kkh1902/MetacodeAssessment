-- 문제 10 초기화 스크립트 — 4단계 lineage 테이블

-- Stage 0: 원본 이벤트 (Kafka consumer가 적재한다고 가정)
CREATE TABLE IF NOT EXISTS raw_events (
    event_id   SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    revenue    NUMERIC(12, 2) NOT NULL,
    event_time TIMESTAMP NOT NULL   -- UTC 기준
);

-- Stage 1: raw → staging (날짜 필터링)
CREATE TABLE IF NOT EXISTS staging_events (
    event_id   INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    revenue    NUMERIC(12, 2) NOT NULL,
    event_time TIMESTAMP NOT NULL
);

-- Stage 2: staging → agg (일별 집계)
CREATE TABLE IF NOT EXISTS agg_daily (
    agg_date     DATE NOT NULL,
    user_count   INTEGER NOT NULL,
    total_revenue NUMERIC(12, 2) NOT NULL
);

-- Stage 3: agg → final (컬럼 변환/정제)
CREATE TABLE IF NOT EXISTS final_report (
    report_date  DATE NOT NULL,
    user_count   INTEGER NOT NULL,
    sales_amount NUMERIC(12, 2)   -- BUG-3: revenue → sales_amount 로 컬럼명 변경됨
);
