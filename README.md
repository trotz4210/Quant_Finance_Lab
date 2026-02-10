# Quant-Finance-Lab: Quantitative Finance Research Portfolio

**Financial Engineering & Computational Finance Implementation Project**

## 1. Project Overview (연구 개요)
**Quant-Finance-Lab** is a comprehensive research project aiming to implement core quantitative finance theories from scratch using Python.
This repository demonstrates the ability to bridge the gap between **Mathematical Theory** (Stochastic Calculus, Linear Algebra) and **Practical Implementation** (Data Pipeline, Backtesting).

* **Objective:** To build an MFE-level portfolio by verifying financial theories with real-world data.
* **Key Focus:**
    1.  **Data Engineering:** Automated ETL pipeline for financial time-series.
    2.  **Econometrics:** Statistical analysis of returns, volatility, and normality.
    3.  **Asset Pricing:** Implementation of CAPM, Fama-French Factor models.
    4.  **Derivatives:** Option pricing via Black-Scholes and Monte Carlo Simulations.

## 2. Repository Structure (폴더 구조)
The project is organized into sequential modules, mimicking the curriculum of a master's program in financial engineering.

```
Quant-Finance-Lab/
│
├── 01_Data_Pipeline/       # ETL: Data Collection, Preprocessing, SQL Database
├── 02_Financial_Analysis/  # Statistics: Returns, Volatility, Normality Tests
├── 03_Asset_Pricing/       # Factors: CAPM, Fama-French, Alpha Decay Analysis
├── 04_Portfolio_Mgmt/      # Optimization: Markowitz (MVO), Black-Litterman
├── 05_Derivatives/         # Pricing: Black-Scholes, Greeks, Monte Carlo (GBM)
├── 06_Paper_Replication/   # Research: Implementing Academic Papers
└── README.md               # Project Documentation
```

## 3. Tech Stack & Tools
* **Language:** Python 3.9+
* **Data Handling:** `pandas`, `numpy`, `sqlite3`, `yfinance`
* **Statistical Analysis:** `scipy.stats`, `statsmodels`
* **Visualization:** `matplotlib`, `seaborn`
* **Documentation:** LaTeX (for mathematical formulations)

## 4. Curriculum & Progress (학습 로드맵)

### Phase 1: Financial Data Infrastructure [Completed]
Building a robust data pipeline to ensure data integrity.
- [x] **Automated Crawler:** Fetching OHLCV data using `yfinance` API.
- [x] **Database Integration:** Storing time-series data into SQLite (`market_data.db`).
- [x] **Data Cleansing:** Handling missing values and adjusted close prices.

### Phase 2: Econometrics & Factor Modeling [In Progress]
Analyzing statistical properties of asset returns and decomposing alpha.
- [ ] **Time-Series Analysis:** Normality tests (Q-Q plot), Autocorrelation, Volatility Clustering.
- [ ] **Factor Modeling:** Implementing Fama-French 3-Factor Model using `statsmodels`.
- [ ] **Backtesting:** Strategy verification based on fundamental factors (PER, PBR).

### Phase 3: Portfolio Optimization
Mathematical approach to asset allocation and risk management.
- [ ] **Efficient Frontier:** Visualizing the risk-return trade-off.
- [ ] **Optimization Solvers:** Finding MVP (Minimum Variance Portfolio) using `scipy.optimize`.
- [ ] **Black-Litterman Model:** Incorporating investor views into market equilibrium.

### Phase 4: Derivatives & Computational Finance
Pricing complex financial instruments via numerical methods.
- [ ] **Black-Scholes Equation:** Analytical solution for European options & Greeks visualization.
- [ ] **Monte Carlo Simulation:** Pricing path-dependent options assuming GBM.
- [ ] **Binomial Trees:** Pricing American options.

### Phase 5: Paper Replication
Deep dive into academic research.
- [ ] Replicating "Momentum Crash" or "Machine Learning in Asset Pricing" papers.

---
**Contact:** [trotz4210@gmail.com]