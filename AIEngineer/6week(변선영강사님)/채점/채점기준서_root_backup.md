# 6주차 채점기준서 — 변선영 강사님

> **채점 원칙: 문제당 0 or 10, 부분점수 없음**
> 총점 100점 (10문제 × 10점) / 감점 사유는 짧은 키워드로 작성 (20자 내외)

## 채점 방식
- 각 문제: O(10점) / X(0점) 이진 채점
- O: 문제지 요구사항 **모두** 충족
- X: 하나라도 미충족 / 미제출
- 감점 표기: "미제출", 또는 핵심 누락 키워드 (예: `top_p 미설정`, `CoT 유도 없음`)

## 주차 주제 / 과제 범위
프롬프트 엔지니어링 / 디코딩 / 평가지표 — 결정론적 디코딩, Few-shot, 자가교정(self-correction), JSON 추출, CoT, ROUGE/BLEU, BERTScore, Contrastive Decoding, DSPy, Self-Correction 루프까지 10문항. 주관식·빈칸 채우기 중심.

---

## 문제 1: 데이터 추출 에이전트의 디코딩 최적화

**배점**: 10점
**대상 함수**: `get_extraction_config()`

### O (10점) — 모두 충족
- [ ] `temperature: 0.0` (무작위성 제거)
- [ ] `top_p`를 결정론적 디코딩에 맞게 설정 (0.0 또는 극단값)
- [ ] `presence_penalty: 0.0`
- [ ] 주석의 의도(Greedy Search와 유사) 준수
- [ ] 실제 호출 시 JSON 파싱 성공

### X (0점) 사례
- temperature > 0
- 파라미터 값 임의 변경으로 결정론성 상실
- config dict 반환 구조 변경
- 미제출

---

## 문제 2: Few-shot 구조적 데이터 추출

**배점**: 10점
**대상 함수**: `extract_entities_with_few_shot(news_text)`

### O (10점) — 모두 충족
- [ ] `FEW_SHOT_EXAMPLES`에 **최소 2개 이상** 예시 작성 (user/assistant 쌍)
- [ ] 각 예시의 assistant 응답이 **순수 JSON만** (설명 텍스트 없음)
- [ ] 출력 포맷: `[{"person": "...", "org": "..."}]` 리스트 형태
- [ ] system 메시지로 역할/형식 지시
- [ ] 테스트 문장 "이순신/조선 수군" 기대 출력 구조에 부합

### X (0점) 사례
- Few-shot 예시 누락 또는 1개만
- 예시 assistant 응답에 설명 텍스트 포함 (zero-shot 실패 사례와 동일)
- 출력이 dict 단일 형태 (리스트 아님)
- 미제출

---

## 문제 3: 구조화 추출 + Self-Correction 프롬프트

**배점**: 10점
**대상 함수**: `call_llm_for_extraction(text, error_message=None)`

### O (10점) — 모두 충족
- [ ] system_prompt에 역할(JSON 추출기) + 출력 규칙(JSON만, 설명 없음) 명시
- [ ] 첫 시도 user_content: 입력 text로 추출 요청
- [ ] 재시도 시 user_content: error_message 포함하여 교정 지시
- [ ] `required_fields`(store_name, date, items, total_amount) 충족
- [ ] `total_amount`가 int 타입
- [ ] `date`는 `"2024-03-15"` 포맷
- [ ] 최종 자동채점 100점 달성

### X (0점) 사례
- error_message 분기 미구현 (항상 동일 프롬프트)
- 필수 필드 누락으로 검증 실패
- total_amount 타입 오류 (문자열)
- 날짜 포맷 불일치
- 자동채점 75점 이하
- 미제출

---

## 문제 4: 감성 분석 JSON 프롬프트 e2e

**배점**: 10점
**대상 변수**: `prompt` (system prompt)

### O (10점) — 모두 충족
- [ ] 프롬프트에 "JSON만 출력" 지시 포함
- [ ] sentiment 값 제한: `positive`/`negative`/`neutral` 중 하나
- [ ] reason 필드 포함 지시
- [ ] 출력 결과가 `json.loads()`로 파싱 가능
- [ ] 3개 테스트 입력(positive/neutral/negative) 모두 올바르게 분류 가능한 프롬프트 (주석의 기대값 기준)

### X (0점) 사례
- JSON validation 실패 (`❌ invalid JSON`)
- sentiment enum 범위 지시 없음
- 테스트 입력 "너무 재미없었어"가 negative로 분류되지 않음
- 미제출

---

## 문제 5: CoT vs Standard Prompt 비교

**배점**: 10점
**대상 변수**: `standard_prompt`, `cot_prompt`

### O (10점) — 모두 충족
- [ ] `standard_prompt`: 가이드 없이 문제만 전달
- [ ] `cot_prompt`: 단계별 사고 유도 문구 포함 (예: "단계별로 생각해보세요", "각 단계를 설명하세요")
- [ ] CoT 실행 결과에 "112"가 포함됨 (`verify_logic` Pass)
- [ ] 추론 유도 전략이 실제 프롬프트 문구로 구현됨

### X (0점) 사례
- standard/cot 프롬프트 중 하나라도 비어 있음
- CoT 결과 `verify_logic`에서 Fail (정답 112 미포함)
- CoT 프롬프트가 Standard와 동일 (가이드 누락)
- 미제출

