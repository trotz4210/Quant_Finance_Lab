import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os
from scipy import stats
import statsmodels.api as sm

# Import DatabaseManager from 01_Data_Engineering
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ENG_PATH = PROJECT_ROOT / "01_Data_Engineering"
if str(DATA_ENG_PATH) not in sys.path:
    sys.path.insert(0, str(DATA_ENG_PATH))
from database_manager import DatabaseManager

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

def analyze_returns(ticker: str, data: pd.DataFrame):
    """
    주식 수익률을 계산하고, 정규성 및 자기상관을 분석합니다.
    """
    if data.empty:
        logging.warning(f"No data to analyze for {ticker}.")
        return

    # 일일 수익률 계산 (로그 수익률 사용)
    # Close 컬럼이 없으면 에러 발생 가능성 있으므로 확인
    if 'Close' not in data.columns:
        logging.error(f"'Close' column not found in data for {ticker}.")
        return

    returns = data['Close'].pct_change().dropna()
    # returns = np.log(data['Close'] / data['Close'].shift(1)).dropna() # 로그 수익률

    if returns.empty:
        logging.warning(f"No returns to analyze for {ticker}.")
        return

    logging.info(f"Analyzing returns for {ticker} (Total {len(returns)} data points).")

    # 1. 수익률 분포 시각화 (히스토그램)
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1)
    sns.histplot(returns, kde=True, bins=50)
    plt.title(f'{ticker} Daily Returns Distribution')
    plt.xlabel('Daily Return')
    plt.ylabel('Frequency')

    # 2. Q-Q 플롯을 통한 정규성 검정
    plt.subplot(1, 3, 2)
    stats.probplot(returns, dist="norm", plot=plt)
    plt.title(f'{ticker} Q-Q Plot (Normality Test)')

    # 3. 자기상관 함수 (ACF) 플롯
    plt.subplot(1, 3, 3)
    sm.graphics.tsa.plot_acf(returns, lags=30, ax=plt.gca())
    plt.title(f'{ticker} Autocorrelation Function (ACF)')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    target_ticker = "AAPL" # 분석할 종목 선택
    logging.info(f"--- Starting Time Series Analysis for {target_ticker} ---")

    # 1. 데이터 로드
    stock_data = load_data_from_db(target_ticker)

    # 2. 수익률 분석 및 시각화
    if not stock_data.empty:
        analyze_returns(target_ticker, stock_data)
    else:
        logging.error(f"Failed to load data for {target_ticker}. Cannot proceed with analysis.")

    logging.info(f"--- Time Series Analysis for {target_ticker} Completed ---")