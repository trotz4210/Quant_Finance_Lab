import yfinance as yf
import pandas as pd
import os
import time
import logging
from database_manager import DatabaseManager # 수정: DatabaseManager 임포트

# 1. Settings (설정)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "market_data.db")

# List of tickers to download (다운로드할 종목 리스트)
# 'SPY' is an ETF that tracks S&P 500 (SPY는 S&P 500을 추종하는 ETF)
TICKERS = ["AAPL", "MSFT", "TSLA", "SPY"] 

START_DATE = "2020-01-01"   
END_DATE = "2023-12-31"     

def fetch_stock_data(ticker, start, end):
    """
    티커의 주가 데이터를 다운로드/기본적인 데이터 정제 수행
    """
    logging.info(f"Fetching data for {ticker} from {start} to {end}...")
    
    # Download data (데이터 다운로드)
    # progress=False: Hide the default progress bar of yfinance (yfinance 기본 진행바 숨기기)
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)

    if df.empty:
        logging.warning(f"No data downloaded for {ticker}. It might be delisted or the ticker is incorrect.")
        return None
    
    # MultiIndex 컬럼명을 단순 컬럼명으로 변환 (첫 번째 레벨 사용: Open, High, Low, Close, Volume)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # 데이터 정제: 결측치 확인
    if df.isnull().values.any():
        logging.warning(f"NaN values found in {ticker} data. Applying forward-fill.")
        df.ffill(inplace=True) # Forward-fill로 결측치 처리

    df.reset_index(inplace=True)
    # Date 컬럼의 타입을 datetime에서 string으로 변경 (DB 호환성)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    logging.info(f"Successfully fetched and cleaned data for {ticker}.")
    return df

if __name__=="__main__":
    logging.info("--- Starting Batch Data Collection ---")
    logging.info(f"Target Tickers: {TICKERS}")
    
    db_manager = DatabaseManager(DB_PATH)
    
    # Loop through each ticker (각 종목에 대해 반복)
    for ticker in TICKERS:
        # 1. Fetch & Clean (수집 및 정제)
        data = fetch_stock_data(ticker, START_DATE, END_DATE)
        
        if data is not None:
            # 2. Save (저장)
            table_name = f"{ticker}_daily"
            try:
                with db_manager as db:
                    db.save_dataframe(data, table_name)
            except Exception as e:
                logging.error(f"Failed to process and save data for {ticker}: {e}")
        
        # Be polite to the API server (API 서버에 부하를 주지 않기 위해 잠시 대기)
        logging.info("Waiting for 1 second before next request...")
        time.sleep(1) 

    logging.info("--- All tasks completed! ---")