---

## 문제 6: ROUGE / BLEU 지표 빈칸 채우기

**배점**: 10점
**대상 출력**: ROUGE-L Score, BLEU Score

### O (10점) — 모두 충족
- [ ] ROUGE-L 출력 키를 올바르게 선택 (`rougeL_fmeasure` 또는 동등한 F1 키)
- [ ] BLEU score 정상 출력
- [ ] 빈칸 `_______` 자리에 ROUGE-L F1을 대표하는 키 삽입
- [ ] 코드 실행 시 두 점수 숫자로 출력

### X (0점) 사례
- `rouge_results['_______']` 빈칸 미채움으로 KeyError
- ROUGE-L이 아닌 다른 지표 키 사용 (예: rouge1_fmeasure)
- 미제출

---

## 문제 7: ROUGE-L vs BERTScore 비교 구현

**배점**: 10점
**대상 함수**: `calculate_metrics(reference, prediction)`

### O (10점) — 모두 충족
- [ ] `rouge_scorer`로 ROUGE-L F1 계산
- [ ] `bert_score.score`로 BERTScore F1 계산 (한국어 대응 모델 사용)
- [ ] 두 점수 float로 반환
- [ ] 검증 통과: `rouge_val < 0.2`
- [ ] 검증 통과: `bert_val > 0.8`
- [ ] 검증 통과: `bert_val > rouge_val`

### X (0점) 사례
- 3개 assert 중 하나라도 실패
- rouge_scorer 또는 bert_score 미사용
- 한국어 문장에 영어 전용 모델 사용으로 점수 왜곡
- 미제출

---

## 문제 8: Contrastive Decoding (PyTorch)

**배점**: 10점
**대상 클래스**: `ContrastiveGenerator.get_next_token`

### O (10점) — 모두 충족
- [ ] Adaptive Masking: expert_logits 상위권 외 값 필터링 (alpha 기준)
- [ ] Contrastive Logits: `expert_logits - tau * small_logits` 계산
- [ ] 마스킹된 위치를 -inf 또는 매우 작은 값으로 처리
- [ ] Softmax 적용 후 `argmax`로 토큰 선택
- [ ] `torch`와 `torch.nn.functional`만 사용 (외부 라이브러리 없음)
- [ ] 테스트 `run_test()`에서 선택 토큰 == 0 → "테스트 합격" 출력

### X (0점) 사례
- 테스트 Fail (선택 인덱스 ≠ 0)
- Adaptive Masking 누락 (tau 감산만)
- 외부 라이브러리 사용 (numpy, scipy 등)
- 미제출

---

## 문제 9: DSPy Guardrail 설계

**배점**: 10점
**대상 코드**: `GuardrailSignature`, `GuardrailAgent`, `llM_generation_config`

### O (10점) — 모두 충족
- [ ] `user_input = dspy.InputField(desc=...)` 설명 포함 정의
- [ ] `is_safe = dspy.OutputField(desc=...)` 설명 포함 정의
- [ ] `GuardrailAgent.analyze_safety = dspy.ChainOfThought(GuardrailSignature)`
- [ ] `forward`에서 `self.analyze_safety(user_input=user_input)` 호출 후 반환
- [ ] config dict에 `top_p: 0.95` (Nucleus Sampling)
- [ ] config dict에 `repetition_penalty` (또는 `frequency_penalty`) > 1.0 (예: 1.2)

### X (0점) 사례
- InputField/OutputField 설명 누락
- ChainOfThought 대신 Predict 사용
- top_p=0.95 미설정
- repetition_penalty 누락 또는 ≤ 1.0
- 미제출

---

## 문제 10: Self-Correction 프롬프트 개선 루프

**배점**: 10점
**대상 함수**: `optimize_prompt_loop(goal)` 내 `critic_prompt`, `improvement_instruction`

### O (10점) — 모두 충족
- [ ] `critic_prompt`: 생성물(current_answer)을 4가지 조건(120-150자, 필수단어, 금지단어, 해시태그 3개)에 대해 각각 평가하도록 작성
- [ ] `improvement_instruction`: 피드백을 반영해 원래 goal을 더 구체적·강력한 지시문으로 개정
- [ ] 최종 출력이 `evaluate_final_output`에서 100점 달성 (4개 조건 모두 통과)
  - 글자 수 120~150
  - 필수 단어(친환경/노이즈캔슬링/할인) 포함
  - 금지 단어(플라스틱/최고/애플) 미포함
  - 해시태그 3개, 맨 끝에 연속

### X (0점) 사례
- 최종 채점 100점 미달 (75점 이하 X, 100점 O)
- critic_prompt 또는 improvement_instruction 빈 문자열/미작성
- 4가지 조건 중 하나라도 미통과
- 미제출

---

## 공통 0점 조건
- 실행 불가 코드 제출 (SyntaxError, ImportError)
- `YOUR_API_KEY` 미교체로 API 호출 실패 (단, 코드 로직이 완성되어 있으면 O 가능 — 실행 환경 차이 감안)
- 요구된 assert/채점 스크립트 실패
- 미제출

## 참조
- 문제지: `문제지/6주차_주관식_문제지.ipynb`
- 정답지(참조용): `정답지/` 하위 파일 (있을 경우)
