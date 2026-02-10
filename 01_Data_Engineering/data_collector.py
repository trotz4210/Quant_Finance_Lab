import yfinance as yf
import pandas as pd
import sqlite3
import os
import time

# 1. Settings (설정)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "market_data.db")

# List of tickers to download (다운로드할 종목 리스트)
# 'SPY' is an ETF that tracks S&P 500 (SPY는 S&P 500을 추종하는 ETF)
TICKERS = ["AAPL", "MSFT", "TSLA", "SPY"] 

START_DATE = "2020-01-01"   
END_DATE = "2023-12-31"     

def fetch_stock_data(ticker, start, end):
    print(f"\n[Processing] Downloading {ticker}...")
    
    # Download data (데이터 다운로드)
    # progress=False: Hide the default progress bar of yfinance (yfinance 기본 진행바 숨기기)
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)

    if df.empty:
        print(f"Error: No data for {ticker}. (오류: 데이터 없음)")
        return None
    
    df.reset_index(inplace=True)
    return df

def save_to_database(df, ticker, db_path):
    if df is None:
        return
    
    conn = sqlite3.connect(db_path)

    try:
        # Table name: e.g., AAPL_daily (테이블 이름: 예, AAPL_daily)
        table_name = f"{ticker}_daily"
        
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Success: Saved {len(df)} rows to table '{table_name}'. (성공: {len(df)}행 저장 완료)")

    except Exception as e:
        print(f"Error saving {ticker}: {e}")
    
    finally:
        conn.close()

if __name__=="__main__":
    print(f"Start Batch Processing... (일괄 처리 시작)")
    print(f"Target Tickers: {TICKERS}")
    
    # Loop through each ticker (각 종목에 대해 반복)
    for ticker in TICKERS:
        # 1. Fetch (수집)
        data = fetch_stock_data(ticker, START_DATE, END_DATE)
        
        # 2. Save (저장)
        save_to_database(data, ticker, DB_PATH)
        
        # Be polite to the API server (API 서버에 부하를 주지 않기 위해 잠시 대기)
        time.sleep(1) 

    print("\nAll tasks completed! (모든 작업 완료)")
