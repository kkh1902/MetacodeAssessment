#!/usr/bin/env python3
"""10주차 주관식 문제지 v2 — 10문제 × 2문제 = 총 20문제 (100점 만점)"""

from reportlab.platypus import Image as RLImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

# ── Fonts ──
FONT_DIR = os.path.expanduser("~/.fonts")
pdfmetrics.registerFont(TTFont("NanumGothic", os.path.join(FONT_DIR, "NanumGothic.ttf")))
pdfmetrics.registerFont(TTFont("NanumGothicBold", os.path.join(FONT_DIR, "NanumGothicBold.ttf")))

# ── Colors ──
PRIMARY_RED = HexColor("#DC3545")
DARK_GRAY = HexColor("#333333")
LIGHT_GRAY = HexColor("#F8F9FA")
MEDIUM_GRAY = HexColor("#E9ECEF")
BORDER_GRAY = HexColor("#DEE2E6")
CODE_BG = HexColor("#F5F5F0")
BLUE_ACCENT = HexColor("#0D6EFD")
GREEN_BG = HexColor("#F4FBF4")
GREEN_BORDER = HexColor("#B8DDB8")
YELLOW_BG = HexColor("#FFF8E1")
YELLOW_BORDER = HexColor("#FFE082")
RED_BG = HexColor("#FFF3F3")
RED_BORDER = HexColor("#FFCCCC")
BLUE_BG = HexColor("#EEF6FF")
BLUE_BORDER = HexColor("#B7D7FF")

# ── Styles ──
S = {
    "title": ParagraphStyle("title", fontName="NanumGothicBold", fontSize=24,
                             alignment=TA_CENTER, spaceAfter=6*mm, textColor=DARK_GRAY, leading=32),
    "subtitle": ParagraphStyle("subtitle", fontName="NanumGothic", fontSize=11,
                                alignment=TA_CENTER, spaceAfter=10*mm, textColor=HexColor("#666666"), leading=16),
    "h1": ParagraphStyle("h1", fontName="NanumGothicBold", fontSize=16,
                          spaceBefore=8*mm, spaceAfter=4*mm, textColor=DARK_GRAY, leading=22),
    "h2": ParagraphStyle("h2", fontName="NanumGothicBold", fontSize=13,
                          spaceBefore=5*mm, spaceAfter=3*mm, textColor=DARK_GRAY, leading=18),
    "h3": ParagraphStyle("h3", fontName="NanumGothicBold", fontSize=11,
                          spaceBefore=3*mm, spaceAfter=2*mm, textColor=DARK_GRAY, leading=16),
    "body": ParagraphStyle("body", fontName="NanumGothic", fontSize=10,
                            spaceBefore=1*mm, spaceAfter=1*mm, textColor=DARK_GRAY, leading=16, alignment=TA_JUSTIFY),
    "bullet": ParagraphStyle("bullet", fontName="NanumGothic", fontSize=10,
                              spaceBefore=0.5*mm, spaceAfter=0.5*mm, textColor=DARK_GRAY, leading=15, leftIndent=5*mm),
    "bullet2": ParagraphStyle("bullet2", fontName="NanumGothic", fontSize=9.5,
                               spaceBefore=0.5*mm, spaceAfter=0.5*mm, textColor=DARK_GRAY, leading=14, leftIndent=10*mm),
    "code": ParagraphStyle("code", fontName="NanumGothic", fontSize=8.5,
                            spaceBefore=1*mm, spaceAfter=1*mm, textColor=DARK_GRAY, leading=13, leftIndent=5*mm, backColor=CODE_BG),
    "warning": ParagraphStyle("warning", fontName="NanumGothicBold", fontSize=10,
                               textColor=PRIMARY_RED, leading=15),
    "path": ParagraphStyle("path", fontName="NanumGothic", fontSize=8.5,
                            textColor=HexColor("#666666"), leading=13, leftIndent=5*mm),
    "check": ParagraphStyle("check", fontName="NanumGothic", fontSize=9.5,
                             spaceBefore=0.5*mm, spaceAfter=0.5*mm, textColor=DARK_GRAY, leading=14, leftIndent=5*mm),
}


# ── Helpers ──
def hr():
    return HRFlowable(width="100%", thickness=1, color=BORDER_GRAY, spaceBefore=3*mm, spaceAfter=3*mm)


def box(elements_list, bg=LIGHT_GRAY, border=BORDER_GRAY):
    inner = []
    for el in elements_list:
        inner.append(Paragraph(el, S["body"]) if isinstance(el, str) else el)
    t = Table([[inner]], colWidths=[165*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border),
        ("TOPPADDING", (0, 0), (-1, -1), 3*mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3*mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 4*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4*mm),
    ]))
    return t


def submit_box(items):
    els = []
    for title, path in items:
        els.append(Paragraph(f"<b>* {title}</b>", S["body"]))
        if path:
            els.append(Paragraph(f"  경로: {path}", S["path"]))
    return box(els)


