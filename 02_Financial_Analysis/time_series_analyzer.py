import pandas as pd
import matplotlib.pyplot as plt
import logging
import os
from scipy import stats
import statsmodels.api as sm

# Import from other modules
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ENG_PATH = str(PROJECT_ROOT / "01_Data_Engineering")
ANALYSIS_PATH = str(PROJECT_ROOT / "02_Financial_Analysis")

if DATA_ENG_PATH not in sys.path:
    sys.path.insert(0, DATA_ENG_PATH)
if ANALYSIS_PATH not in sys.path:
    sys.path.insert(0, ANALYSIS_PATH)

from database_manager import DatabaseManager
from analyzer_engine import TimeSeriesAnalyzer

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 데이터베이스 경로 설정 (01_Data_Engineering 폴더 내 market_data.db)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "01_Data_Engineering", "market_data.db")

def load_data_from_db(ticker: str) -> pd.DataFrame:
    """
    SQLite 데이터베이스에서 특정 티커의 일별 데이터를 로드합니다.
    """
    table_name = f"{ticker}_daily"
    df = pd.DataFrame()
    try:
        with DatabaseManager(DB_PATH) as db:
            # SQL 쿼리를 직접 실행하여 DataFrame으로 로드
            df = pd.read_sql_query(f"SELECT Date, Close FROM {table_name}", db.conn)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            logging.info(f"Successfully loaded {len(df)} rows for {ticker} from database.")
    except Exception as e:
        logging.error(f"Error loading data for {ticker} from database: {e}")
    return df

def analyze_returns_multi(tickers: list, data_dict: dict):
    """
    여러 종목의 수익률을 함께 분석하고 시각화합니다.
    (분석 로직은 analyzer_engine.py를 사용)
    """
    # 데이터 검증
    valid_tickers = [t for t in tickers if not data_dict[t].empty]
    if not valid_tickers:
        logging.warning("No valid data to analyze.")
        return

    logging.info(f"Analyzing returns for {valid_tickers} (Total {len(valid_tickers)} tickers).")

    # 1. 수익률 계산
    returns_dict = {}
    for ticker in valid_tickers:
        if 'Close' not in data_dict[ticker].columns:
            logging.error(f"'Close' column not found in data for {ticker}.")
            continue
        returns = data_dict[ticker]['Close'].pct_change().dropna()
        if not returns.empty:
            returns_dict[ticker] = returns

    if not returns_dict:
        logging.warning("No valid returns data.")
        return

    # 2. 하나의 figure에 모든 그래프를 배치 (각 티커마다 3개 subplot: histogram, Q-Q, ACF)
    num_tickers = len(returns_dict)
    fig, axes = plt.subplots(num_tickers, 3, figsize=(16, 4.5 * num_tickers))
    
    # 티커가 1개일 때 axes 형태 조정
    if num_tickers == 1:
        axes = axes.reshape(1, -1)
    
    for idx, (ticker, returns) in enumerate(returns_dict.items()):
        # 0열: 수익률 분포 (히스토그램)
        ax = axes[idx, 0]
        ax.hist(returns, bins=40, edgecolor='black', alpha=0.7)
        ax.set_title(f'{ticker} Daily Returns', fontsize=10)
        ax.set_xlabel('Daily Return', fontsize=9)
        ax.set_ylabel('Frequency', fontsize=9)
        ax.tick_params(labelsize=8)
        ax.grid(alpha=0.3)

        # 1열: Q-Q 플롯 (정규성 검정)
        ax = axes[idx, 1]
        stats.probplot(returns, dist="norm", plot=ax)
        ax.set_title(f'{ticker} Q-Q Plot', fontsize=10)
        ax.tick_params(labelsize=8)
        ax.grid(alpha=0.3)

        # 2열: ACF 플롯 (자기상관)
        ax = axes[idx, 2]
        sm.graphics.tsa.plot_acf(returns, lags=30, ax=ax)
        ax.set_title(f'{ticker} ACF', fontsize=10)
        ax.tick_params(labelsize=8)
        ax.grid(alpha=0.3)

    # 간격 조정: hspace와 wspace를 명시적으로 설정
    plt.subplots_adjust(hspace=0.4, wspace=0.35, left=0.08, right=0.95, top=0.95, bottom=0.08)
    plt.show()

if __name__ == "__main__":
    # 분석할 종목 리스트
    target_tickers = ["AAPL", "MSFT", "TSLA", "SPY"]
    
    logging.info(f"--- Starting Time Series Analysis for {target_tickers} ---")

    # 1. 데이터 로드
    data_dict = {}
    for ticker in target_tickers:
        stock_data = load_data_from_db(ticker)
        data_dict[ticker] = stock_data

    # 2. 수익률 분석 및 시각화 (함께 표시)
    analyze_returns_multi(target_tickers, data_dict)

    logging.info(f"--- Time Series Analysis for {target_tickers} Completed ---")