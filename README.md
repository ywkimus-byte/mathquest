# Math Quest v0.6 — Streamlit 배포판

기존 Gradio v06의 학습 로직을 유지하고 화면을 Streamlit으로 변환한 버전입니다.

## 포함 기능
- 덧셈 학습 6단계, 5문제 중 4문제 이상이면 레벨 상승
- 오답노트 및 반복 복습
- 점수, 연속 정답, 배지 4종
- 수학 왕국 모험 지도(6개 지역)
- 레벨별 학습 결과 및 통계 그래프
- JSON 학습 기록 다운로드/복원 (기존 Gradio v06 파일과 호환)

## 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud 배포
1. GitHub에 공개 저장소 `mathquest`를 만들고, 이 폴더의 `app.py`와 `requirements.txt`를 저장소 최상위에 업로드합니다.
2. https://share.streamlit.io/ 에 GitHub로 로그인 후 **Create app / Deploy an app**을 선택합니다.
3. 저장소와 브랜치(`main`), 앱 파일 경로(`app.py`)를 선택합니다.
4. 배포 후 생성된 `*.streamlit.app` 주소에서 확인합니다.

## 주의사항
- 학습 기록은 자동으로 클라우드에 저장되지 않습니다. 학생이 JSON 파일을 다운로드하여 다음에 다시 업로드해야 합니다.
- 사용자 로그인이나 교사용 통합 계정은 아직 구현하지 않았습니다.
- Community Cloud에서 비활성 상태로 오래 두면 앱이 잠들 수 있습니다.
- `app.py`에 학습 로직과 화면 코드가 함께 있으므로 추후 기능 추가도 이 파일에서 가능합니다.
