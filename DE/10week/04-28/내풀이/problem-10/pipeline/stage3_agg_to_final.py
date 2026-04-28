"""
Stage 3: agg_daily → final_report

버그 (BUG-3):
  agg_daily의 컬럼명은 'total_revenue' 인데
  final_report 테이블의 컬럼명은 'sales_amount'
  → INSERT 시 컬럼 매핑 없이 positional insert 사용
  → sales_amount에 NULL이 들어감 (또는 컬럼 순서 어긋남)

실행:
  python stage3_agg_to_final.py --date 2025-04-01
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

    # BUG-3: SELECT 컬럼 순서가 INSERT 컬럼 순서와 불일치
    # final_report: (report_date, user_count, sales_amount)
    # 아래 SELECT: agg_date, total_revenue, user_count → user_count와 sales_amount 위치 뒤바뀜
    cur.execute("""
        INSERT INTO final_report (report_date, user_count, sales_amount)
        SELECT
            agg_date,
            total_revenue,   -- BUG: user_count 자리에 total_revenue 들어감
            user_count       -- BUG: sales_amount 자리에 user_count 들어감
        FROM agg_daily
        WHERE agg_date = %s
    """, (target_date,))

    conn.commit()

    cur.execute("SELECT report_date, user_count, sales_amount FROM final_report WHERE report_date = %s", (target_date,))
    row = cur.fetchone()

    cur.close()
    conn.close()
    if row:
        print(f"[Stage 3] final_report [{row[0]}]: user_count={row[1]}, sales_amount={row[2]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    run(args.date)
