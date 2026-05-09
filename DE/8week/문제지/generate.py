#!/usr/bin/env python3
"""DE 8주차 문제지 (260429-version) — 양식 유지 + 목차 + Q6~Q10 + PDF 단독 제출 금지 명시"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

FONT_DIR = os.path.expanduser("~/.local/share/fonts")
pdfmetrics.registerFont(TTFont("NG",  os.path.join(FONT_DIR, "NanumGothic-Regular.ttf")))
pdfmetrics.registerFont(TTFont("NGB", os.path.join(FONT_DIR, "NanumGothic-Bold.ttf")))

NAVY      = Color(0.1058, 0.2274, 0.4196)
MED_BLUE  = Color(0.2901, 0.4352, 0.6470)
GRAY_TEXT = Color(0.2666, 0.2666, 0.2666)
GRAY_SUB  = Color(0.4,    0.4,    0.4   )
RED_TEXT  = Color(0.8,    0.0,    0.0   )
RED_BG    = Color(1.0,    0.9607, 0.9607)
BLUE_BG   = Color(0.9411, 0.9568, 0.9803)
DARK      = Color(0.1333, 0.1333, 0.1333)
GREEN_BG  = Color(0.9215, 0.9686, 0.9254)
GREEN_BD  = Color(0.3843, 0.7137, 0.4313)

S = {
    "title":    ParagraphStyle("title",  fontName="NGB", fontSize=26,
                                alignment=TA_CENTER, textColor=NAVY,
                                spaceAfter=4*mm, leading=34),
    "subtitle": ParagraphStyle("sub",    fontName="NG",  fontSize=11,
                                alignment=TA_CENTER, textColor=GRAY_SUB,
                                spaceAfter=8*mm, leading=16),
    "sec":      ParagraphStyle("sec",    fontName="NGB", fontSize=14,
                                textColor=NAVY, spaceBefore=4*mm, spaceAfter=3*mm, leading=20),
    "sec_sm":   ParagraphStyle("sec_sm", fontName="NGB", fontSize=11,
                                textColor=NAVY, spaceBefore=4*mm, spaceAfter=2*mm, leading=16),
    "q_title":  ParagraphStyle("qt",     fontName="NGB", fontSize=16,
                                textColor=NAVY, spaceAfter=2*mm, leading=22),
    "score":    ParagraphStyle("score",  fontName="NGB", fontSize=10,
                                textColor=MED_BLUE, spaceAfter=4*mm, leading=14),
    "body":     ParagraphStyle("body",   fontName="NG",  fontSize=10,
                                textColor=GRAY_TEXT, spaceAfter=3*mm, leading=16),
    "bullet":   ParagraphStyle("bul",    fontName="NG",  fontSize=10,
                                textColor=GRAY_TEXT, leading=16,
                                leftIndent=4*mm, spaceAfter=1.5*mm),
    "file":     ParagraphStyle("file",   fontName="NGB", fontSize=10,
                                textColor=MED_BLUE, leading=16,
                                leftIndent=4*mm, spaceAfter=1.5*mm),
    "warn":     ParagraphStyle("warn",   fontName="NGB", fontSize=11,
                                textColor=RED_TEXT, leading=16),
    "warn_bul": ParagraphStyle("wbul",   fontName="NG",  fontSize=11,
                                textColor=RED_TEXT, leading=16, leftIndent=4*mm,
                                spaceAfter=2*mm),
    "code":     ParagraphStyle("code",   fontName="NG",  fontSize=8.5,
                                textColor=GRAY_TEXT, leading=11,
                                leftIndent=4*mm, spaceAfter=0.5*mm,
                                backColor=Color(0.96, 0.96, 0.94)),
    "note":     ParagraphStyle("note",   fontName="NG",  fontSize=10,
                                textColor=DARK, leading=15),
    "green_hd": ParagraphStyle("ghd",    fontName="NGB", fontSize=10,
                                textColor=Color(0.1, 0.4, 0.2), leading=15),
    "toc":      ParagraphStyle("toc",    fontName="NG",  fontSize=11,
                                textColor=DARK, leading=20, leftIndent=2*mm),
    "toc_b":    ParagraphStyle("tocb",   fontName="NGB", fontSize=11,
                                textColor=NAVY, leading=20, leftIndent=2*mm),
}


def sp(h=3):
    return Spacer(1, h * mm)


def light_box(items, bg, border=None, label=None, label_style=None, border_w=0.5):
    rows = []
    if label:
        rows.append(Paragraph(label, label_style or S["sec_sm"]))
        rows.append(sp(1))
    for item in items:
        rows.append(item if not isinstance(item, str) else Paragraph(item, S["bullet"]))
    t = Table([[rows]], colWidths=[170 * mm])
    ts = [
        ("BACKGROUND",   (0, 0), (-1, -1), bg),
        ("TOPPADDING",   (0, 0), (-1, -1), 4 * mm),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4 * mm),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
    ]
    if border:
        ts.append(("BOX", (0, 0), (-1, -1), border_w, border))
    t.setStyle(TableStyle(ts))
    return t


def struct_box(lines):
    rows = [Paragraph("제출 ZIP 내부 폴더 구조", S["sec_sm"]), sp(1)]
    for l in lines:
        # 공백을 &nbsp; 로 변환해서 reportlab Paragraph 가 들여쓰기를 collapse 하지 않도록
        rendered = l.replace(" ", "&nbsp;")
        rows.append(Paragraph(rendered, S["code"]))
    t = Table([[rows]], colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), BLUE_BG),
        ("TOPPADDING",   (0, 0), (-1, -1), 4 * mm),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4 * mm),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
    ]))
    return t


FOOTER_TEXT = (
    "© 메타코드 | 본 자료는 수강생 본인만 열람 가능합니다. "
    "외부 유출·공유·재배포를 엄격히 금지하며, "
    "위반 시 저작권법 제136조에 의거하여 법적 조치가 취해질 수 있습니다."
)


def draw_footer(canvas, doc):
    """모든 페이지 하단에 저작권 안내 + 페이지 번호 표시."""
    canvas.saveState()
    canvas.setFont("NG", 7)
    canvas.setFillColor(GRAY_SUB)
    page_w = A4[0]
    # 본문과의 분리선
    canvas.setStrokeColor(GRAY_SUB)
    canvas.setLineWidth(0.3)
    canvas.line(20 * mm, 14 * mm, page_w - 20 * mm, 14 * mm)
    # 저작권 텍스트 (가운데)
    text_obj = canvas.beginText()
    text_obj.setTextOrigin(20 * mm, 10 * mm)
    text_obj.setFont("NG", 7)
    text_obj.setFillColor(GRAY_SUB)
    # 텍스트 줄바꿈 (문장 길어서 두 줄)
    line1 = "© 메타코드 | 본 자료는 수강생 본인만 열람 가능합니다. 외부 유출·공유·재배포를 엄격히 금지하며,"
    line2 = "위반 시 저작권법 제136조에 의거하여 법적 조치가 취해질 수 있습니다."
    text_obj.textLine(line1)
    text_obj.textLine(line2)
    canvas.drawText(text_obj)
    # 페이지 번호 (오른쪽)
    canvas.drawRightString(page_w - 20 * mm, 6 * mm, f"- {doc.page} -")
    canvas.restoreState()


def build():
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "8주차_문제지.pdf")
    doc = SimpleDocTemplate(
        output, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=22 * mm,  # 푸터 공간 확보
    )
    story = []

    # ══════════════════════════════════════
    # 1페이지 — 표지 + 안내
    # ══════════════════════════════════════
    story += [
        sp(20),
        Paragraph("8 주차 주관식 문제지", S["title"]),
        Paragraph("Airflow · Spark · Kubernetes 데이터 파이프라인 실습", S["subtitle"]),
        sp(2),
        HRFlowable(width="100%", thickness=1, color=NAVY,
                   spaceBefore=2*mm, spaceAfter=8*mm),
        Paragraph("과제 제출 안내", S["sec"]),
        sp(2),
        light_box([
            Paragraph("▲  아래 경우 모두 <b>0 점 처리</b>", S["warn"]),
            sp(2),
            Paragraph("•  <b>.docx · .doc · .hwp</b> 등 워드/한글 문서 파일만 단독 제출", S["warn_bul"]),
            Paragraph("•  <b>.pdf</b> 파일만 단독 제출", S["warn_bul"]),
            Paragraph("•  코드를 이미지(캡쳐/사진)로 제출", S["warn_bul"]),
            sp(2),
            Paragraph("▲  <b>과제 제출 양식(폴더 구조 · 파일명) 틀릴 시 −10점 감점</b>", S["warn"]),
            Paragraph("▲  <b>캡처가 아닌 로그 텍스트로 제출 시 −10점 감점</b>", S["warn"]),
            sp(2),
            Paragraph(
                "반드시 아래 폴더 구조를 지켜 <b>ZIP 파일</b>로 <b>압축하여 제출</b>하세요.",
                S["note"]),
        ], bg=RED_BG, border=RED_TEXT),
        sp(6),
        Paragraph("제출 형식", S["sec"]),
        sp(1),
        Paragraph(
            "<b>파일명:</b>  <font color='#4A6FA5'><b>데엔몇기_이름_몇주차.zip</b></font>",
            ParagraphStyle("pf", fontName="NGB", fontSize=11,
                           textColor=DARK, leading=18)),
        Paragraph(
            "예시:  데엔3기_홍길동_8주차.zip",
            ParagraphStyle("ex", fontName="NG", fontSize=10,
                           textColor=GRAY_SUB, leading=15)),
        PageBreak(),
    ]

    # ══════════════════════════════════════
    # 2페이지 — 목차
    # ══════════════════════════════════════
    def toc_line(label, page):
        dots = "." * max(2, 70 - len(label) - len(str(page)) - 2)
        return Paragraph(
            f"{label}  <font color='#888888'>{dots}</font>  <b>{page}</b>",
            S["toc"])

    story += [
        sp(8),
        Paragraph("목차", S["sec"]),
        sp(2),
        HRFlowable(width="100%", thickness=0.5, color=NAVY, spaceAfter=4*mm),
        toc_line("과제 제출 안내", 1),
        toc_line("제출 폴더 구조", 3),
        sp(2),
        Paragraph("Part 1 — Airflow · Spark 기초 (Q1 ~ Q5)", S["toc_b"]),
        toc_line("과제 01_1 — 첫 번째 DAG 만들기", 5),
        toc_line("과제 01_2 — S3 에서 데이터 가져오기 (Airflow + boto3)", 6),
        toc_line("과제 02_1 — Spark 에서 CSV 파일 분석하기", 7),
        toc_line("과제 02_2 — Airflow 로 Spark 작업 자동화하기", 8),
        toc_line("과제 03 — Airflow Variable 과 Connection 활용", 9),
        toc_line("과제 04 — Spark UDF 적용", 10),
        toc_line("과제 05 — Spark Streaming 실시간 로그 분석", 11),
        sp(2),
        Paragraph("Part 2 — 부동산 실거래가 Medallion ETL (Q6 ~ Q8)", S["toc_b"]),
        toc_line("과제 06 — Bronze (국토부 API → S3 raw)", 12),
        toc_line("과제 07 — Silver (PySpark 정제 + UDF)", 13),
        toc_line("과제 08 — Gold (집계 + PostgreSQL 적재)", 14),
        sp(2),
        Paragraph("Part 3 — Kubernetes 입문 (Q9 ~ Q10)", S["toc_b"]),
        toc_line("과제 09 — Kubernetes 정적 페이지 배포", 15),
        toc_line("과제 10 — HPA 오토스케일링", 16),
        PageBreak(),
    ]

    # ══════════════════════════════════════
    # 3페이지 — 제출 폴더 구조 Part 1 (Q1~Q5)
    # 캡처는 각 Q 폴더 안 capture/ 서브폴더로 분리
    # ══════════════════════════════════════
    story += [
        sp(4),
        Paragraph("제출 폴더 구조  (1/2 — Q1 ~ Q5)", S["sec"]),
        sp(2),
        Paragraph(
            "각 문제 폴더는 <b>코드 파일</b>과 <b>capture/</b> 서브폴더로 명확히 분리합니다. "
            "캡처(스크린샷)는 모두 <b>capture/</b> 폴더 안에 모아 주세요.",
            S["body"]),
        sp(2),
        struct_box([
            "데엔3기_홍길동_8주차.zip",
            "└─ 데엔3기_홍길동_8주차/",
            "   │",
            "   ├─ Q1/                              ← 첫 번째 DAG (Q01_1) / S3 다운로드 (Q01_2)",
            "   │  ├─ hello_airflow_dag.py          (Q01_1)",
            "   │  ├─ s3_download_dag.py            (Q01_2)",
            "   │  └─ capture/",
            "   │     ├─ airflow_ui.png             (Q01_1)",
            "   │     └─ s3_download_log.png        (Q01_2)",
            "   │",
            "   ├─ Q2/                              ← Spark CSV (Q02_1) / Airflow + Spark (Q02_2)",
            "   │  ├─ analyze_csv.py                (Q02_1)",
            "   │  ├─ run_spark_job.py              (Q02_2)",
            "   │  └─ capture/",
            "   │     └─ spark_csv_output.png       (Q02_1)",
            "   │",
            "   ├─ Q3/                              ← Variable + Connection",
            "   │  ├─ db_query_dag.py",
            "   │  └─ capture/",
            "   │     └─ query_result.png",
            "   │",
            "   ├─ Q4/                              ← Spark UDF",
            "   │  ├─ apply_udf.py",
            "   │  ├─ output/                       (저장된 CSV 또는 parquet)",
            "   │  └─ capture/",
            "   │     └─ udf_result.png",
            "   │",
            "   └─ Q5/                              ← Spark Streaming",
            "      ├─ stream_log_processor.py",
            "      └─ capture/",
            "         └─ streaming_output.png",
            "",
            "   ⋯ (다음 페이지 Q6 ~ Q10 계속)",
        ]),
        PageBreak(),
        sp(4),
        Paragraph("제출 폴더 구조  (2/2 — Q6 ~ Q10)", S["sec"]),
        sp(2),
        struct_box([
            "데엔3기_홍길동_8주차/   ⋯ (앞 페이지 이어서)",
            "   ├─ Q6_7_8_realestate/                ← 부동산 Medallion ETL (Q6~Q8 통합 환경)",
            "   │  ├─ docker-compose.yml             ← 공통 환경 (Airflow + Spark + Postgres)",
            "   │  │",
            "   │  ├─ Q6/                            ← Bronze",
            "   │  │  ├─ dags/",
            "   │  │  │  └─ bronze_realestate_collect.py",
            "   │  │  └─ capture/",
            "   │  │     ├─ airflow_graph.png",
            "   │  │     └─ s3_objects.png",
            "   │  │",
            "   │  ├─ Q7/                            ← Silver",
            "   │  │  ├─ dags/",
            "   │  │  │  └─ silver_realestate_transform.py",
            "   │  │  ├─ scripts/",
            "   │  │  │  └─ silver_spark.py",
            "   │  │  └─ capture/",
            "   │  │     ├─ spark_ui.png",
            "   │  │     └─ s3_silver.png",
            "   │  │",
            "   │  └─ Q8/                            ← Gold",
            "   │     ├─ dags/",
            "   │     │  └─ gold_realestate_aggregate.py",
            "   │     ├─ scripts/",
            "   │     │  └─ gold_spark_sql.py",
            "   │     └─ capture/",
            "   │        ├─ postgres_tables.png",
            "   │        └─ postgres_select.png",
            "   │",
            "   ├─ Q9/                              ← EC2 + k3s Nginx 배포",
            "   │  ├─ k8s/",
            "   │  │  ├─ 01-namespace.yaml",
            "   │  │  ├─ 02-configmap.yaml",
            "   │  │  ├─ 03-deployment.yaml",
            "   │  │  ├─ 04-service.yaml",
            "   │  │  └─ 05-ingress.yaml",
            "   │  └─ capture/",
            "   │     ├─ instance_id.png",
            "   │     ├─ kubectl_get_all.png",
            "   │     └─ browser.png",
            "   └─ Q10/                             ← HPA 오토스케일링",
            "      ├─ k8s/",
            "      │  └─ 07-hpa.yaml",
            "      ├─ load-test.sh",
            "      └─ capture/",
            "         ├─ kubectl_top_pod.png",
            "         ├─ hpa_watch.png",
            "         └─ hpa_describe.png",
        ]),
        sp(3),
        PageBreak(),
    ]

    # ══════════════════════════════════════
    # 문제 헬퍼
    # ══════════════════════════════════════
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    def q(num, title, score, desc, conditions, submits, checks, images=None):
        label = f"과제 {num:02d}" if isinstance(num, int) else f"과제 {num}"
        elems = [
            Paragraph(f"{label} — {title}", S["q_title"]),
            Paragraph(f"배점: {score}점", S["score"]),
            Paragraph(desc, S["body"]),
        ]
        if conditions:
            elems.append(Paragraph("조건", S["sec_sm"]))
            for c in conditions:
                elems.append(Paragraph(f"•  {c}", S["bullet"]))
            elems.append(sp(2))
        # 참고 이미지 (제출물 위에 배치)
        if images:
            elems.append(Paragraph("참고 이미지 (예상 출력 화면)", S["sec_sm"]))
            n = len(images)
            # 이미지 1개: 크게, 2개+: 페이지 내에서 더 잘 보이게 확대
            max_h = 110 * mm if n == 1 else 70 * mm
            max_w = 170 * mm
            for img_name in images:
                img_path = os.path.join(SCRIPT_DIR, "images", img_name)
                if os.path.exists(img_path):
                    img = Image(img_path)
                    ratio = img.imageHeight / img.imageWidth
                    img.drawWidth = min(img.imageWidth, max_w)
                    img.drawHeight = img.drawWidth * ratio
                    if img.drawHeight > max_h:
                        img.drawHeight = max_h
                        img.drawWidth = img.drawHeight / ratio
                    img.hAlign = 'LEFT'
                    elems.append(img)
                    elems.append(sp(2))
        elems.append(Paragraph("제출물", S["sec_sm"]))
        sub_rows = []
        for s in submits:
            sub_rows.append(Paragraph(f"•  {s}", S["file"]))
        elems.append(light_box(sub_rows, bg=BLUE_BG, border=MED_BLUE))
        elems.append(sp(2))
        elems.append(Paragraph("채점 기준", S["sec_sm"]))
        chk_rows = []
        for c in checks:
            chk_rows.append(Paragraph(f"•  {c}", S["bullet"]))
        elems.append(light_box(chk_rows, bg=GREEN_BG, border=GREEN_BD))
        elems.append(PageBreak())
        return elems

    # ══════════════════════════════════════
    # Q01_1 — 첫 번째 DAG 만들기
    # ══════════════════════════════════════
    story += q(
        "01_1", "첫 번째 DAG 만들기", 5,
        "Airflow DAG 를 구성하여 Hello Airflow 문장을 출력하는 작업을 등록하세요.",
        [
            "DAG 이름은 hello_airflow_dag",
            "BashOperator 를 사용하여 \"Hello Airflow\" 출력",
            "스케줄은 매 5 분마다",
        ],
        [
            "dags/hello_airflow_dag.py",
            "실행 스크린샷 또는 실행 로그",
        ],
        [
            "DAG ID 가 hello_airflow_dag 로 정확히 등록",
            "BashOperator 사용 + bash_command 에 echo \"Hello Airflow\" 포함",
            "schedule_interval 가 5분 단위 (예: */5 * * * *)",
            "Airflow UI 에서 Task 성공 (초록 체크) 캡처 존재",
        ],
        images=["Q01_1.png"],
    )

    # ══════════════════════════════════════
    # Q01_2 — S3 에서 데이터 가져오기 (Airflow + boto3)
    # ══════════════════════════════════════
    story += q(
        "01_2", "S3 에서 데이터 가져오기 (Airflow + boto3)", 5,
        "Airflow DAG 를 구성하여 AWS S3 에 저장된 CSV 데이터를 다운로드하세요.",
        [
            "PythonOperator 사용",
            "AWS 연결은 Airflow Connection 으로 구성",
            "다운로드한 파일은 /opt/airflow/data/ 에 저장",
            "data.csv 파일 활용",
        ],
        [
            "dags/s3_download_dag.py",
            "다운로드 확인용 CSV 파일 캡처",
            "실행 스크린샷 또는 실행 로그",
        ],
        [
            "PythonOperator + boto3 (또는 S3Hook) 사용",
            "Airflow Connection 등록 (aws_default 또는 사용자 정의)",
            "/opt/airflow/data/ 경로에 data.csv 저장 확인",
            "Task 성공 + CSV 파일 존재 캡처",
        ],
        images=["Q01_2.png"],
    )

    # ══════════════════════════════════════
    # Q02_1 — Spark 에서 CSV 파일 분석하기
    # ══════════════════════════════════════
    story += q(
        "02_1", "Spark 에서 CSV 파일 분석하기", 5,
        "PySpark 를 사용하여 로컬 또는 S3 에서 가져온 CSV 파일을 분석하세요.",
        [
            "PySpark 로 로딩",
            "특정 컬럼 기준 평균값/최댓값/개수 계산",
            "결과는 콘솔 또는 파일로 출력",
        ],
        [
            "analyze_csv.py (Spark 코드)",
            "실행 결과 로그",
        ],
        [
            "SparkSession 생성 + spark.read.csv 로 로딩",
            "agg / groupBy / select 등으로 평균·최댓값·개수 계산",
            "결과 콘솔 출력 (show) 또는 파일 저장",
        ],
        images=["Q02_1.png"],
    )

    # ══════════════════════════════════════
    # Q02_2 — Airflow 로 Spark 작업 자동화하기
    # ══════════════════════════════════════
    story += q(
        "02_2", "Airflow 로 Spark 작업 자동화하기", 5,
        "Airflow DAG 를 구성하여 Spark Job 을 실행하세요.",
        [
            "SparkSubmitOperator 사용",
            "Spark 코드는 이전 미션 활용",
            "스케줄은 매 5 분마다",
        ],
        [
            "dags/run_spark_job.py",
        ],
        [
            "SparkSubmitOperator 사용",
            "application 파라미터에 Q02_1 의 .py 파일 경로 지정",
            "schedule_interval 가 5분 단위",
        ],
    )

    # ══════════════════════════════════════
    # Q03 — Airflow Variable 과 Connection 활용
    # ══════════════════════════════════════
    story += q(
        3, "Airflow Variable 과 Connection 활용", 10,
        "Airflow Variable 과 Connection 을 활용하여 재사용 가능한 DAG 구성하기.",
        [
            "PostgreSQL 연결 정보를 Connection 으로 관리",
            "대상 테이블명은 Variable 로 관리",
            "연결된 DB 에서 SELECT 쿼리 수행",
        ],
        [
            "dags/db_query_dag.py",
            "실행 스크린샷 또는 실행 로그",
        ],
        [
            "PostgresHook 또는 BaseHook.get_connection 사용",
            "Variable.get 으로 테이블명 동적 로딩",
            "SELECT 쿼리 실행 결과가 로그/캡처에 노출",
        ],
        images=["Q03.png"],
    )

    # ══════════════════════════════════════
    # Q04 — Spark UDF 적용
    # ══════════════════════════════════════
    story += q(
        4, "Spark UDF 적용", 10,
        "사용자 정의 함수(UDF)를 작성하여 특정 컬럼의 값을 가공하세요.",
        [
            "예: 이름 컬럼 → 이니셜 추출",
            "PySpark 에서 UDF 등록 후 데이터 처리",
            "처리 결과 저장",
        ],
        [
            "apply_udf.py",
            "실행 스크린샷 또는 실행 로그",
        ],
        [
            "@udf 데코레이터 또는 udf() 함수로 UDF 등록",
            "DataFrame 에 UDF 적용 (withColumn 등)",
            "결과 저장 (write.csv / write.parquet)",
        ],
        images=["Q04.png"],
    )

    # ══════════════════════════════════════
    # Q05 — Spark Streaming 실시간 로그 분석
    # ══════════════════════════════════════
    story += q(
        5, "Spark Streaming 실시간 로그 분석", 10,
        "TCP 소켓으로 들어오는 로그 데이터를 실시간 처리하세요.",
        [
            "오류 로그(예: \"ERROR\") 개수 실시간 집계",
            "결과를 콘솔에 출력",
            "Spark Structured Streaming 사용",
        ],
        [
            "stream_log_processor.py",
            "실행 스크린샷 또는 실행 로그",
        ],
        [
            "spark.readStream.format(\"socket\") 사용",
            "ERROR 필터링 + count 집계",
            "writeStream.format(\"console\") 로 출력",
        ],
        images=["Q05.png"],
    )

    # ══════════════════════════════════════
    # Q6 — Bronze (부동산 실거래가 수집)
    # ══════════════════════════════════════
    story += q(
        6, "부동산 실거래가 Bronze (API 수집)", 10,
        "국토교통부 실거래가 공개 API를 호출하여 다중 시군구의 아파트 매매 데이터를 수집하고, "
        "원본 XML을 그대로 AWS S3 bronze 영역에 저장하는 Airflow DAG를 구현하세요. "
        "본인이 직접 발급받은 data.go.kr API 키를 사용해야 합니다.",
        [
            "API 신청: <link href='https://www.data.go.kr/data/15126469/openapi.do' "
            "color='blue'><u>data.go.kr/data/15126469/openapi.do</u></link>  "
            "(국토교통부_아파트 매매 실거래가 자료)",
            "End Point: https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade",
            "필수 파라미터: serviceKey, LAWD_CD (시군구코드 5자리), DEAL_YMD (yyyyMM)",
            "DAG 이름: bronze_realestate_collect",
            "스케줄: @monthly, catchup=True (월 단위)",
            "TaskGroup 또는 dynamic task mapping 으로 6개 시군구(11680·11650·11710·11440·11170·11200) 병렬 수집",
            "BranchPythonOperator 로 응답 0건/JSON 파싱 실패 시 분기 처리",
            "S3 저장 경로: s3://realestate-홍길동/bronze/{yyyymm}/{LAWD_CD}.xml",
            "수집 task 첫 줄에 print(f'collector={본인이름}, time={datetime.now()}, lawd={LAWD_CD}') 강제",
        ],
        [
            "Q6/dags/bronze_realestate_collect.py",
            "Q6/capture/airflow_graph.png  —  TaskGroup 그래프 (6개 task 병렬 가시화)",
            "Q6/capture/s3_objects.png  —  S3 콘솔 또는 mc ls 로 저장된 6개 객체 캡처",
        ],
        [
            "TaskGroup  또는  expand  (dynamic task mapping)",
            "BranchPythonOperator",
            "boto3.put_object  또는  S3Hook.load_string",
            "data.go.kr  (API URL 호출)",
            "capture/airflow_graph.png 파일 존재",
            "capture/s3_objects.png 파일 존재",
        ],
        images=[
            "Q6_airflow_graph.png",
            "Q6_s3_objects.png",
        ],
    )

    # ══════════════════════════════════════
    # Q7 — Silver (PySpark 정제 + UDF)
    # ══════════════════════════════════════
    story += q(
        7, "부동산 실거래가 Silver (PySpark 정제 + UDF)", 10,
        "Q6 에서 적재한 raw XML 을 PySpark 로 파싱·정제하고, "
        "UDF 2개로 평당가·평형 분류 컬럼을 생성한 뒤 parquet 으로 silver 영역에 저장하세요.",
        [
            "DAG 이름: silver_realestate_transform",
            "ExternalTaskSensor 로 Q6 DAG 완료 대기",
            "spark-xml 또는 직접 XML 파싱으로 DataFrame 생성",
            "결측치 (거래금액 / 면적 NULL) row 제거",
            "거래금액 콤마·공백 제거 후 정수 변환",
            "시군구별 IQR 1.5배 밖 평당가 이상치 제거",
            "UDF (1)  price_per_pyeong:  거래금액 ÷ (전용면적 ÷ 3.3058)",
            "UDF (2)  size_category:  60 미만 소형 / 60~85 중소형 / 85~135 중대형 / 135 이상 대형",
            "출력: parquet + snappy 압축, 파티션 키 = (시군구, yyyymm)",
            "S3 경로: s3://realestate-홍길동/silver/{시군구}/yyyymm=XXXXXX/",
        ],
        [
            "Q7/dags/silver_realestate_transform.py",
            "Q7/scripts/silver_spark.py",
            "Q7/capture/spark_ui.png  —  Spark UI 4040 포트 Job 실행 화면 캡처",
            "Q7/capture/s3_silver.png  —  S3 silver 디렉토리 파티션 구조 캡처",
        ],
        [
            "ExternalTaskSensor",
            "udf  (UDF 등록 2회 이상 — @udf 데코레이터 또는 udf() 호출)",
            "approxQuantile  또는  percentile_approx  (IQR 계산)",
            "write.parquet",
            "compression='snappy'  또는  partitionBy",
            "capture/spark_ui.png 파일 존재",
            "capture/s3_silver.png 파일 존재",
        ],
        images=["Q7_s3_silver.png"],
    )

    # ══════════════════════════════════════
    # Q8 — Gold (집계 + 적재)
    # ══════════════════════════════════════
    story += q(
        8, "부동산 실거래가 Gold (집계 + PostgreSQL 적재)", 10,
        "Q7 silver 데이터를 입력으로 5종 집계를 수행하고, 결과를 PostgreSQL 5개 테이블에 적재하세요.",
        [
            "DAG 이름: gold_realestate_aggregate",
            "ExternalTaskSensor 로 Q7 DAG 완료 대기",
            "PySpark SQL 또는 DataFrame API 로 5개 집계 모두 구현:",
            "    (1) gold_realestate_district_avg  —  시군구별 평균 거래가·평당가 (월별)",
            "    (2) gold_realestate_top10  —  평당가 TOP 10 단지 (동·아파트명·평당가)",
            "    (3) gold_realestate_size_dist  —  평형 분류별 거래량 분포 (Q7 UDF 결과 활용)",
            "    (4) gold_realestate_age_avg  —  건축연식 카테고리별 평당가 (신축 0~5 / 준신축 6~15 / 구축 16+)",
            "    (5) gold_realestate_mom_change  —  전월 대비 거래량·평당가 변화율 (LAG window function)",
            "PostgreSQL 적재: write.jdbc 또는 PostgresHook.insert_rows",
            "적재 후 검증 task: 각 테이블 row count > 0 확인",
        ],
        [
            "Q8/dags/gold_realestate_aggregate.py",
            "Q8/scripts/gold_spark_sql.py",
            "Q8/capture/postgres_tables.png  —  psql \\dt 출력 (5개 gold_* 테이블 보이도록)",
            "Q8/capture/postgres_select.png  —  5개 테이블 SELECT * LIMIT 5 결과 (한 장에 모아서 캡처)",
        ],
        [
            "ExternalTaskSensor",
            "spark.sql  또는  groupBy.agg  (5개 집계 코드 존재)",
            "lag  또는  Window.partitionBy  (window function 사용)",
            "write.jdbc  또는  PostgresHook",
            "5개 테이블명 모두 코드에 존재 (district_avg, top10, size_dist, age_avg, mom_change)",
            "capture/postgres_tables.png, capture/postgres_select.png 파일 존재",
        ],
    )

    # ══════════════════════════════════════
    # [Q6·7·8 채점 요소]
    # ══════════════════════════════════════
    story += [
        Paragraph("[ Q6 · 7 · 8 채점 요소 ]", S["sec"]),
        sp(2),
        light_box([
            Paragraph(
                "•  6·7·8번을 풀 때는 <b>data.go.kr API 키, AWS access/secret key</b> 를 제출 시 빈 문자열('')로 두고 제출해 주세요.",
                S["bullet"]),
            Paragraph(
                "•  채점 시 채점자가 키를 채워서 실행했을 때 코드가 정상 동작해야 합니다.",
                S["bullet"]),
            Paragraph(
                "•  DAG 이름은 위에 명시된 대로 <b>bronze_realestate_collect</b>, "
                "<b>silver_realestate_transform</b>, <b>gold_realestate_aggregate</b> 를 따릅니다.",
                S["bullet"]),
            Paragraph(
                "•  제출 시 폴더 전체를 제출하면 채점자가 다음 명령으로 실행합니다. "
                "동작하지 않으면 0점 처리되니 반드시 확인해 주세요.",
                S["bullet"]),
            sp(1),
            Paragraph(
                "<font name='NGB' color='#4A6FA5'>docker-compose up -d</font>",
                ParagraphStyle("cmd", fontName="NGB", fontSize=10,
                               textColor=MED_BLUE, leftIndent=8*mm)),
            sp(1),
            Paragraph(
                "•  각 DAG가 위 명령으로 정상 실행되어야 해당 문제 <b>10점</b> 인정",
                S["bullet"]),
            Paragraph(
                "•  task 실패·에러·output 누락 시 해당 문제 <b>0점</b> (부분점수 없음)",
                S["bullet"]),
        ], bg=BLUE_BG),
        sp(5),
        Paragraph(
            "<b>※ Q6·Q7·Q8 통합 폴더 + docker-compose.yml 제출 안내</b>",
            S["sec_sm"]),
        sp(1),
        Paragraph(
            "Q6·Q7·Q8 은 동일한 Airflow + Spark + Postgres 환경에서 순차 실행되므로, "
            "<b>4페이지 폴더 구조와 같이</b> 하나의 통합 폴더 <b>Q6_7_8_realestate/</b> 로 묶고 "
            "<b>docker-compose.yml 을 함께 제출</b>해 주세요. "
            "채점자는 이 폴더에서 docker-compose up -d 로 실행합니다.",
            S["bullet"]),
        sp(1),
        Paragraph(
            "•  <b>docker-compose.yml 누락 시 Q6·Q7·Q8 모두 0점</b> "
            "(채점자가 환경을 구동할 수 없음)",
            S["warn_bul"]),
        PageBreak(),
    ]

    # ══════════════════════════════════════
    # Q9 — k8s nginx 배포
    # ══════════════════════════════════════
    story += q(
        9, "EC2 + k3s Nginx 배포", 10,
        "AWS EC2 인스턴스에 k3s 를 설치하고, nginx 기반 정적 안내 페이지를 Kubernetes 로 배포하세요. "
        "Q8 결과를 사람이 보기 좋게 정리한 HTML 1장을 ConfigMap 으로 mount 합니다.",
        [
            "EC2 t3.small (Ubuntu 22.04), 보안그룹: SSH(22) · HTTP(80) · NodePort(30000-32767) 인바운드 허용",
            "k3s 설치: curl -sfL https://get.k3s.io | sh -",
            "Namespace: realestate-{본인이름} (예: realestate-홍길동)",
            "ConfigMap: 02-configmap.yaml 안에 index.html 직접 작성",
            "    - HTML 본문에 본인 이름 · 기수 · Q8 결과 요약(시군구 TOP3 평당가) 포함",
            "Deployment: nginx:alpine, replicas 2, ConfigMap 을 /usr/share/nginx/html 에 mount",
            "    - livenessProbe + readinessProbe 모두 포함",
            "    - resources.requests, resources.limits 모두 명시",
            "Service: NodePort (30080)",
            "Ingress: ingressClassName: traefik (k3s 기본 내장, 별도 설치 불필요)",
        ],
        [
            "Q9/k8s/01-namespace.yaml",
            "Q9/k8s/02-configmap.yaml",
            "Q9/k8s/03-deployment.yaml",
            "Q9/k8s/04-service.yaml",
            "Q9/k8s/05-ingress.yaml",
            "Q9/capture/instance_id.png  —  curl http://169.254.169.254/latest/meta-data/instance-id 출력",
            "Q9/capture/kubectl_get_all.png  —  kubectl get all -n realestate-{본인이름} 출력",
            "Q9/capture/browser.png  —  EC2 퍼블릭IP:30080 브라우저 접속 화면 (페이지에 본인 이름 노출)",
        ],
        [
            "5개 manifest 파일 모두 존재 (01-namespace ~ 05-ingress)",
            "Namespace, ConfigMap, Deployment, Service, Ingress 리소스 각 1개 이상",
            "replicas: 2",
            "livenessProbe + readinessProbe 모두 존재",
            "resources.requests + resources.limits 모두 존재",
            "capture/instance_id.png + capture/kubectl_get_all.png + capture/browser.png 파일 존재",
        ],
        images=["Q9_browser.png", "Q9_kubectl_get_all.png", "Q9_instance_id.png"],
    )

    # ══════════════════════════════════════
    # Q10 — HPA
    # ══════════════════════════════════════
    story += q(
        10, "HPA 오토스케일링", 10,
        "Q9 에서 띄운 nginx 앱에 HPA 를 추가해서 부하 발생 시 Pod 가 자동 확장되는 것을 확인하세요.",
        [
            "k3s 는 Metrics Server 내장 — 별도 설치 불필요, kubectl top pod 바로 동작",
            "07-hpa.yaml: apiVersion autoscaling/v2",
            "    - 대상: Q9 nginx Deployment",
            "    - cpu averageUtilization: 50%",
            "    - minReplicas: 2, maxReplicas: 5",
            "load-test.sh: busybox Pod 에서 wget 무한 루프로 부하 발생",
            "    - 예: kubectl run load-gen --image=busybox --rm -it -- /bin/sh -c 'while sleep 0.01; do wget -qO- http://realestate-svc.realestate-{이름}.svc.cluster.local; done'",
            "부하 발생 후 Pod 자동 확장 확인 (replicas 2→3 이상)",
        ],
        [
            "Q10/k8s/07-hpa.yaml",
            "Q10/load-test.sh  —  busybox 부하 명령어",
            "Q10/capture/kubectl_top_pod.png  —  kubectl top pod 출력 (CPU 사용률 노출)",
            "Q10/capture/hpa_watch.png  —  kubectl get hpa -w 출력 (replicas 변화 시점)",
            "Q10/capture/hpa_describe.png  —  kubectl describe hpa Events 섹션 (SuccessfulRescale 포함)",
        ],
        [
            "07-hpa.yaml: apiVersion: autoscaling/v2",
            "minReplicas + maxReplicas 정의",
            "averageUtilization 또는 averageValue 정의",
            "load-test.sh 파일 존재",
            "capture/kubectl_top_pod.png + capture/hpa_watch.png + capture/hpa_describe.png 파일 존재",
        ],
        images=["Q10_hpa_watch.png", "Q10_hpa_describe.png", "Q10_kubectl_top_pod.png"],
    )

    # ══════════════════════════════════════
    # [Q9·10 채점 요소]
    # ══════════════════════════════════════
    story += [
        Paragraph("[ Q9 · 10 채점 요소 ]", S["sec"]),
        sp(2),
        light_box([
            Paragraph(
                "•  k8s 환경은 <b>AWS EC2 + k3s</b> 를 사용합니다 (k3s 는 Metrics Server · traefik Ingress 내장).",
                S["bullet"]),
            Paragraph(
                "•  채점자는 다음 절차로 실행 검증합니다:",
                S["bullet"]),
            sp(1),
            Paragraph(
                "<font name='NGB' color='#4A6FA5'>kubectl apply -f Q9/k8s/</font><br/>"
                "<font name='NGB' color='#4A6FA5'>kubectl apply -f Q10/k8s/07-hpa.yaml</font><br/>"
                "<font name='NGB' color='#4A6FA5'>bash Q10/load-test.sh</font>",
                ParagraphStyle("cmd", fontName="NGB", fontSize=10,
                               textColor=MED_BLUE, leftIndent=8*mm, leading=15)),
            sp(1),
            Paragraph(
                "•  Q9 manifest 5개 모두 정상 적용 + 브라우저 접속 응답 200 → <b>10점</b> 인정",
                S["bullet"]),
            Paragraph(
                "•  Q10 HPA scale-out (replicas 2→3 이상 변화) 발생 → <b>10점</b> 인정",
                S["bullet"]),
            Paragraph(
                "•  manifest 미동작·HPA 미발동 시 해당 문제 <b>0점</b> (부분점수 없음)",
                S["bullet"]),
            Paragraph(
                "•  본인 이름이 namespace · ConfigMap · Ingress host · 브라우저 캡처 모든 곳에 노출되어야 합니다.",
                S["bullet"]),
        ], bg=BLUE_BG),
    ]

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    print(f"생성 완료: {output}")


if __name__ == "__main__":
    build()
