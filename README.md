# 한미일보 기사 크롤러

한미일보(hanmiilbo.kr) 웹사이트에서 기사를 자동으로 수집하는 크롤러 프로그램입니다.

## 주요 기능

- 특정 날짜(오늘/어제)의 기사 자동 수집
- GUI 인터페이스로 간편한 사용
- 기사 제목, 본문, 저자, 날짜 정보 추출
- JSON 및 Excel 파일로 결과 저장
- 날짜 필터링으로 정확한 기사 수집

## 설치 방법

### 1. Python 환경 설정

Python 3.8 이상이 필요합니다.

```bash
pip install -r requirements.txt
```

### 2. Playwright 브라우저 설치

```bash
playwright install chromium
```

## 사용 방법

### GUI 버전 (권장)

```bash
python crawler_ui.py
```

GUI에서 다음을 설정할 수 있습니다:

- 날짜 선택 (오늘/어제)
- 최대 기사 수 (1~50개)
- 실시간 크롤링 진행 상황 확인

### CLI 버전

```python
python hanmi_crawler.py
```

코드에서 설정 변경:

```python
# 오늘 날짜 기사 수집
crawler = HanmiCrawler()
await crawler.run(max_articles=10, use_list_page=True)

# 특정 날짜 기사 수집
from datetime import date
crawler = HanmiCrawler(target_date=date(2026, 2, 1))
await crawler.run(max_articles=10)
```

## 출력 파일

크롤링 완료 후 다음 파일이 생성됩니다:

- `hanmi_articles_YYYYMMDD_HHMMSS.json` - JSON 형식 원본 데이터
- `hanmi_articles_YYYYMMDD_HHMMSS.xlsx` - Excel 형식 (가독성 좋음)

### Excel 파일 구조

| 제목 | 저자 | 등록일시 | 본문 | URL | 크롤링일시 |
| ---- | ---- | -------- | ---- | --- | ---------- |

## 기술 스택

- **Playwright**: 동적 웹페이지 렌더링 및 크롤링
- **BeautifulSoup4**: HTML 파싱
- **Pandas**: 데이터 처리 및 Excel 저장
- **Tkinter**: GUI 인터페이스
- **OpenPyXL**: Excel 파일 스타일링

## 프로젝트 구조

```
.
├── crawler_ui.py          # GUI 인터페이스
├── hanmi_crawler.py       # 크롤러 핵심 로직
├── requirements.txt       # 의존성 패키지
└── README.md             # 프로젝트 문서
```

## 주요 특징

### 날짜 필터링

- 타겟 날짜와 정확히 일치하는 기사만 수집
- 메인 페이지 또는 카테고리 목록 페이지에서 수집 가능

### 크로스 플랫폼 지원

- Windows, macOS, Linux 지원
- 플랫폼별 폰트 자동 설정

### PyInstaller 호환

- 실행 파일(.exe)로 패키징 가능
- UTF-8 인코딩 자동 처리

## 주의사항

- 웹사이트 서버에 부하를 주지 않도록 요청 간 1초 대기 시간 적용
- 크롤링은 해당 웹사이트의 이용약관을 준수해야 합니다
- 개인적인 용도로만 사용하세요

## 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 제작되었습니다.
