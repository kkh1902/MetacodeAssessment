"""
문제 10 풀이 — Stage 3 수정

[BUG-3 수정]
  원인: SELECT 컬럼 순서와 INSERT 컬럼 순서 불일치
        INSERT INTO final_report (report_date, user_count, sales_amount)
        SELECT agg_date, total_revenue, user_count   ← 순서 뒤바뀜
        → user_count 자리에 total_revenue(수십만) 가 들어감
        → sales_amount 자리에 user_count(수백) 가 들어감

  수정: SELECT 컬럼 순서를 INSERT 컬럼 순서에 맞게 수정

[확인 쿼리]
  -- 수정 전: user_count = 수십만, sales_amount = 수백
  -- 수정 후: user_count = 수백~수천, sales_amount = 수억
  SELECT * FROM final_report;
"""
import psycopg2
import argparse

CONN = {
    "host": "localhost",
    "port": 5433,
    "dbname": "lineage_db",
    "user": "metade",
    "password": "metade2025",
}

def run(target_date: str):
    conn = psycopg2.connect(**CONN)
    cur  = conn.cursor()

    cur.execute("DELETE FROM final_report WHERE report_date = %s", (target_date,))

    # FIX: SELECT 컬럼 순서를 INSERT 컬럼 순서(report_date, user_count, sales_amount)에 맞춤
    cur.execute("""
        INSERT INTO final_report (report_date, user_count, sales_amount)
        SELECT
            agg_date,
            user_count,       -- FIX: user_count → user_count 자리
            total_revenue     -- FIX: total_revenue → sales_amount 자리
        FROM agg_daily
        WHERE agg_date = %s
    """, (target_date,))

    conn.commit()

    cur.execute("SELECT report_date, user_count, sales_amount FROM final_report WHERE report_date = %s", (target_date,))
    row = cur.fetchone()

    cur.close()
    conn.close()
    if row:
        print(f"[Stage 3 FIXED] final_report [{row[0]}]: user_count={row[1]}, sales_amount={row[2]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    run(args.date)
