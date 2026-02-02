# 한미일보 기사 크롤러

한미일보(hanmiilbo.kr) 웹사이트에서 기사를 자동으로 수집하고 이메일로 전송하는 크롤러 프로그램입니다.

## 주요 기능

- 특정 날짜(오늘/어제)의 기사 자동 수집
- GUI 인터페이스로 간편한 사용
- 기사 제목, 본문, 저자, 날짜 정보 추출
- **이메일로 기사 전송** (HTML 형식)
- JSON 및 Excel 파일로 결과 저장 (선택 사항)
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

### 3. Gmail 앱 비밀번호 설정 (Gmail 사용 시)

Gmail을 사용하여 이메일을 전송하려면 앱 비밀번호가 필요합니다:

1. Google 계정 설정 → 보안
2. 2단계 인증 활성화
3. 앱 비밀번호 생성
4. 생성된 16자리 비밀번호를 GUI에 입력

## 사용 방법

### GUI 버전 (권장)

```bash
python crawler_ui.py
```

GUI에서 다음을 설정할 수 있습니다:

- **날짜 선택** (오늘/어제)
- **최대 기사 수** (1~50개)
- **이메일 전송 설정**
  - SMTP 서버 (기본: smtp.gmail.com)
  - SMTP 포트 (기본: 587)
  - 발신 이메일
  - 앱 비밀번호
  - 수신 이메일
- 실시간 크롤링 진행 상황 확인

### CLI 버전

```python
python hanmi_crawler.py
```

코드에서 설정 변경:

```python
# 파일로 저장
crawler = HanmiCrawler()
await crawler.run(max_articles=10, use_list_page=True)

# 이메일로 전송
email_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'your-app-password',
    'recipient_email': 'recipient@example.com'
}
crawler = HanmiCrawler()
await crawler.run(max_articles=10, use_list_page=True, email_config=email_config)
```

## 이메일 전송 기능

### 지원하는 이메일 서비스

- **Gmail**: smtp.gmail.com:587 (앱 비밀번호 필요)
- **Naver**: smtp.naver.com:587
- **Outlook/Hotmail**: smtp-mail.outlook.com:587

### 이메일 형식

HTML 형식으로 깔끔하게 정리된 기사 목록이 전송됩니다:

- 기사 제목, 저자, 날짜
- 본문 요약 (500자)
- 원문 링크
- 반응형 디자인

## 출력 파일 (이메일 미사용 시)

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
- **SMTP**: 이메일 전송

## 프로젝트 구조

```
.
├── crawler_ui.py          # GUI 인터페이스
├── hanmi_crawler.py       # 크롤러 핵심 로직
├── email_sender.py        # 이메일 전송 모듈
├── requirements.txt       # 의존성 패키지
└── README.md             # 프로젝트 문서
```

## 주요 특징

### 이메일 전송

- HTML 형식의 깔끔한 기사 레이아웃
- 주요 이메일 서비스 지원 (Gmail, Naver, Outlook)
- 보안 연결 (TLS/STARTTLS)

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
- 이메일 계정 정보는 안전하게 관리하세요

## 문제 해결

### Gmail 로그인 오류

- 2단계 인증이 활성화되어 있는지 확인
- 앱 비밀번호를 생성했는지 확인
- 일반 비밀번호가 아닌 앱 비밀번호를 사용해야 함

### SMTP 연결 오류

- 방화벽에서 587 포트가 열려있는지 확인
- SMTP 서버 주소가 올바른지 확인

## 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 제작되었습니다.
