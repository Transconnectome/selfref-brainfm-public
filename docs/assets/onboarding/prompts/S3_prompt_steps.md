<!-- source: file:docs/ONBOARDING.md | type: explainer | complexity: LOW -->
# S3 Prompt — 어떻게 연구하나
## Rendering Rule
- Text with pt size + color name → RENDER in image
- Layout instructions → follow as structure, never render as text
- Never render hex codes, CSS, font names, or section headers as visible text

## Theme
Background: pure white. Five colors only: Deep Navy (titles), Signal Orange (the thing we look for), Cerulean Blue (neutral elements), Charcoal (body text), Ice Blue (box fills). Friendly flat line icons, rounded cards, lots of whitespace. Audience: first-year undergraduates with no neuroscience or statistics background. Korean only, no English jargon, no numbers, no Greek letters, no formulas.

## Prompt for nanobanana2
Create a 16:9 Korean explainer infographic, pure white background.

TOP TITLE: "어떻게 연구하나: 네 단계" 32pt Bold Deep Navy. Subtitle: "새로 실험하지 않는다. 이미 공개된 데이터와 Python으로 한다" 18pt Charcoal.

FOUR NUMBERED ROUNDED CARDS left to right, connected by straight horizontal arrows:
Card 1, Cerulean Blue outline, folder icon: "① 공개 데이터 모으기" 20pt Bold Deep Navy. Three short lines 15pt Charcoal: "영화 보며 찍은 뇌 영상", "'방금 내 생각 했나요?' 질문과 뇌파", "영상마다 '나와 관련 있었나' 점수".
Card 2, Cerulean Blue outline, test tube icon: "② 가짜 데이터로 먼저 연습" 20pt Bold Deep Navy. Two lines 15pt Charcoal: "정답을 심어 둔 가짜 데이터", "분석 코드가 정답을 찾는지 확인".
Card 3, Cerulean Blue outline, sealed envelope icon: "③ 기준을 미리 적어 두기" 20pt Bold Deep Navy. Two lines 15pt Charcoal: "결과를 보기 전에", "무엇이면 성공인지 정한다".
Card 4, thick Signal Orange outline, Ice Blue fill, magnifying glass over brain icon: "④ 진짜 데이터 분석" 20pt Bold Signal Orange. Two lines 15pt Charcoal: "가짜 단서를 걸러내고", "'나'에 관한 신호를 찾는다".

BOTTOM BAR full width, Ice Blue fill:
"지금은 ②까지 끝났다. ③부터 학생과 함께 한다" 22pt Bold Deep Navy.

## Negative
dark background, glossy, gradients, 3D, photorealistic, English words, numbers other than the circled step numbers, formulas, Greek letters, charts, tiny text, diagonal arrows, curved arrows, circular diagrams, color codes or markup in image
