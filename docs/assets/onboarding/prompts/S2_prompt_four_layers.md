<!-- source: file:docs/ONBOARDING.md | type: academic | complexity: MED -->

# S2 Prompt — 개인 고유 신호의 네 층위와 Δ_id

## Rendering Rule
- Text with pt size + color name → RENDER in image
- Layout instructions → follow as structure, never render as text
- Never render hex codes, CSS, font names, or section headers as visible text

## Theme
Background: pure white. Five colors only: Deep Navy (titles), Signal Orange (target layer iii), Cerulean Blue (controls), Charcoal (body), Ice Blue (box fills). Flat line icons. Rounded cards. Korean primary.

## Prompt for nanobanana2

Create a 16:9 Korean scientific infographic, pure white background.

TOP TITLE: "뇌 신호 속 '그 사람다움'의 네 층위" 32pt Bold Deep Navy. Subtitle: "같은 영화를 두 번 본 22명" 18pt Charcoal.

LEFT HALF (55%): four horizontal rounded cards stacked vertically.
Card 1, Cerulean Blue outline: "(i) 정적 정체성" 20pt Bold, "해부 구조 · FC 지문 — 어느 장면에서나" 15pt Charcoal. Small tag right: "통제" 14pt Cerulean Blue.
Card 2, Cerulean Blue outline: "(ii) 정적 반응 특성" 20pt Bold, "HRF 지연 · 이득 — 같은 순간끼리만" 15pt Charcoal. Tag: "통제" 14pt Cerulean Blue.
Card 3, thick Signal Orange outline, Ice Blue fill: "(iii) 순간 특이성" 20pt Bold Signal Orange, "그 장면, 그 사람만의 반응" 15pt Charcoal. Tag: "관심 대상" 14pt Bold Signal Orange.
Card 4, thin Charcoal outline: "(iv) 자기회귀" 20pt Bold, "자기 과거로 설명되는 부분" 15pt Charcoal. Tag: "과제 F" 14pt Charcoal.

RIGHT HALF (45%): heading "Δ_id로 (iii)만 남기기" 22pt Bold Deep Navy.
Three rows as a vertical subtraction, each row a rounded box with a large number:
Row 1: "I_lock (같은 시점)" 16pt, render "lock" as a subscript, "0.20" 28pt Bold Deep Navy, caption "(i)+(ii)+(iii)" 14pt.
Row 2: "− I_shift (멀리 떨어진 시점)" 16pt, render "shift" as a subscript and spell 멀리 exactly, "0.10" 28pt Bold Cerulean Blue, caption "(i)" 14pt.
Row 3: "− HRF 대리 자료" 16pt, "0.06" 28pt Bold Cerulean Blue, caption "(ii)" 14pt.
Horizontal rule, then result box Ice Blue fill: "= 0.04" 32pt Bold Signal Orange, "(iii) 추정치" 16pt Bold.
Small note under result: "예시 값 · 정적 지문이 그대로 남는 지표(예: FC) 가정. B 지표에서는 I_shift ≈ 0" 12pt Charcoal.

## Negative
dark background, glossy surfaces, gradients, poster style, tiny text, mixed icon styles, stock photos, brain photos, extra numbers, emoji, diagonal arrows, curved arrows, circular diagrams, color codes or markup in image

## Fallback
If halves fail: layers on top as four cards in a row, subtraction below as one horizontal equation.
