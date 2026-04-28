-- 문제 9 초기화 스크립트

-- 원본 이벤트 테이블
CREATE TABLE IF NOT EXISTS raw_events (
    event_id   SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    amount     NUMERIC(12, 2) NOT NULL,
    event_time TIMESTAMP NOT NULL
);

-- 상품 테이블 (BUG: 중복 행 의도적으로 삽입됨)
CREATE TABLE IF NOT EXISTS products (
    product_id   INTEGER NOT NULL,
    product_name VARCHAR(100),
    category     VARCHAR(50)
);

-- 일별 매출 집계 테이블
CREATE TABLE IF NOT EXISTS daily_sales_agg (
    agg_date   DATE NOT NULL,
    user_id    INTEGER NOT NULL,
    total_amount NUMERIC(12, 2),
    order_count  INTEGER
);

-- 정상 상품 데이터 (product_id 1~5)
INSERT INTO products VALUES (1, '노트북',   '전자제품');
INSERT INTO products VALUES (2, '마우스',   '전자제품');
INSERT INTO products VALUES (3, '키보드',   '전자제품');
INSERT INTO products VALUES (4, '모니터',   '전자제품');
INSERT INTO products VALUES (5, '헤드셋',   '전자제품');

-- BUG: product_id 1, 2 가 중복 삽입 → JOIN 시 fan-out 발생
INSERT INTO products VALUES (1, '노트북',   '전자제품');
INSERT INTO products VALUES (2, '마우스',   '전자제품');
