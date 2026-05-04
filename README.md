# sembench-ko-fin

> **의미보존 가명화가 실제로 얼마나 잘 동작하는가?**

한국 금융 서비스 컨텍스트에서 의미보존 가명화(semantic-preserving pseudonymization) 품질을 측정하는 벤치마크 테스트 스위트입니다.

혁신금융서비스 신청을 준비하는 금융회사의 AI/보안/컴플라이언스팀이 "우리 가명화 처리가 외부 LLM 활용 시 원본 대비 얼마나 의미를 보존하는가"를 정량적으로 측정할 수 있습니다.

## 핵심 아이디어

```
원본(Private)  →  가명화 서비스  →  외부 LLM  →  응답 A
원본(Private)  →  (직접 전달)   →  외부 LLM  →  응답 B (기준)

SPS = judge(응답 A, 응답 B) / 20.0
```

LLM-as-a-Judge가 5개 차원에서 의미 보존 정도를 0–4점으로 채점합니다:
- **Intent Preservation** — 같은 질문에 답하고 있는가
- **Fact Accuracy** — 금액·금리·결정 등 핵심 사실이 맞는가
- **Reasoning Completeness** — 추론 과정이 완전한가
- **Actionability** — 같은 행동을 취할 수 있는가
- **Hallucination Absence** — 없는 사실을 만들어내지 않는가

## 5축 테스트 매트릭스

| 축 | 값 |
|---|---|
| Turn | Single / Multi |
| Service | 챗봇 / 청구상담 / 자산관리 / 부채최적화 / 세금 / 이상거래 |
| Domain | 카드 / 보험 / 부채 / 뱅킹 / 증권 / 세금 |
| Difficulty | L1(단순조회) / L2(추론) / L3(어드버서리) / L4(규제엣지) |
| Strategy | token / taxonomy / relation / lifecycle / band / hybrid |

## 플러그인 어댑터 인터페이스

```python
from sembench.adapters.base import PseudonymizationAdapter

class MyAdapter(PseudonymizationAdapter):
    @property
    def adapter_id(self) -> str: return "my-service-v1"

    def redact(self, raw_utterance, raw_context) -> dict: ...
    def rehydrate(self, external_response, raw_context) -> str: ...
```

## 빠른 시작

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# CI smoke (카드 L1, 3 cases)
sembench run --config configs/ci_smoke.yaml

# 전체 검증 실행
sembench run --config configs/full.yaml --out results/run.json

# HTML 리포트
sembench report html --input results/run.json --out results/report.html

# 여러 실행 결과 비교
sembench report leaderboard results/run.json
```

## 현재 포함된 것

- 6개 도메인(card, insurance, debt, banking, securities, tax) 데이터셋
- L1/L2 일반 케이스, L3 교차참조 공격, L4 규제 엣지 케이스
- manifest 기반 `MatrixLoader`
- YAML 기반 `ComplianceChecker`
- `semantic-redaction-ko` reference adapter
- HTML 리포트와 leaderboard
- 가명정보 처리 가이드라인(2026.03.) 기반 문서와 DPIA 템플릿

## 규제 컨텍스트

이 벤치마크는 `가명정보 처리 가이드라인(2026.03.)` 3단계 위험 체계를 준수합니다:
- **L1/L2**: 저위험 — 단일 판사(Claude Haiku/Sonnet)
- **L3/L4**: 고위험 — 앙상블 판사(Claude Opus × 2+)

## 라이선스

Apache-2.0
