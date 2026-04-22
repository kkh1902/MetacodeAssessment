# 3주차 채점기준서 — 김예진 강사님

> **채점 원칙: 문제당 0 or 10, 부분점수 없음**
> 총점 100점 (10문제 × 10점) / 감점 사유는 짧은 키워드로 작성 (20자 내외)

## 채점 방식
- 각 문제: O(10점) / X(0점) 이진 채점
- O: 문제지 요구사항 **모두** 충족 (출력 결과 일치 + 핵심 로직 구현)
- X: 하나라도 미충족 / 미제출
- 출력 결과가 동일하면 다양한 접근 방식 인정 (문제지 안내 기준)
- 감점 표기: "미제출", 또는 핵심 누락 키워드 (예: `재시도 로직 누락`, `vocab_diversity 미계산`)

## 주차 주제 / 과제 범위
LLM API 활용 심화 — TrackedLLMClient(관측성), Sampling 실험, 스트리밍, Few-shot, Stepback, CoT + Self-Consistency, ToT, ReAct, 벤치마크까지 10문항.

---

## 문제 1: TrackedLLMClient — Observability 시스템

**배점**: 10점
**대상 클래스**: `TrackedLLMClient`

### O (10점) — 모두 충족
- [ ] Exponential backoff 재시도 (최대 3회, 1초/2초 대기)
- [ ] 호출별 로깅: 모델, 토큰 사용량(input/output), 레이턴시, 상태
- [ ] 누적 사용량 추적: 총 토큰, 총 비용, 호출 횟수
- [ ] `PRICE_PER_1K` 기반 비용 계산
- [ ] `get_usage_summary()` 반환: total_calls, total_input_tokens, total_output_tokens, total_cost_usd, avg_latency_ms
- [ ] 테스트 3회 호출 후 사용량 요약 출력

### X (0점) 사례
- 재시도 로직 누락
- 누적 사용량 추적 누락
- 비용 계산 누락
- summary 반환 필드 부족
- 미제출

---

## 문제 2: Sampling Parameter 실험 자동화

**배점**: 10점
**대상 함수**: `run_temperature_experiment(prompt, temperatures, n_trials=5)`

### O (10점) — 모두 충족
- [ ] temperature=[0.0, 0.3, 0.7, 1.0, 1.5] 각 5회 실행
- [ ] `unique_ratio` 계산 (고유 응답 수 / 전체)
- [ ] `avg_length` 계산 (평균 문자 수)
- [ ] `vocab_diversity` 계산 (고유 단어 / 전체 단어)
- [ ] 결과 dict 구조 `{temp: {unique_ratio, avg_length, vocab_diversity, responses}}`

### X (0점) 사례
- 3가지 지표 중 하나라도 미계산
- max_tokens=150 미사용 (문제지 명시)
- 반환 구조 불일치
- 미제출

---

## 문제 3: Top-p × Temperature 교차 실험

**배점**: 10점
**대상 함수**: `cross_experiment(prompt, temperatures, top_ps, n_trials=5)`

### O (10점) — 모두 충족
- [ ] `itertools.product`로 2×2 조합 (temp × top_p) 실험
- [ ] 각 조합별 5회 생성, max_tokens=200
- [ ] `avg_tokens` 계산 (output 토큰 수 평균)
- [ ] `vocab_diversity` 계산
- [ ] 결과 키: `(temp, tp)` 튜플

### X (0점) 사례
- avg_tokens 또는 vocab_diversity 누락
- output 토큰 수 수집 누락 (문자열 길이로 대체)
- 2×2 매트릭스 미구성
- 미제출

---

## 문제 4: 스트리밍 응답 + 금칙어 실시간 필터

**배점**: 10점
**대상 함수**: `stream_with_filter(prompt, forbidden_words, max_tokens=500)`

### O (10점) — 모두 충족
- [ ] OpenAI `stream=True`로 스트리밍 호출
- [ ] TTFT(첫 토큰 시간) 기록
- [ ] `tokens_per_sec` 계산
- [ ] `total_ms` 계산
- [ ] 금칙어 감지 시 즉시 중단 + `stopped_by_filter=True`, `trigger_word` 기록
- [ ] 반환 dict 필드 모두 채움 (text, stopped_by_filter, trigger_word, ttft_ms, total_ms, tokens_per_sec, token_count)

### X (0점) 사례
- stream=True 미사용
- TTFT 미측정
- 금칙어 감지 후 중단 누락
- trigger_word 기록 누락
- 미제출

---

## 문제 5: DynamicFewShotSelector + Class Mixing

**배점**: 10점
**대상 클래스**: `DynamicFewShotSelector`

### O (10점) — 모두 충족
- [ ] `_compute_similarity`: Jaccard 유사도 (intersection/union)
- [ ] `_select_top_k`: 12개 풀에서 유사도 상위 K개 선택
- [ ] `_apply_class_mixing`: 동일 클래스 3개 연속 방지 재배치
- [ ] `build_prompt`: "리뷰: ... / 감성: ..." 포맷 + 마지막 query 추가
- [ ] 프롬프트에 POSITIVE/NEUTRAL/NEGATIVE 분류 지시 포함

### X (0점) 사례
- Jaccard 아닌 다른 유사도 사용 (문제지 명시 위반)
- class mixing 로직 누락
- 최종 프롬프트 포맷 불일치
- 미제출

