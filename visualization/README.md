# 시계열 분석 대시보드

Python과 HTML/CSS/JavaScript를 활용한 인터랙티브 시계열 분석 시각화 대시보드입니다.

## 📁 폴더 구조

```
visualization/
├── index.html          # 메인 HTML 파일
├── style.css           # 스타일시트
├── script.js           # JavaScript (Plotly 차트)
├── generate_data.py    # 데이터 생성 스크립트
├── data.json           # 생성된 데이터 (자동 생성)
└── README.md           # 이 파일
```

## 🚀 사용 방법

### 1. 데이터 생성

먼저 Python 스크립트를 실행하여 JSON 데이터를 생성합니다:

```bash
cd e:\Quant_Program_env\Quant_Finance_Lab\visualization
python generate_data.py
```

이 명령을 실행하면 `data.json` 파일이 생성됩니다.

### 2. 대시보드 실행

#### 방법 1: 간단한 HTTP 서버 실행 (Python)

```bash
# Python 3.7+
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

그 후 브라우저에서 `http://localhost:8000` 접속

#### 방법 2: VS Code Live Server 확장

1. VS Code에서 `visualization/index.html` 파일 열기
2. 마우스 우클릭 → "Open with Live Server"

#### 방법 3: 브라우저에서 직접 열기

`index.html` 파일을 브라우저에 드래그하면 작동합니다.

## 📊 대시보드 기능

### 1. **티커 선택**
   - AAPL, MSFT, TSLA, SPY 중 선택 가능
   - 클릭하면 해당 종목의 분석 자료로 즉시 업데이트

### 2. **통계 정보**
   - 평균 수익률
   - 표준편차 (변동성)
   - 최소/최대 수익률
   - 왜도 (Skewness)
   - 첨도 (Kurtosis)

### 3. **차트**

#### 가격 추이 (Price History)
- 2020년부터 2023년까지의 종목별 가격 변동
- 장기 추세 파악에 유용

#### 수익률 분포 (Histogram)
- 일일 수익률의 분포도
- 정규분포 여부 판단 가능

#### Q-Q 플롯 (Q-Q Plot)
- 표본 분위수 vs 이론적 분위수
- 정규분포 적합성 검정
- 대각선에 가까울수록 정규분포에 가까움

#### 자기상관 (ACF)
- 시계열의 자기상관성 측정
- 점선은 95% 신뢰도 구간
- 구간 내에 있으면 유의하지 않음

## 🛠️ 기술 스택

- **Backend**: Python, Pandas, SciPy, StatsModels, SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Visualization**: Plotly.js (인터랙티브 차트)

## 📈 분석 방법론

### 1. 수익률 계산
```
Daily Return = (Close[t] - Close[t-1]) / Close[t-1]
```

### 2. 정규성 검정 (Q-Q Plot)
- 금융 자료의 정규성 여부 확인
- 꼬리가 클수록 극단값 위험이 높음

### 3. 자기상관 (ACF)
- 과거 수익률이 현재 수익률에 미치는 영향
- 금융 시계열의 독립성 검정

## 💾 데이터 소스

- **출처**: Yahoo Finance (yfinance)
- **기간**: 2020-01-01 ~ 2023-12-31
- **종목**: AAPL, MSFT, TSLA, SPY

## 🔄 데이터 업데이트

최근 데이터로 분석을 업데이트하려면:

```bash
# data_collector.py 실행 (최신 데이터 수집)
cd ..\01_Data_Engineering
python data_collector.py

# 시각화 데이터 재생성
cd ..\visualization
python generate_data.py
```

## 📱 반응형 디자인

- 데스크톱: 최적화된 4개 차트 레이아웃
- 태블릿: 2x2 그리드
- 모바일: 1열 레이아웃

## 🎨 색상 테마

- AAPL: 회색 (#555555)
- MSFT: 파란색 (#00a4ef)
- TSLA: 빨간색 (#e82127)
- SPY: 초록색 (#006400)

## ⚠️ 주의사항

1. `data.json` 파일이 없으면 대시보드가 작동하지 않습니다.
2. Python 스크립트 실행 시 인터넷 연결 필요 (데이터 다운로드)
3. 브라우저의 개발자 도구(F12)에서 에러 메시지 확인 가능

## 🚀 포트폴리오 활용

이 대시보드는 다음과 같이 포트폴리오에 활용할 수 있습니다:

1. **GitHub에 업로드**: HTML/CSS/JS만 필요 (데이터 포함)
2. **GitHub Pages 배포**: 무료 웹 호스팅
3. **라이브 데모**: 모든 상호작용 기능 포함

## 📝 파일 설명

### generate_data.py
- 데이터베이스에서 데이터 로드
- 통계 계산 및 차트 데이터 생성
- JSON 형식으로 내보내기

### index.html
- 대시보드 레이아웃
- Plotly.js 차트 컨테이너
- 통계 정보 패널

### style.css
- 모던한 그래디언트 디자인
- 반응형 그리드 레이아웃
- 호버 애니메이션 효과

### script.js
- JSON 데이터 로드
- Plotly 차트 렌더링
- 티커 선택 인터랙션
- 통계 정보 업데이트

## 📞 문의 및 개선 사항

더 많은 기능을 추가하고 싶다면:
- 추가 기술 지표 (MACD, RSI, Bollinger Bands)
- 시계열 예측 모델
- 포트폴리오 분석
- 리스크 분석

---

**Created**: 2026-02-25  
**Last Updated**: 2026-02-25
