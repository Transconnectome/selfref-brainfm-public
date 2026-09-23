<!-- source: file:docs/ONBOARDING.md | type: academic | complexity: MED -->

# S3 Prompt — 판정 규칙: 결과를 네 가지로 말하기

## Rendering Rule
- Text with pt size + color name → RENDER in image
- Layout instructions → follow as structure, never render as text
- Never render hex codes, CSS, font names, or section headers as visible text

## Theme
Background: pure white. Five colors only: Deep Navy (titles), Signal Orange (support), Cerulean Blue (reject), Charcoal (body, undetermined), Ice Blue (band fill). Flat design. Korean primary.

## Prompt for nanobanana2

Create a 16:9 Korean statistics infographic, pure white background.

TOP TITLE: "판정 규칙: p값 대신 네 가지 결론" 32pt Bold Deep Navy. Subtitle: "기준은 SESOI (관심 있는 최소 효과) = 0.2" 18pt Charcoal.

MAIN AREA: a horizontal number line from −0.3 to 0.5 with tick labels "−0.2", "0", "0.2", "0.4" 14pt Charcoal. A light Ice Blue shaded vertical band between −0.2 and 0.2 labeled "동등성 구간 ±SESOI" 14pt. A thin vertical line at 0.

Four horizontal confidence-interval bars stacked above the number line, each a straight line with a dot at the center, with a label at the right end:
Bar 1 from 0.25 to 0.45, dot 0.35, Signal Orange: "지지(강) · 95% CI 하한 ≥ SESOI" 16pt Bold Signal Orange.
Bar 2 from 0.05 to 0.45, dot 0.25, Signal Orange lighter: "지지(약) · 0 배제, 점추정 ≥ SESOI" 16pt Signal Orange.
Bar 3 from 0.02 to 0.08, dot 0.05, Cerulean Blue: "기각 · 90% CI가 구간 안 (TOST)" 16pt Bold Cerulean Blue.
Bar 4 from −0.05 to 0.25, dot 0.10, Charcoal: "판단 불가" 16pt Bold Charcoal.

BOTTOM BAR full width, Ice Blue fill, two boxes side by side:
Left: "기각 ≠ 효과 0" 22pt Bold Deep Navy, "SESOI보다 작다는 뜻" 16pt Charcoal.
Right: "CI가 0을 포함 ≠ 효과 없음" 22pt Bold Deep Navy, "기각은 90% CI가 ±SESOI 안일 때만" 16pt Charcoal.

## Negative
dark background, glossy surfaces, gradients, poster style, tiny text, stock photos, extra numbers, emoji, diagonal lines, curved arrows, circular diagrams, p-value formulas, color codes or markup in image

## Fallback
If number line fails: four rounded cards in a row, each with its interval written as text.
