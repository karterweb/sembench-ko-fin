# SPS Rubric Korean Calibration Prompt

Use this prompt to calibrate Korean financial semantic-preservation judging.

## Dimensions

1. Intent Preservation: 후보 답변이 기준 답변과 같은 질문에 답하는가.
2. Fact Accuracy: 금액, 금리, 승인/취소, 청구 가능성 등 핵심 사실이 맞는가.
3. Reasoning Completeness: 기준 답변의 판단 근거와 조건을 충분히 보존하는가.
4. Actionability: 사용자가 같은 후속 행동을 취할 수 있는가.
5. Hallucination Absence: 기준에 없는 사실을 만들어내지 않는가.

## Annotated Examples

### Example A: 카드 승인/취소 쌍

Reference: `승인 1건과 취소 1건의 쌍이므로 실제 청구는 1건입니다.`

Candidate: `같은 금액의 커피전문점 거래 중 하나는 취소되어 최종 청구는 1건일 가능성이 큽니다.`

Expected: 18-20. 핵심 의도, 사실, 추론, 행동 가능성이 거의 보존됨.

### Example B: 보험 청구 서류 누락

Reference: `실손 청구 가능성이 있지만 세부내역서와 의학적 필요성 확인이 필요합니다.`

Candidate: `청구할 수 있습니다.`

Expected: 10-13. 의도는 맞지만 불확실성과 서류 조건이 사라져 actionability가 낮음.

### Example C: 부채 상환 우선순위

Reference: `고금리 카드론을 우선 검토하고, 마이너스통장 한도 유지 여부를 확인해야 합니다.`

Candidate: `자동차 할부를 먼저 갚으세요.`

Expected: 0-6. 핵심 우선순위가 뒤집혀 fact accuracy와 actionability가 낮음.
