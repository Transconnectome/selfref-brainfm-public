# 데이터 받기와 받은 파일 기록

`data/`는 git에서 제외한다(`.gitignore`). 이 문서는 무엇을 어디서 받았는지와 실측 크기를 기록한다. 파일별 sha256은 각 데이터셋 폴더의 `SHA256SUMS`에 있다. PLAN §9의 `data/MANIFEST.tsv`는 이 문서와 폴더별 `SHA256SUMS`로 대신한다.

모든 공개 S3 경로는 `aws s3 ... --no-sign-request`로 받는다. 대역폭 실측값은 8.8 MB/s다(`docs/stage0/V7.md`).

## 출처

| 데이터 | 위치 | 비고 |
|---|---|---|
| Kucyi ds007216 | `s3://openneuro.org/ds007216/` | V1 |
| Spacetop ds005256 (원본) | `s3://openneuro.org/ds005256/` | V2 |
| Spacetop fMRIPrep ds007070 | `s3://openneuro.org/ds007070/` | V10. alignvideo MNI 1.46 TB, fsLR 581 GB. 아직 받지 않았다 |
| Spacetop MRIQC ds006692 | `s3://openneuro.org/ds006692/` | 41.8 GB. 받지 않았다 |
| NATVIEW | `s3://fcp-indi/data/Projects/NATVIEW_EEGFMRI/` | V3 |
| SwiFT v1 체크포인트 | `https://raw.githubusercontent.com/Transconnectome/SwiFT/main/pretrained_models/contrastive_pretrained.ckpt` | V4. pickle을 실행하지 않고 읽는다(`docs/stage0/V4.md`) |

## 받은 파일 (0단계, 2026-09-23)

| 폴더 | 파일 수 | 크기 | 내용 | 체크섬 |
|---|---|---|---|---|
| `data/kucyi/` | 1,560 | 31,824,318 B | 메타, 평정, events, sidecar, EEG `.set` 헤더(3명, 10개), sub-018 `.fdt` 1개 | `SHA256SUMS` |
| `data/spacetop/` | 2,751 | 154,077,961 B | alignvideo events·sidecar·participants, S3 목록, 집계 CSV. BOLD와 mp4는 없다 | `SHA256SUMS` |
| `data/natview/` | 444 | 7,361,827 B | S3 목록, sidecar, participants, scans, parcel 표본 | `SHA256SUMS` |
| `data/models/swift_v1/` | 1 | 52,998,337 B | `contrastive_pretrained.ckpt` | `5922c84b31b4e59de1c26ed4839689234ce401216f5a2a4fbbf6a4d5940cce3e` |
| `data/search/` | 24 | 2,087,051 B | V10·V11 검색 메타데이터 | — |

## T1 추가 수신 (2026-09-23)

| 폴더 | 내용 | 수신 후 폴더 합계 | 확인 |
|---|---|---|---|
| `data/kucyi/derivatives/` | ExperienceSampling run의 `*_Bergen_CWreg.set`·`.fdt` 140쌍(24명, 47세션). sub-023 ses-002는 파일 이름에 `_events_events_`가 들어 있어 따로 받았다 | `data/kucyi/`: 1,830개, 3,575,599,488 B | `.set` 140개, `.fdt` 140개 ✅ |
| `data/natview/preproc_data/` | dme, dmh, tp, monkey1, monkey2, monkey5, checker, inscapes, rest의 Schaefer 100·200·400 parcel 시계열(sm0, sm0gsr), `mc_1-6.txt`, `Model_Motion24_CompCor.txt` | `data/natview/`: 3,278개, 852,603,757 B | 355 run, parcel tsv 2,124개. V3의 run 표(`natview_func_runs.tsv`)에서 기대한 수와 같다 ✅ |

run 번호가 없는 NATVIEW 폴더(예: `task-checker_bold`)는 `run-*` 패턴에 걸리지 않으므로 받을 때 두 패턴을 모두 써야 한다. 체크섬은 수신 뒤 폴더별 `SHA256SUMS`에 다시 썼다.

아직 받지 않은 것: T1b(NATVIEW 볼륨, C의 게이트 뒤), T2(Spacetop ds007070, 받을 공간을 정한 뒤).
