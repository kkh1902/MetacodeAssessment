-- 중복 적재 검증 쿼리
-- daily_sales 테이블에서 동일 order_id가 2회 이상 적재된 건 확인
SELECT order_id, COUNT(*) as cnt
FROM daily_sales
GROUP BY order_id
HAVING COUNT(*) > 1
ORDER BY cnt DESC;

-- 전체 건수 vs 중복 제거 건수 비교
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT order_id) as unique_orders,
    COUNT(*) - COUNT(DISTINCT order_id) as duplicate_rows
FROM daily_sales;
