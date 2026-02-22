# Quant-Finance-Lab: 체계적인 퀀트 금융 리서치 및 구현 포트폴리오
**금융공학 및 계산금융 이론 구현 프로젝트**

---

## 1. Project Overview
**Quant-Finance-Lab**은 Python을 활용하여 핵심적인 퀀트 금융 이론을 'From Scratch' 방식으로 직접 구현하고, 실제 데이터를 통해 검증하는 체계적인 리서치 프로젝트입니다. 본 프로젝트는 **수학적 이론**(확률 미적분, 선형대수)과 **실용적 구현**(데이터 파이프라인, 백테스팅) 사이의 간극을 연결하는 능력을 보여주는 것을 목표로 합니다.

*   **목표:** 금융 이론을 실제 데이터와 결합하여 검증함으로써, 금융공학 석사(MFE) 수준의 깊이 있는 포트폴리오를 구축합니다.
*   **주요 중점 분야:**
    1.  **데이터 엔지니어링:** 금융 시계열 데이터 수집 및 정제를 위한 자동화된 ETL 파이프라인 구축.
    2.  **계량경제학:** 수익률, 변동성 등 통계적 특성 분석 및 정규성 검정.
    3.  **자산 가격결정:** CAPM, Fama-French 팩터 모델 등 주요 가격결정 모델 구현.
    4.  **파생상품:** 블랙숄즈 모형 및 몬테카를로 시뮬레이션을 통한 옵션 가격 결정.

## 2. Repository Structure
본 프로젝트는 금융공학 석사 과정의 커리큘럼을 참고하여, 이론 학습부터 실제 구현까지의 과정을 순차적으로 경험할 수 있도록 모듈화되었습니다.

```plaintext
Quant-Finance-Lab/
│
├── 00_notebooks/           # EDA 및 프로토타이핑을 위한 Jupyter Notebook
├── 01_Data_Pipeline/       # ETL: 데이터 수집, 전처리, SQL 데이터베이스
│   ├── data_collector.py   # yfinance API 크롤러
│   ├── market_data.db      # OHLCV 저장을 위한 SQLite 데이터베이스
│   └── database_manager.py # SQL 상호작용 핸들러
│
├── 02_Financial_Analysis/  # 통계: 수익률, 변동성, 정규성 검정
├── 03_Asset_Pricing/       # 팩터: CAPM, Fama-French, 알파 붕괴 분석
├── 04_Portfolio_Mgmt/      # 최적화: 마코위츠(MVO), 블랙-리터만
├── 05_Derivatives/         # 가격결정: 블랙-숄즈, 그릭스, 몬테카를로(GBM)
├── 06_Paper_Replication/   # 리서치: 학술 논문 구현
├── .gitattributes          # Git configuration
├── .gitignore              # Git exclusion list
└── README.md               # Project Documentation
```

## 3. Tech Stack & Tools

* **Language:** Python 3.9+
* **Data Handling:** pandas, numpy, sqlite3, yfinance
* **Statistical Analysis:** scipy.stats, statsmodels
* **Visualization:** matplotlib, seaborn
* **Documentation:** LaTeX

## 4. Curriculum & Progress

### Phase 1: 금융 데이터 인프라 구축 [완료]
*데이터 무결성을 보장하는 견고한 금융 데이터 파이프라인 구축.*
- [x] **데이터 수집 자동화:** `yfinance` API를 활용하여 OHLCV 데이터 크롤링 및 적재 자동화 (`data_collector.py`).
- [x] **데이터베이스 구축:** 수집된 시계열 데이터를 SQLite DB에 저장하여 체계적으로 관리 (`market_data.db`).
- [x] **데이터 정제:** 결측치 처리 및 수정종가(Adjusted Close) 기준 데이터 클렌징 수행.

### Phase 2: 계량경제학 및 팩터 모델링 [진행 중]
*자산 수익률의 통계적 특성 분석 및 초과 수익(Alpha) 분해.*
- [ ] **시계열 분석:** Q-Q 플롯을 통한 정규성 검정, 자기상관(Autocorrelation), 변동성 군집(Volatility Clustering) 현상 분석.
- [ ] **팩터 모델링:** `statsmodels`를 이용한 Fama-French 3-Factor 모델 구현 및 회귀분석.
- [ ] **백테스팅:** PER, PBR 등 기본적(Fundamental) 팩터를 기반으로 한 투자 전략 수립 및 성과 검증.

### Phase 3: Portfolio Optimization
*자산 배분 및 리스크 관리를 위한 계량적 접근.*
- [ ] **효율적 투자선 (Efficient Frontier):** 위험-수익률 상충 관계(Trade-off) 시각화.
- [ ] **최적화 기법:** `scipy.optimize`를 활용하여 최소분산포트폴리오(MVP) 등 최적 포트폴리오 탐색.
- [ ] **블랙-리터만 모델:** 시장 균형에 투자자의 주관적 견해를 결합하는 모델 구현.

### Phase 4: 파생상품 및 계산금융
*수치적 기법을 활용한 복합 금융상품 가격결정.*
- [ ] **블랙-숄즈 방정식:** 유럽형 옵션의 해석적 해(Analytical Solution) 도출 및 민감도(Greeks) 지표 시각화.
- [ ] **몬테카를로 시뮬레이션:** 기하 브라운 운동(GBM)을 가정한 경로 의존형 옵션(Path-Dependent Options) 가격 결정.
- [ ] **이항 트리 모델:** 미국형 옵션(American Options) 가격 결정 모델 구현.

### Phase 5: 논문 재현
*주요 금융 연구 논문 구현 및 분석.*
- [ ] **논문 선정 및 구현:** "Momentum Crash", "Machine Learning in Asset Pricing" 등 최신 금융공학 논문 재현.

---
**Contact:** [trotz4210@gmail.com]