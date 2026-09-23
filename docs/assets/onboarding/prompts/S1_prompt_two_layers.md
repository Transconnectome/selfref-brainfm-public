<!-- source: file:docs/ONBOARDING.md | type: academic | complexity: MED -->

# S1 Prompt — 두 층 구조와 과제 지도

## Rendering Rule
- Text with pt size + color name → RENDER in image
- Layout instructions → follow as structure, never render as text
- Never render hex codes, CSS, font names, or section headers as visible text

## Theme
Background: pure white. Five colors only: Deep Navy (titles), Signal Orange (layer 1), Cerulean Blue (layer 2), Charcoal (body), Ice Blue (box fills). Flat line icons. Rounded cards. Generous whitespace. Korean primary, English terms kept as is.

## Prompt for nanobanana2

Create a 16:9 Korean scientific infographic, pure white background.

TOP TITLE: "selfref-brainfm: 두 층 구조" 32pt Bold Deep Navy. Subtitle below: "자기참조를 재기 전에, 측정 도구부터 검증한다" 18pt Charcoal.

TWO HORIZONTAL BANDS stacked vertically:

UPPER BAND, Signal Orange outline, label on left "1층 · 자기 라벨로 가설 검정" 20pt Bold Signal Orange.
Three rounded cards in a row:
Card: "A" 28pt Bold, "개인 관련성의 사람×클립 성분" 16pt, "Spacetop 평정" 14pt Charcoal.
Card: "D" 28pt Bold, "탐침 직전 EEG → self 평정" 16pt, "Kucyi EEG" 14pt Charcoal.
Card: "E" 28pt Bold, "관련성 ↔ 뇌 반응 특이성 (교량)" 16pt, "Spacetop fMRI" 14pt Charcoal.

LOWER BAND, Cerulean Blue outline, label on left "2층 · 측정 도구 검증" 20pt Bold Cerulean Blue.
Three rounded cards in a row:
Card: "B" 28pt Bold, "순간 특이성 Δ_id" 16pt, "NATVIEW parcel" 14pt Charcoal.
Card: "C" 28pt Bold, "SwiFT 표상의 보존율" 16pt, "NATVIEW 볼륨 · GPU" 14pt Charcoal.
Card: "F" 28pt Bold, "자기회귀 대 자극 예측 지수" 16pt, "NATVIEW parcel" 14pt Charcoal.

One straight arrow that starts at the top edge of card B, goes straight up, then straight right, then straight up into the bottom edge of card E, passing above card C without touching it. Label on the arrow next to card B: "B의 판정 → E 결과의 해석" 14pt Cerulean Blue.

BOTTOM BAR full width, Ice Blue fill:
Left: "0단계 검증 · 합성 테스트 완료 (2026-09-23)" 18pt Bold Deep Navy. Right: "합성 데이터 테스트 70개 · 실데이터 분석 전" 16pt Charcoal.

## Negative
dark background, glossy surfaces, gradients, poster style, tiny text, mixed icon styles, stock photos, extra numbers, emoji, diagonal arrows, curved arrows, circular diagrams, color codes or markup in image

## Fallback
If bands fail: two columns, 1층 left and 2층 right, cards stacked vertically.