def criteria_table(rows):
    header = ["#", "통과 조건 (코드/설명)", "통과 조건 (캡처/증빙)"]
    data = [header] + rows
    t = Table(data, colWidths=[12*mm, 75*mm, 75*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "NanumGothic"),
        ("FONTNAME", (0, 0), (-1, 0), "NanumGothicBold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 12),
        ("BACKGROUND", (0, 0), (-1, 0), MEDIUM_GRAY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2*mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 2*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2*mm),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def zero_box(extra=""):
    items = [
        Paragraph('<font color="#DC3545"><b>0점 조건 (세부문제 중 하나라도 미충족 시 해당 문제 전체 0점)</b></font>', S["warning"]),
        Paragraph("* 캡처/로그/실행결과 증빙 없음", S["bullet"]),
        Paragraph("* 수정 전/후 비교 없음", S["bullet"]),
        Paragraph("* 가설 2개 미만 (가설 요구 문제)", S["bullet"]),
        Paragraph("* 최종 원인 명확히 특정 못함", S["bullet"]),
        Paragraph("* 캡처에 <b>date &amp;&amp; hostname</b> 출력 미포함", S["bullet"]),
    ]
    if extra:
        items.append(Paragraph(f"* {extra}", S["bullet"]))
    return box(items, bg=RED_BG, border=RED_BORDER)


def p(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items, style="bullet"):
    return [Paragraph(f"* {i}", S[style]) for i in items]


# ════════════════════════════════════════════════════════════════
def build_pdf():
    output = "/home/pc/dev/metade/10week/문제지/10주차_주관식_문제지_v2.pdf"
    doc = SimpleDocTemplate(output, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    story = []

    # ╔══════════════════════════════════════╗
    # ║            COVER PAGE                ║
    # ╚══════════════════════════════════════╝
    story.append(Spacer(1, 40*mm))
    story.append(p("10주차 실전 장애 대응 시험", "title"))
    story.append(p("Docker · Kafka · Spark · Airflow · Databricks 데이터 파이프라인", "subtitle"))
    story.append(hr())

    # 시험 구조
    story.append(p("시험 구조", "h2"))
    story.append(box([
        Paragraph("<b>총 10문제 (100점 만점) | 문제당 10점</b>", S["body"]),
        Paragraph("* 각 문제는 X-1, X-2 두 개의 세부문제로 구성됩니다.", S["bullet"]),
        Paragraph('<font color="#DC3545"><b>* X-1, X-2 중 하나라도 틀리면 해당 문제 전체 0점</b></font>', S["warning"]),
        Paragraph("* 문제 1→2→3은 연계 (k8s Kafka→Spark→Airflow 파이프라인)", S["bullet"]),
        Paragraph("* 문제 6→7 / 8→9는 2개씩 연계, 문제 4, 5, 10은 독립 문제", S["bullet"]),
        Paragraph("* 연계 문제는 앞 문제에서 구축/수정한 환경을 뒤 문제에서 이어서 사용합니다.", S["bullet"]),
    ], bg=BLUE_BG, border=BLUE_BORDER))

    story.append(Spacer(1, 5*mm))

    # 제출 안내
    story.append(p("과제 제출 안내", "h2"))
    story.append(box([
        Paragraph('<font color="#DC3545"><b>아래 경우 모두 0점 처리</b></font>', S["warning"]),
        Paragraph('<font color="#DC3545">* .docx / .hwp 등 문서 파일만 단독 제출</font>', S["bullet"]),
        Paragraph('<font color="#DC3545">* 코드를 이미지(캡처/사진)로 제출</font>', S["bullet"]),
        Paragraph("반드시 아래 폴더 구조를 지켜 <b>ZIP 파일로 압축하여 제출</b>하세요.", S["body"]),
        Paragraph("* <b>각 문제 폴더(problem-X/) 전체를 포함</b>하여 ZIP으로 압축 제출", S["bullet"]),
        Paragraph("* 코드, 설정 파일, 캡처, 텍스트 증빙을 모두 폴더 안에 포함할 것", S["bullet"]),
    ], bg=RED_BG, border=RED_BORDER))

    story.append(Spacer(1, 3*mm))
    story.append(p("<b>파일명: 데엔몇기_이름_10주차.zip</b>", "body"))
    story.append(p("예시: 데엔3기_홍길동_10주차.zip", "body"))

    story.append(PageBreak())

    # 증빙 원칙
    story.append(p("증빙 원칙", "h3"))
    story.append(box([
        Paragraph("* 모든 문제는 <b>가설 → 검증 → 증명</b> 구조 강제", S["bullet"]),
        Paragraph("* 중간 결과(로그, UI 캡처, diff) 제출 필수 — 최종 결과만 제출 시 0점", S["bullet"]),
        Paragraph("* 캡처 시 반드시 <b>date &amp;&amp; hostname</b> 명령 출력 포함", S["bullet"]),
        Paragraph("  예시:", S["bullet"]),
        Paragraph("  $ date &amp;&amp; hostname", S["code"]),
        Paragraph("  Wed Apr  2 09:13:42 KST 2025", S["code"]),
        Paragraph("  ubuntu-de-lab", S["code"]),
    ], bg=YELLOW_BG, border=YELLOW_BORDER))

    story.append(Spacer(1, 5*mm))

    # 제출물 공통 구조
    story.append(p("제출물 공통 구조 (모든 문제 동일)", "h3"))
    story.append(box([
        Paragraph("1. 문제 재현 결과 (실패 상태 캡처)", S["bullet"]),
        Paragraph("2. 실패 로그 (관련 로그 라인 인용)", S["bullet"]),
        Paragraph("3. 원인 가설 2개 이상", S["bullet"]),
        Paragraph("4. 실제 원인 특정 + 근거", S["bullet"]),
        Paragraph("5. 수정 내용", S["bullet"]),
        Paragraph("6. 수정 후 결과 (성공 상태 캡처)", S["bullet"]),
        Paragraph("7. 수정 전/후 비교", S["bullet"]),
    ], bg=GREEN_BG, border=GREEN_BORDER))

    # 캡처 예시 이미지
    story.append(Spacer(1, 3*mm))
    story.append(p("캡처 예시 (date && hostname 포함)", "h3"))
    _img_path = "/mnt/c/Users/82107/Downloads/example.png"
    if os.path.exists(_img_path):
        story.append(RLImage(_img_path, width=160*mm, height=90*mm, kind='proportional'))
    story.append(Spacer(1, 3*mm))

    story.append(PageBreak())


    # ╔══════════════════════════════════════════════════════════════════╗
    # ║   PROBLEM 1 — k8s 기반 Kafka 환경 구축 + 아키텍처 문서화           ║
    # ╚══════════════════════════════════════════════════════════════════╝
    story.append(p("문제 1: k8s 기반 Kafka 환경 구축 및 아키텍처 문서화 [10점]", "h1"))
    story.append(p("주제: k8s / Kafka 환경 구축 | 난이도: 중급", "body"))
    story.append(hr())

    story.append(p("상황", "h2"))
    story.append(box([
        Paragraph("실시간 주식 데이터 수집 시스템에 <b>백필 기능이 도입</b>됩니다.", S["body"]),
        Paragraph("* Kafka cluster를 k8s(k3d) 위에 구축하고 메시지를 발행합니다", S["bullet"]),
        Paragraph("* 백필이 추가된 아키텍처를 문서화합니다", S["bullet"]),
        Paragraph("* 멀티노드 환경, 포트: 30092-30094(kafka), 30095(kafka-ui), 30097(airflow)", S["bullet"]),
    ]))

    story.append(Spacer(1, 3*mm))

    story.append(p("1-1: 아키텍처 다이어그램", "h2"))
    story.append(p("Excalidraw로 아키텍처 다이어그램을 작성하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "Excalidraw로 아키텍처 다이어그램 작성",
        "포함 요소: Kafka 토픽(실시간/백필 분리), 데이터 수집기(실시간/백필), Spark, Airflow DAG, 알림시스템, 모니터링",
        "백필 도입 전/후 차이 설명 + 데이터 흐름 방향 명시",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["1-1", "다이어그램 완성도\n+ 구성요소 7가지 모두 포함", "아키텍처 다이어그램 캡처"],
    ]))

    story.append(Spacer(1, 3*mm))

    story.append(p("1-2: Kafka cluster k8s 설치 및 메시지 발행", "h2"))
    story.append(p(
        "k3d 멀티노드 환경에 Kafka cluster를 배포하고, producer.py를 로컬에서 실행하여 k3d 내부 Kafka로 메시지를 전송하시오.",
        "body"
    ))

    story.append(p("요구사항", "h3"))
    for item in [
        "k3d 멀티노드 환경에 Kafka cluster 배포 (yaml 전체 소스)",
        "producer.py 로컬 실행 → k3d 내부 Kafka로 전송",
        "토픽: user-events, 메시지: {'user_id': ..., 'event': ..., 'timestamp': ...}",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["1-2", "Kafka cluster yaml 제출\n+ producer.py 소스 제출", "Kafka UI(localhost:30095)\n메시지 목록 캡처"],
    ]))

    story.append(p("제출물", "h2"))
    story.append(submit_box([
        ("아키텍처 다이어그램 (.excalidraw 파일)", "problem-1/answer/updated_architecture.excalidraw"),
        ("아키텍처 다이어그램 캡처", "problem-1/answer/updated_architecture.png"),
        ("Kafka cluster yaml", "problem-1/answer/kafka-cluster.yaml"),
        ("단계별 실행 캡처", "problem-1/answer/kafka_setup.png"),
        ("Kafka UI 메시지 목록", "problem-1/answer/kafka_ui_messages.png"),
    ]))

    story.append(Spacer(1, 3*mm))
    story.append(zero_box("아키텍처 다이어그램 미제출, 구성요소 3개 이상 누락, Kafka UI 캡처 미제출"))

    story.append(PageBreak())

    # ╔══════════════════════════════════════════════════════╗
    # ║   PROBLEM 2 — PySpark 배치로 Kafka → PostgreSQL 저장  ║
    # ╚══════════════════════════════════════════════════════╝
    story.append(p("문제 2: PySpark 배치로 Kafka → PostgreSQL 저장 [10점]", "h1"))
    story.append(p("주제: Spark / 데이터 파이프라인 | 난이도: 중급", "body"))
    story.append(hr())

    story.append(p("상황", "h2"))
    story.append(box([
        Paragraph("문제 1에서 구축한 Kafka에서 메시지를 <b>spark-operator PySpark 배치 job</b>으로 읽어 PostgreSQL에 저장합니다.", S["body"]),
        Paragraph("* 테이블명: user_events_stream", S["bullet"]),
        Paragraph("* 매 실행 시 테이블 삭제 후 재생성", S["bullet"]),
    ]))

    story.append(Spacer(1, 3*mm))

    story.append(p("2-1: SparkApplication 배치 job 실행", "h2"))
    story.append(p(
        "spark-operator로 SparkApplication을 배포하고, user_events_stream 테이블에 Kafka 메시지를 적재하시오.",
        "body"
    ))

    story.append(p("요구사항", "h3"))
    for item in [
        "spark-operator로 SparkApplication 배포",
        "user_events_stream 테이블에 Kafka 메시지 적재",
        "yaml 기반 전체 소스코드 + 실행 과정 제출",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["2-1", "SparkApplication yaml 제출\n+ PySpark 소스 제출", "spark-operator 실행 캡처\n+ PostgreSQL 테이블 데이터 캡처"],
    ]))

    story.append(p("제출물", "h2"))
    story.append(submit_box([
        ("SparkApplication yaml", "problem-2/answer/kafka-to-postgres-batch.yaml"),
        ("PySpark 배치 스크립트", "problem-2/answer/consume_kafka_to_postgres_batch.py"),
        ("spark-operator 실행 캡처", "problem-2/answer/spark_application_run.png"),
        ("PostgreSQL 테이블 데이터 캡처", "problem-2/answer/postgres_table.png"),
    ]))

    story.append(Spacer(1, 3*mm))
    story.append(zero_box("spark-operator 미사용, PostgreSQL 테이블 캡처 미제출"))

    story.append(PageBreak())

    # ╔══════════════════════════════════════════════════════╗
    # ║   PROBLEM 3 — Airflow로 Spark 배치 자동화              ║
    # ╚══════════════════════════════════════════════════════╝
    story.append(p("문제 3: Airflow로 Spark 배치 자동화 [10점]", "h1"))
    story.append(p("주제: Airflow / 오케스트레이션 | 난이도: 중급", "body"))
    story.append(hr())

    story.append(p("상황", "h2"))
    story.append(box([
        Paragraph("문제 2의 Spark 배치 작업을 <b>Airflow DAG으로 자동화</b>합니다. SparkKubernetesOperator 사용.", S["body"]),
        Paragraph("* 실행 시마다 테이블에 데이터 추가 적재", S["bullet"]),
        Paragraph("* Airflow UI: localhost:30097", S["bullet"]),
    ]))

    story.append(Spacer(1, 3*mm))

    story.append(p("3-1: Airflow DAG 구성 및 실행", "h2"))
    story.append(p(
        "SparkKubernetesOperator로 DAG를 작성하고, DAG 실행 후 PostgreSQL 테이블 데이터 추가 적재를 확인하시오.",
        "body"
    ))

    story.append(p("요구사항", "h3"))
    for item in [
        "SparkKubernetesOperator로 DAG 작성",
        "DAG 실행 후 PostgreSQL 테이블 데이터 추가 적재 확인",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["3-1", "SparkKubernetesOperator\nDAG 소스 제출", "Airflow DAG 실행 화면\n+ 테이블 데이터 재집계 캡처"],
    ]))

    story.append(Spacer(1, 3*mm))

    story.append(p("3-2: 실행 증적 비교", "h2"))
    story.append(p(
        "spark-operator 직접 실행 1건 + Airflow를 통한 실행 1건 = 총 2건을 제출하시오.",
        "body"
    ))

    story.append(p("요구사항", "h3"))
    for item in [
        "spark-operator 직접 실행 1건 + Airflow 통한 실행 1건 = 총 2건 제출",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["3-2", "SparkApplication 실행 캡처\n총 2건 제출", "직접 실행 1건\n+ Airflow 실행 1건"],
    ]))

    story.append(p("제출물", "h2"))
    story.append(submit_box([
        ("Airflow DAG 파일", "problem-3/answer/kafka_to_postgres_dag.py"),
        ("Airflow DAG 실행 화면", "problem-3/answer/airflow_dag_run.png"),
        ("PostgreSQL 테이블 적재 후 캡처", "problem-3/answer/postgres_table_after.png"),
        ("spark-operator 직접 실행 캡처", "problem-3/answer/spark_direct_run.png"),
        ("spark-operator 직접 실행 로그 (kubectl logs)", "problem-3/answer/spark_direct_log.txt"),
        ("Airflow 통한 실행 캡처", "problem-3/answer/spark_airflow_run.png"),
        ("Airflow 통한 실행 로그 (kubectl logs)", "problem-3/answer/spark_airflow_log.txt"),
    ]))

    story.append(Spacer(1, 3*mm))
    story.append(zero_box("SparkKubernetesOperator 미사용, 실행 캡처 2건 미만"))

    # ╔══════════════════════════════════════════════════════╗
    # ║   PROBLEM 1 — Kafka GC Cascade (docker-compose)     ║
    # ╚══════════════════════════════════════════════════════╝
    story.append(p("문제 4: 침묵하는 브로커 — Kafka GC Cascade 진단 및 복구 [10점]", "h1"))
    story.append(p("주제: 분산 시스템 장애 진단 | 난이도: 심화", "body"))
    story.append(hr())

    story.append(p("상황", "h2"))
    story.append(box([
        Paragraph("제공된 docker-compose.yaml을 실행하면 <b>Spark job이 간헐적으로 실패</b>합니다.", S["body"]),
        Paragraph("* docker ps 상 모든 컨테이너 Up 상태", S["bullet"]),
        Paragraph("* Spark 로그에 LeaderNotAvailableException 반복", S["bullet"]),
        Paragraph("* Kafka broker는 재시작을 반복하며 Zookeeper 연결 유실", S["bullet"]),
        Paragraph("* Zookeeper 로그에는 별다른 이상 없음", S["bullet"]),
    ]))

    story.append(Spacer(1, 3*mm))

    # 1-a
    story.append(p("4-1: Cascading Failure 원인 분석", "h2"))
    story.append(p(
        "Spark → Kafka → Zookeeper 순서로 로그를 교차 분석하여 <b>root cause 서비스와 설정값</b>을 특정하고, "
        "<b>두 설정이 어떻게 상호작용하여 cascade를 유발하는지</b> 인과관계를 설명하시오.",
        "body"
    ))

    story.append(p("요구사항", "h3"))
    for item in [
        "Spark / Kafka / Zookeeper 3개 서비스 로그 각각 캡처",
        "원인 가설 2개 이상 (각 가설에 검증 명령어 포함)",
        "실제 원인 설정값 2개 특정 + 로그 라인 인용 근거",
        "두 설정이 단독 vs 조합 시 동작 차이 설명",
        "GC pause 시간과 session timeout 수치 비교 분석",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["a-1", "3개 서비스 로그 교차 분석\n+ 가설 2개 이상", "Spark/Kafka/ZK 로그에서\n시간순 연쇄 로그 캡처"],
        ["a-2", "원인 설정값 2개 특정\n+ 단독/조합 차이 설명", "GC pause 로그 라인 +\nsession expired 로그 인용"],
    ]))

    story.append(Spacer(1, 3*mm))

    # 1-b
    story.append(p("4-2: 설정 수정 및 안정성 증명", "h2"))
    story.append(p(
        "원인이 되는 설정 <b>2개를 모두 수정</b>하고, "
        "<b>Spark job이 연속 3회 성공</b>하는 것을 증명하시오.",
        "body"
    ))

    story.append(p("요구사항", "h3"))
    for item in [
        "수정 전/후 docker-compose.yaml diff 제출",
        "수정 근거: 각 설정값을 어떤 값으로 바꿨는지 + 이유",
        "수정 후 docker-compose up 전체 서비스 healthy 캡처",
        "Spark job 연속 3회 실행 성공 로그 캡처",
        "Kafka broker 재시작 없이 안정 유지 확인 (docker ps 시계열 캡처)",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["b-1", "설정 2개 모두 수정\n+ 각 수정 근거 설명", "docker ps 전체 healthy +\nKafka 재시작 없음 캡처"],
        ["b-2", "Spark job 3회 연속 성공\n로그 제출", "GC pause 발생 시에도\nsession 유지 확인"],
    ]))

    story.append(p("제출물", "h2"))
    story.append(submit_box([
        ("3개 서비스 로그 캡처 (date && hostname 포함)", "problem-4/answer/cascade_logs.png"),
        ("3개 서비스 로그 합본 (시간순 텍스트)", "problem-4/answer/cascade_logs.txt"),
        ("원인 분석 문서 (인과관계 포함)", "problem-4/answer/root_cause_analysis.md"),
        ("수정 전/후 설정 diff", "problem-4/answer/config_diff.txt"),
        ("수정된 docker-compose 파일", "problem-4/answer/docker-compose-fix.yaml"),
        ("수정 후 전체 서비스 healthy 캡처", "problem-4/answer/services_healthy.png"),
        ("Spark job 3회 성공 로그 캡처", "problem-4/answer/spark_job_success.png"),
    ]))

    story.append(Spacer(1, 3*mm))
    story.append(zero_box("설정 1개만 수정하거나, 로그 근거 없이 수정값만 제출한 경우"))

    story.append(PageBreak())

    # ╔══════════════════════════════════════════════════════╗
    # ║   PROBLEM 2 — Spark Executor OOMKilled (k8s)         ║
    # ╚══════════════════════════════════════════════════════╝
    story.append(p("문제 5: 죽지 않는 OOM — k8s Spark Executor 메모리 진단 [10점]", "h1"))
    story.append(p("주제: k8s 리소스 관리 | 난이도: 심화", "body"))
    story.append(hr())

    story.append(p("상황", "h2"))
    story.append(box([
        Paragraph("제공된 SparkApplication을 k3d 클러스터에 배포하면 <b>executor pod이 OOMKilled를 반복</b>합니다.", S["body"]),
        Paragraph("* driver pod은 정상 Running", S["bullet"]),
        Paragraph("* executor pod만 반복 OOMKilled (Exit Code 137)", S["bullet"]),
        Paragraph("* memory 설정값이 존재함에도 계속 실패", S["bullet"]),
        Paragraph("* 버그가 2개 존재하며, 하나만 수정하면 여전히 실패함", S["bullet"]),
    ]))

    story.append(Spacer(1, 3*mm))

    # 2-a
    story.append(p("5-1: OOMKilled 원인 분석", "h2"))
    story.append(p(
        "kubectl 명령어로 실측 데이터를 수집하고, <b>OOMKilled를 유발하는 설정 버그 2개</b>를 특정하여 "
        "<b>각각의 원인과 상호작용</b>을 수치 근거와 함께 설명하시오.",
        "body"
    ))

    story.append(p("요구사항", "h3"))
    for item in [
        "kubectl describe pod으로 OOMKilled 이벤트 및 limits 확인 캡처",
        "kubectl top pod으로 실제 메모리 사용량 수집 캡처",
        "JVM이 인식하는 max heap 크기 확인 (java -XshowSettings:vm)",
        "원인 버그 2개 각각 특정 + 수치 근거 (계산식 포함)",
        "버그 2개가 단독 vs 조합 시 동작 차이 설명",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["a-1", "kubectl 실측 데이터 수집\n(describe + top + JVM settings)", "OOMKilled 이벤트 +\n실측 메모리 사용량 캡처"],
        ["a-2", "버그 2개 특정\n+ 수치 계산식 포함", "JVM heap 크기 vs\ncontainer limits 비교 캡처"],
    ]))

    story.append(Spacer(1, 3*mm))

    # 2-b
    story.append(p("5-2: 설정 수정 및 executor 안정화 증명", "h2"))
    story.append(p(
        "버그 <b>2개를 모두 수정</b>하고, executor가 <b>OOMKilled 없이 정상 완료</b>되는 것을 증명하시오.",
        "body"
    ))

    story.append(p("요구사항", "h3"))
    for item in [
        "수정 전/후 spark-application.yaml diff 제출",
        "각 수정값 근거 설명 (왜 그 값인지 계산 과정 포함)",
        "수정 후 executor pod Running → Completed 상태 캡처",
        "kubectl top pod으로 수정 후 메모리 사용량이 limits 이내임을 확인",
        "SparkApplication 최종 Completed 상태 캡처",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["b-1", "설정 2개 모두 수정\n+ 각 계산 근거 포함", "executor Completed +\ntop으로 limits 이내 확인"],
        ["b-2", "SparkApplication\nCompleted 상태 캡처", "OOMKilled 재발 없이\n안정 완료 증명"],
    ]))

    story.append(p("제출물", "h2"))
    story.append(submit_box([
        ("kubectl diagnostics 캡처 (date && hostname 포함)", "problem-5/answer/kubectl_diagnostics.png"),
        ("kubectl diagnostics 텍스트", "problem-5/answer/kubectl_diagnostics.txt"),
        ("JVM settings 확인 캡처", "problem-5/answer/jvm_settings.png"),
        ("JVM settings 텍스트", "problem-5/answer/jvm_settings.txt"),
        ("원인 분석 문서 (버그 2개 + 수치 계산)", "problem-5/answer/root_cause_analysis.md"),
        ("수정 전/후 yaml diff", "problem-5/answer/config_diff.txt"),
        ("수정된 SparkApplication yaml", "problem-5/answer/spark-application-fixed.yaml"),
        ("executor Completed + top 캡처", "problem-5/answer/executor_stable.png"),
        ("executor Completed + top 텍스트", "problem-5/answer/executor_stable.txt"),
    ]))

    story.append(Spacer(1, 3*mm))
    story.append(zero_box("버그 1개만 수정하거나, 수치 계산 없이 값만 변경한 경우"))

    story.append(PageBreak())

    # ╔══════════════════════════════════════╗
    # ║   PROBLEM 3 — 멱등성 (DAG 재실행)    ║
    # ╚══════════════════════════════════════╝
    story.append(p("문제 6: DAG 멱등성 검증 [10점]", "h1"))
    story.append(p("주제: 데이터 정합성 | 난이도: 중급", "body"))
    story.append(hr())

    story.append(p("상황", "h2"))
    story.append(box([
        Paragraph("제공된 DAG를 <b>2회 이상 실행하면 데이터 중복 적재</b>가 발생합니다.", S["body"]),
        Paragraph("* late data 존재, timezone 혼재, 동일 데이터 반복 적재", S["bullet"]),
        Paragraph("* <b>중복 원인을 찾고 멱등성을 보장하도록 수정해야 합니다</b>", S["bullet"]),
    ]))

    story.append(Spacer(1, 3*mm))

    # 3-1
    story.append(p("6-1: 중복 적재 현상 재현 및 진단", "h2"))
    story.append(p("버그 DAG를 2회 이상 실행하여 <b>중복 현상을 재현하고 원인을 특정</b>하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "중복 검증 쿼리 제출 (GROUP BY + HAVING count > 1)",
        "1차/2차 실행 후 row count 비교 캡처 (수치 증가 확인)",
        "중복 원인 가설 2개 이상 + 실제 원인 특정",
        "duplicate 쿼리 결과에서 중복 row 존재 캡처",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["6-1a", "중복 검증 쿼리 제출\n(GROUP BY + HAVING count > 1)", "1차/2차 실행 후\nrow count 비교 캡처\n(수치 증가 확인)"],
        ["6-1b", "중복 원인 가설 2개 이상\n+ 실제 원인 특정", "duplicate 쿼리 결과에서\n중복 row 존재 캡처"],
    ]))

    story.append(Spacer(1, 3*mm))

    # 3-2
    story.append(p("6-2: 멱등성 보장 구현 및 검증", "h2"))
    story.append(p("원인을 수정하고, <b>동일 DAG 2회 이상 실행 시 데이터가 중복되지 않음</b>을 증명하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "dedup 전략 코드 구현 + event time 기준 처리 (processing time 아님)",
        "2회 실행 후 row count 동일 캡처",
        "idempotent 설계 논리 문서",
        "duplicate 검증 = 0건 + checksum 동일 캡처",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["6-2a", "dedup 전략 코드 구현\n+ event time 기준 처리", "2회 실행 후\nrow count 동일 캡처"],
        ["6-2b", "idempotent 설계 논리 문서", "duplicate 검증 = 0건\n+ checksum 동일 캡처"],
    ]))

    story.append(p("제출물", "h2"))
    story.append(submit_box([
        ("1차/2차 실행 row count 비교 캡처", "problem-6/answer/row_count_comparison.png"),
        ("수정 전 중복 검증 결과 캡처", "problem-6/answer/duplicates_before.png"),
        ("수정된 DAG 파일", "problem-6/answer/idempotent_dag.py"),
        ("중복 검증 쿼리", "problem-6/answer/duplicate_check.sql"),
        ("dedup 전략 설명 문서", "problem-6/answer/dedup_strategy.md"),
        ("수정 후 멱등성 검증 캡처", "problem-6/answer/idempotency_proof.png"),
    ]))

    story.append(Spacer(1, 3*mm))
    story.append(zero_box("`datetime.now()` 미수정 (event time 기준 미사용)\nDELETE-INSERT 또는 동등한 dedup 전략 미구현\ndiff 없이 '동일하다'고만 주장하는 경우"))

    story.append(PageBreak())

    # ╔══════════════════════════════════════╗
    # ║   PROBLEM 4 — 멱등성 (타임존 심화)   ║
    # ╚══════════════════════════════════════╝
    story.append(p("문제 7: 시간의 함정 — 날짜 경계 데이터 정합성 [10점]", "h1"))
    story.append(p("주제: 데이터 정합성 (심화) | 난이도: 개념", "body"))
    story.append(hr())

    story.append(p("상황", "h2"))
    story.append(box([
        Paragraph("<b>문제 3에서 수정한 파이프라인</b>을 이어서 사용합니다.", S["body"]),
        Paragraph("날짜 경계 부근에서 발행된 데이터의 <b>파티션 분포가 기대값과 다릅니다.</b>", S["body"]),
        Paragraph("* 데이터는 정상 적재되어 있음", S["bullet"]),
        Paragraph("* 특정 시간대 데이터만 파티션이 이상함", S["bullet"]),
        Paragraph("* <b>왜 이런 현상이 발생하는지는 직접 파악해야 합니다</b>", S["bullet"]),
    ]))

    story.append(Spacer(1, 3*mm))

    # 4-a
    story.append(p("7-1: 파티션 분포 이상 재현 및 원인 특정", "h2"))
    story.append(p("날짜 경계 부근 데이터를 발행하고, <b>파티션 분포가 왜 기대값과 다른지 원인을 스스로 찾아</b> 증명하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "날짜 경계 부근 데이터 100건 이상 발행 후 Spark job 실행",
        "날짜별 파티션 row count 조회 캡처 (date && hostname 포함)",
        "기대값 vs 실제값 수치 직접 제시",
        "원인 가설 2개 이상 (각 가설에 검증 방법 포함)",
        "실제 원인 특정 + 코드 라인 직접 인용",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["a-1", "날짜 경계 데이터 발행\n코드/명령어 제출", "파티션별 row count에서\n데이터 분산 확인 캡처"],
        ["a-2", "timezone 불일치 원인 특정\n+ 코드 지점 인용", "기대값 vs 실제값\n수치 비교 캡처"],
    ]))

    story.append(Spacer(1, 3*mm))

    # 4-b
    story.append(p("7-2: 수정 및 정합성 복구", "h2"))
    story.append(p("원인을 수정하고, <b>날짜 경계 데이터가 기대한 파티션에 정확히 적재</b>됨을 증명하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "수정 전/후 코드 diff",
        "수정 후 동일 데이터 재처리",
        "수정 후 파티션별 row count = 기대값 캡처",
        "수정 후 2회 실행 시 결과 동일 (멱등성 유지) 캡처",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["b-1", "수정 전/후 코드 diff\n+ 수정 이유 설명", "수정 후 파티션별\nrow count = 기대값 캡처"],
        ["b-2", "— (자동채점)", "2회 실행 후\nrow count 동일 캡처"],
    ]))

    story.append(p("제출물", "h2"))
    story.append(submit_box([
        ("수정 전 파티션 분포 캡처", "problem-7/answer/partition_before.png"),
        ("수정 전/후 코드 diff", "problem-7/answer/code_diff.txt"),
        ("수정 후 파티션 분포 캡처 (기대값 일치)", "problem-7/answer/partition_after.png"),
        ("2회 실행 후 결과 동일 증명 캡처", "problem-7/answer/idempotency_proof.png"),
    ]))

    story.append(Spacer(1, 3*mm))
    story.append(zero_box("코드 라인 인용 없이 원인만 주장하는 경우"))

    story.append(PageBreak())

    # ╔══════════════════════════════════════╗
    # ║   PROBLEM 5 — 디버깅 (Silent Fail)   ║
    # ╚══════════════════════════════════════╝
    story.append(p("문제 8: 보이지 않는 실패 — SUCCESS인데 데이터 없음 [10점]", "h1"))
    story.append(p("주제: 디버깅 / Observability | 난이도: 실무 감각", "body"))
    story.append(hr())

    story.append(p("상황", "h2"))
    story.append(box([
        Paragraph("<b>문제 3~4에서 정합성까지 확보한 파이프라인</b>을 이어서 사용합니다.", S["body"]),
        Paragraph("파이프라인의 모든 단계가 <b>SUCCESS</b>를 반환하지만, <b>최종 DB에 데이터가 없습니다.</b>", S["body"]),
        Paragraph("* Airflow DAG: SUCCESS", S["bullet"]),
        Paragraph("* Spark job: SUCCESS (exit code 0)", S["bullet"]),
        Paragraph("* PostgreSQL target 테이블: 0 rows", S["bullet"]),
    ]))

    story.append(Spacer(1, 3*mm))

    # 5-a
    story.append(p("8-1: Silent Failure 원인 추적", "h2"))
    story.append(p("각 단계의 로그를 분석하여 <b>데이터가 사라지는 정확한 지점</b>을 특정하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "Airflow SUCCESS 화면 캡처",
        "Spark job SUCCESS 로그 캡처",
        "PostgreSQL SELECT count(*) = 0 캡처",
        "데이터 흐름 각 단계 확인: Kafka offset → Spark read count → Spark write count → DB count",
        "데이터가 사라지는 지점 특정 + 로그 라인 인용",
        "원인 가설 2개 이상",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["a-1", "데이터 흐름 4단계\n각각의 count 추적", "Kafka(N) → Spark read(N)\n→ Spark write(?) → DB(0)\n수치 캡처"],
        ["a-2", "데이터 유실 지점 특정\n+ 로그 라인 인용", "가설 2개 이상\n+ 실제 원인 근거"],
    ]))

    story.append(Spacer(1, 3*mm))

    # 5-b
    story.append(p("8-2: 수정 및 데이터 적재 증명", "h2"))
    story.append(p("원인을 수정하고, <b>파이프라인 실행 후 DB에 데이터가 정상 적재</b>됨을 증명하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "수정 전/후 코드 diff",
        "수정 후 파이프라인 실행 결과 캡처",
        "DB target 테이블 row 존재 확인 캡처",
        "staging vs final 테이블 count 일치 확인",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["b-1", "수정 코드 diff 제출", "실행 후 DB row > 0 캡처"],
        ["b-2", "— (자동채점)", "staging count =\nfinal count 캡처"],
    ]))

    story.append(p("제출물", "h2"))
    story.append(submit_box([
        ("SUCCESS인데 0건 증명 (로그+쿼리)", "problem-8/answer/success_but_empty.txt"),
        ("데이터 흐름 추적 (단계별 count)", "problem-8/answer/data_flow_trace.txt"),
        ("원인 분석 문서", "problem-8/answer/silent_failure_analysis.md"),
        ("수정 전/후 코드 diff", "problem-8/answer/code_diff.txt"),
        ("수정 후 DB 적재 증명", "problem-8/answer/data_loaded.txt"),
    ]))

    story.append(Spacer(1, 3*mm))
    story.append(zero_box("'~인 것 같다' 수준의 추정만 있고 로그 인용이 없는 경우"))

    story.append(PageBreak())

    # ╔══════════════════════════════════════╗
    # ║   PROBLEM 6 — 디버깅 (로그 트랩)     ║
    # ╚══════════════════════════════════════╝
    story.append(p("문제 9: 로그의 거짓말 — 불완전 로그 속 진짜 원인 찾기 [10점]", "h1"))
    story.append(p("주제: 디버깅 / Observability (심화) | 난이도: 실무 감각", "body"))
    story.append(hr())

    story.append(p("상황", "h2"))
    story.append(box([
        Paragraph("<b>문제 5에서 데이터 적재를 복구한 파이프라인</b>을 이어서 사용합니다.", S["body"]),
        Paragraph("Spark job이 <b>간헐적으로 실패</b>합니다. 로그에는 여러 에러가 섞여 있습니다.", S["body"]),
        Paragraph("* 10회 실행 중 3~4회 실패", S["bullet"]),
        Paragraph("* 에러 로그: ConnectionTimeout, OOM, TaskNotSerializable 혼재", S["bullet"]),
        Paragraph("* 실패 시점마다 에러 메시지가 다름", S["bullet"]),
        Paragraph("* <b>일부 로그는 의도적으로 누락/오도용으로 삽입됨 (로그 트랩)</b>", S["bullet"]),
    ]))

    story.append(Spacer(1, 3*mm))

    # 6-a
    story.append(p("9-1: 로그 분류 및 진짜 원인 식별", "h2"))
    story.append(p("제공된 로그 파일에서 <b>관련 로그 vs 무관 로그를 분류</b>하고, <b>root cause를 특정</b>하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "제공된 로그 파일에서 에러 라인 전체 목록 추출",
        "각 에러를 '관련(relevant)' / '무관(irrelevant)' 로 분류 + 분류 근거",
        "무관 로그를 배제한 이유 설명",
        "원인 가설 2개 이상",
        "실제 root cause 특정 + 로그 시계열 분석 (어떤 에러가 먼저 발생했는지)",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["a-1", "에러 분류표 제출\n(relevant / irrelevant\n+ 각 분류 근거)", "로그 파일에서\n에러 라인 추출 캡처"],
        ["a-2", "root cause 특정\n+ 시계열 분석", "가설 2개 이상\n+ 배제 논리"],
    ]))

    story.append(Spacer(1, 3*mm))

    # 6-b
    story.append(p("9-2: 수정 및 안정성 증명", "h2"))
    story.append(p("root cause를 수정하고, <b>5회 연속 실행 시 실패 0회</b>를 증명하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "수정 전/후 코드 diff",
        "수정 후 5회 연속 실행 결과 캡처 (각 실행 시각 포함)",
        "5회 모두 SUCCESS 확인",
        "수정이 root cause를 해결하는 이유 설명",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["b-1", "수정 코드 diff +\n수정 이유 설명", "5회 실행 결과 캡처\n(시각 포함)"],
        ["b-2", "— (자동채점)", "5회 모두 SUCCESS\n(실패 0건)"],
    ]))

    story.append(p("제출물", "h2"))
    story.append(submit_box([
        ("에러 분류표", "problem-9/answer/error_classification.md"),
        ("원인 분석 문서", "problem-9/answer/root_cause_analysis.md"),
        ("수정된 Spark 코드", "problem-9/answer/spark_job_fixed.py"),
        ("수정 전/후 코드 diff", "problem-9/answer/code_diff.txt"),
        ("5회 연속 실행 성공 (txt)", "problem-9/answer/five_runs_success.txt"),
        ("5회 연속 실행 성공 (캡처)", "problem-9/answer/five_runs_success.png"),
    ]))

    story.append(Spacer(1, 3*mm))
    story.append(zero_box("로그 분류 없이 바로 수정만 제출한 경우"))

    story.append(PageBreak())

    # ╔══════════════════════════════════════╗
    # ║  PROBLEM 10 — Databricks 성능 최적화 ║
    # ╚══════════════════════════════════════╝
    story.append(p("문제 10: 클라우드 탈출 — Databricks 성능 최적화 [10점]", "h1"))
    story.append(p("주제: Spark 성능 + Databricks | 난이도: 심화", "body"))
    story.append(hr())

    story.append(p("상황", "h2"))
    story.append(box([
        Paragraph("제공된 <b>generate_data.py</b>로 sales_raw.parquet (200만 건, user_id=999에 50% skew)를 생성 후 Databricks DBFS에 업로드하여 집계 job을 실행합니다.", S["body"]),
        Paragraph("* 반드시 공통 초기 설정(num_workers=2, shuffle.partitions=200, AQE 비활성)으로 먼저 실행", S["bullet"]),
        Paragraph("* 튜닝 후 실행 시간 40% 이상 단축 목표", S["bullet"]),
    ]))

    story.append(Spacer(1, 3*mm))

    # 10-1
    story.append(p("10-1: Databricks Cluster 구성 및 기본 실행", "h2"))
    story.append(p("<b>공통 초기 설정</b>(num_workers=2, shuffle.partitions=200)으로 notebook을 실행하고 결과와 실행 시간을 기록하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "generate_data.py 실행 → sales_raw.parquet 생성 → DBFS 업로드",
        "공통 초기 설정(num_workers=2, partitions=200, AQE off)으로 실행",
        "결과 row count 명시 + Spark UI Jobs 탭 실행 시간 기록",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["10-1a", "공통 초기 설정 그대로 실행\n+ cluster 설정 명시", "Databricks cluster\n설정 화면 캡처"],
        ["10-1b", "notebook 실행 성공\n+ row count + 실행 시간 기록", "Spark UI Jobs 탭\n실행 결과 캡처"],
    ]))

    story.append(Spacer(1, 3*mm))

    # 10-2
    story.append(p("10-2: 클러스터 튜닝 및 전/후 비교", "h2"))
    story.append(p("cluster 설정을 최적화하고, <b>튜닝 전 대비 40% 이상 실행 시간 단축</b>을 수치로 증명하시오.", "body"))

    story.append(p("요구사항", "h3"))
    for item in [
        "config 변경 목록 + 각 변경 이유 (num_workers, shuffle.partitions, AQE, executor.memory 4가지 이상)",
        "튜닝된 notebook 제출",
        "Spark UI Stage 상세 전/후 캡처 (shuffle read, task skew 수치 포함)",
        "개선율(%) = (튜닝 전 시간 - 튜닝 후 시간) / 튜닝 전 시간 × 100 직접 계산 → 40% 이상",
    ]:
        story.append(p(f"* {item}", "bullet"))

    story.append(p("평가 기준", "h3"))
    story.append(criteria_table([
        ["10-2a", "config 변경 목록\n+ 각 변경 이유 (4가지 이상)", "Spark UI Stage 전/후 캡처\n(shuffle read 수치 포함)"],
        ["10-2b", "개선율 계산 + 40% 이상 달성", "실행 시간 전/후\n비교표 캡처"],
    ]))

    story.append(p("제출물", "h2"))
    story.append(submit_box([
        ("Databricks cluster 설정 캡처 (튜닝 전)", "problem-10/answer/cluster_config.png"),
        ("notebook 파일 (기본)", "problem-10/answer/notebook.py"),
        ("notebook 실행 결과 캡처 (튜닝 전)", "problem-10/answer/notebook_result.png"),
        ("튜닝된 notebook", "problem-10/answer/notebook_tuned.py"),
        ("튜닝 전/후 Spark UI 캡처", "problem-10/answer/databricks_spark_ui.png"),
        ("성능 비교 문서 (변경 이유 + 개선율)", "problem-10/answer/performance_tuning.md"),
    ]))

    story.append(Spacer(1, 3*mm))
    story.append(zero_box("generate_data.py 미사용 (다른 데이터셋으로 실행한 경우)\n공통 초기 설정(num_workers=2, partitions=200)으로 튜닝 전 실행 캡처 미제출\nDatabricks 환경 미사용 (로컬에서만 실행한 경우)\n튜닝 이유 설명 없이 config만 변경한 경우\n성능 개선율 40% 미만 또는 수치 계산 없음"))



    # ── Footer: 저작권 고지 (모든 페이지 하단) ──
    PAGE_W, PAGE_H = A4

    def draw_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("NanumGothic", 7)
        canvas.setFillColor(HexColor("#888888"))
        text = "© 메타코드 | 본 자료는 수강생 본인만 열람 가능합니다. 외부 유출·공유·재배포를 엄격히 금지하며, 위반 시 저작권법 제136조에 의거하여 법적 조치가 취해질 수 있습니다."
        canvas.drawCentredString(PAGE_W / 2, 10 * mm, text)
        canvas.restoreState()

    # Build
    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    print(f"PDF generated: {output}")






if __name__ == "__main__":
    build_pdf()
