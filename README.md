# 금융 뉴스 크롤러

네이버 미디어에서 주요 경제 신문의 1면 기사를 자동으로 크롤링하고 API를 통해 데이터를 전송하는 Python 프로젝트입니다.

## 프로젝트 개요

이 프로젝트는 다음 5개 경제 신문의 1면 기사를 매일 자동으로 수집합니다:
- 파이낸셜뉴스
- 머니투데이  
- 한국경제
- 매일경제
- 헤럴드경제

## 주요 기능

- **자동 뉴스 크롤링**: 네이버 미디어에서 각 신문의 1면 기사 제목과 링크 추출
- **API 연동**: 수집된 뉴스 데이터를 외부 API로 전송
- **로깅 시스템**: 상세한 로그 기록 및 관리
- **텔레그램 알림**: 오류 발생시 텔레그램으로 알림 전송
- **이미지 처리**: 게시글에 포함된 이미지 압축 및 최적화

## 프로젝트 구조

```
finance-news-crawler/
├── main.py                 # 메인 실행 파일
├── requirements.txt        # Python 의존성 패키지
├── README.md              # 프로젝트 문서
├── logs/                  # 로그 파일 저장 디렉토리
└── utils/                 # 유틸리티 모듈
    ├── api_util.py        # API 통신 관련 유틸리티
    ├── logger_util.py     # 로깅 시스템
    └── telegram_util.py   # 텔레그램 알림 기능
```

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 환경 변수를 설정하세요:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TELEGRAM_CHAT_TEST_ID=your_test_chat_id
```

### 3. API 서버 설정

`utils/api_util.py`에서 API 서버 URL을 설정하세요:

```python
self.base_url = "http://your-api-server/api"
```

## 사용법

### 기본 실행

```bash
python main.py
```

### 주요 기능

1. **뉴스 크롤링**: 각 경제 신문의 1면 기사 정보 수집
2. **API 전송**: 수집된 데이터를 API 서버로 전송
3. **오류 처리**: 실패시 텔레그램으로 알림 전송
4. **로깅**: 모든 과정을 로그 파일에 기록

## API 엔드포인트

### 뉴스 데이터 전송
- **URL**: `POST /api/news/top`
- **데이터**: 
  ```json
  {
    "news_date": "2024-01-01",
    "company": "파이낸셜뉴스",
    "title": "기사 제목",
    "source_url": "https://..."
  }
  ```

### 게시글 생성
- **URL**: `POST /api/board-content`
- **기능**: 텍스트 및 이미지가 포함된 게시글 생성
- **이미지 압축**: 자동으로 이미지 크기 최적화

## 로깅

- 로그 파일은 `logs/` 디렉토리에 날짜별로 저장됩니다
- 로그 레벨: INFO, ERROR, DEBUG
- 콘솔과 파일에 동시 출력

## 텔레그램 알림

- API 오류 발생시 자동으로 텔레그램으로 알림 전송
- 테스트용 채팅방과 운영용 채팅방 구분 지원

## 의존성 패키지

- `python-dotenv`: 환경 변수 관리
- `requests`: HTTP 요청 처리
- `beautifulsoup4`: HTML 파싱
- `fake-useragent`: User-Agent 랜덤화
- `Pillow`: 이미지 처리

## 주의사항

- 네이버 미디어의 구조 변경시 크롤링 로직 수정 필요
- API 서버가 정상 동작해야 데이터 전송 가능
- 텔레그램 봇 토큰과 채팅방 ID 설정 필수