---

## 문제 6: Stepback Prompting + LLM-as-Judge

**배점**: 10점
**대상 함수**: `stepback_pipeline(question)`

### O (10점) — 모두 충족
- [ ] Standard 답변 생성 (직접 답변)
- [ ] Stepback question 생성 (상위 배경 질문)
- [ ] Stepback answer 생성
- [ ] Stepback 답변을 컨텍스트로 최종 답변 생성
- [ ] LLM-as-Judge JSON 평가: `score_A`, `score_B`, `winner`, `reason` 파싱
- [ ] 반환 dict 5개 필드 (stepback_question, stepback_answer, final_answer, standard_answer, judge_result)

### X (0점) 사례
- 3단계 중 하나라도 누락
- Judge 호출 누락 또는 JSON 파싱 실패
- 반환 필드 부족
- 미제출

---

## 문제 7: CoT + Self-Consistency 통합

**배점**: 10점
**대상 함수**: `zero_shot_cot`, `few_shot_cot`, `self_consistency`, `extract_answer`

### O (10점) — 모두 충족
- [ ] `zero_shot_cot`: "단계별로 생각해봅시다" 프롬프트 사용
- [ ] `few_shot_cot`: `COT_DEMOS` 포함 프롬프트
- [ ] `self_consistency`: N=7, temperature=0.8, 다수결
- [ ] `extract_answer`: regex로 "### 최종 정답:" 뒤 값 추출
- [ ] 3개 PROBLEMS에 대한 비교 표 출력 + confidence 계산

### X (0점) 사례
- Self-Consistency 샘플링 횟수 N≠7 또는 temperature≠0.8
- 다수결 로직 누락
- `extract_answer` 미구현
- 미제출

---

## 문제 8 (킬러): Tree of Thoughts 플래너

**배점**: 10점
**대상 함수**: `tree_of_thoughts(problem, n_initial=3, n_expand=2)`

### O (10점) — 모두 충족
- [ ] Step 1: 초기 전략 3개 생성 (temperature=0.9)
- [ ] Step 2: 각 전략 1-10점 평가 (regex로 점수 파싱)
- [ ] Step 3: 상위 2개 전략 확장 (주차별 실행 계획 추가)
- [ ] Step 4: 확장 전략 재평가
- [ ] Step 5: 최고 점수 전략 선택
- [ ] 반환: initial_strategies, initial_scores, expanded_strategies, final_scores, best_strategy, best_score

### X (0점) 사례
- 초기 전략 수 ≠ 3 또는 확장 수 ≠ 2
- 점수 파싱 실패 (regex 누락)
- 상위 선택 로직 오류
- 확장 단계 누락
- 미제출

---

## 문제 9 (킬러): ReAct 에이전트

**배점**: 10점
**대상 함수**: `parse_action(text)`, `react_agent(question, max_steps=5)`

### O (10점) — 모두 충족
- [ ] `parse_action`: regex로 `Action: tool_name(argument)` 파싱, `(tool_name, argument)` 반환
- [ ] Thought/Action/Observation 루프 구현
- [ ] 3개 도구 연동 (search, calculate, lookup_date)
- [ ] `Final Answer:` 감지 시 루프 종료 후 반환
- [ ] Observation을 messages에 추가하여 다음 턴 전달
- [ ] `max_steps=5` 제한

### X (0점) 사례
- Action 파싱 누락
- 도구 실행 누락 (TOOLS dict 미사용)
- Observation 피드백 루프 누락
- Final Answer 탐지 누락
- 미제출

---

## 문제 10 (킬러): PromptBenchmark 시스템

**배점**: 10점
**대상 클래스**: `PromptBenchmark`

### O (10점) — 모두 충족
- [ ] 4가지 전략 구현: Zero-shot, Few-shot(다른 TC 2개 활용), CoT, Self-Consistency(N=5)
- [ ] ROUGE-L F1 계산 (`rouge_scorer` 활용)
- [ ] LLM-as-Judge 1-10점 평가
- [ ] 전략별 토큰/비용 누적 (Judge 호출 제외)
- [ ] `Combined = (avg_rouge_l + avg_judge/10) / 2` 계산
- [ ] `Quality/$ = Combined / total_cost_usd` 계산
- [ ] 리더보드 정렬 기준: **Quality/$ 1위**
- [ ] 추천 전략 = Quality/$ 1위 전략명 출력
- [ ] 리더보드 컬럼: Rank | Strategy | ROUGE-L | Judge | Combined | Cost($) | Quality/$

### X (0점) 사례
- 4가지 전략 중 하나라도 누락
- Quality/$ 계산 누락 (Combined 1위만 출력)
- 비용 단가 사용 오류 (gpt-4o-mini: input $0.00015, output $0.0006 per 1K)
- 리더보드 정렬 기준이 Combined 등 다른 지표
- 미제출

---

## 공통 0점 조건
- 실행 불가 코드 제출
- OpenAI API 키 미설정으로 호출 실패
- 요구된 출력 형식/필드 누락
- 미제출

## 참조
- 문제지: `문제지/3주차_LLM_API_문제지.ipynb`
- 정답지(참조용): `정답지/` 하위 파일 (있을 경우)
