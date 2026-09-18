# 보너스 문제 안내

보너스는 기본 제출물과 섞이지 않도록 이 폴더에 모았습니다.

1. 실제 PR 적용: [PR_EVIDENCE_TEMPLATE.md](PR_EVIDENCE_TEMPLATE.md)를 복사해 실제 링크와 5~10줄 수정 요약을 채웁니다.
2. 컨벤션 사용자화: 저장소 루트에서 `bash bonus/01_compare_convention.sh`를 실행합니다. 설정 예시는 [convention_example.json](convention_example.json)입니다.
3. 고급 safe mode: 민감한 샘플 변경을 만든 뒤 `bash bonus/02_compare_safe_mode.sh`를 실행하여 ON/OFF를 비교합니다. 실제 비밀값은 사용하지 마세요.

두 비교 스크립트는 API 호출을 하지 않는 `--dry-run` 방식입니다. 실제 API 호출 전에는 반드시 safe mode를 켜고 출력 프롬프트를 확인하세요.
