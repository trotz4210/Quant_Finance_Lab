"""
시계열 분석 데이터를 JSON으로 변환하는 스크립트
"""
import json
import sys
from pathlib import Path
import pandas as pd
from scipy import stats
import statsmodels.api as sm

# Add 01_Data_Engineering to path
DATA_ENG = Path(__file__).resolve().parent.parent / "01_Data_Engineering"
if str(DATA_ENG) not in sys.path:
    sys.path.insert(0, str(DATA_ENG))

from database_manager import DatabaseManager

# 02_Financial_Analysis에서 필요한 것들 import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "02_Financial_Analysis"))

# 설정
DB_PATH = str(DATA_ENG / "market_data.db")
TICKERS = ["AAPL", "MSFT", "TSLA", "SPY"]

def load_data_from_db(ticker: str) -> pd.DataFrame:
    """데이터베이스에서 데이터 로드"""
    table_name = f"{ticker}_daily"
    df = pd.DataFrame()
    try:
        with DatabaseManager(DB_PATH) as db:
            df = pd.read_sql_query(f"SELECT Date, Close FROM {table_name}", db.conn)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
    except Exception as e:
        print(f"Error loading data for {ticker}: {e}")
    return df

def calculate_statistics(returns):
    """수익률 통계 계산"""
    return {
        "mean": float(returns.mean()),
        "std": float(returns.std()),
        "min": float(returns.min()),
        "max": float(returns.max()),
        "skewness": float(returns.skew()),
        "kurtosis": float(returns.kurtosis())
    }

def generate_chart_data():
    """모든 티커의 차트 데이터 생성"""
    data = {
        "tickers": {},
        "timestamp": pd.Timestamp.now().isoformat()
    }

    for ticker in TICKERS:
        # 데이터 로드
        stock_data = load_data_from_db(ticker)
        
        if stock_data.empty:
            print(f"Failed to load data for {ticker}")
            continue

        # 수익률 계산
        if 'Close' not in stock_data.columns:
            print(f"'Close' column not found for {ticker}")
            continue

        returns = stock_data['Close'].pct_change().dropna()
        
        if returns.empty:
            print(f"No returns data for {ticker}")
            continue

        # 히스토그램 데이터 (bins 생성)
        hist, bin_edges = pd.cut(returns, bins=40, retbins=True, duplicates='drop')
        hist_counts = hist.value_counts().sort_index()
        
        # Q-Q 플롯 데이터
        qq_result = stats.probplot(returns, dist="norm")
        theoretical_quantiles = qq_result[0][0]
        sample_quantiles = qq_result[0][1]
        
        # ACF 데이터
        acf_values = sm.graphics.tsa.acf(returns, nlags=30)
        
        # 가격 시계열 데이터
        price_data = stock_data['Close'].reset_index()
        price_data['Date'] = price_data['Date'].dt.strftime('%Y-%m-%d')
        
        data["tickers"][ticker] = {
            "returns": returns.tolist(),
            "histogram": {
                "bins": bin_edges.tolist(),
                "counts": hist_counts.values.tolist(),
                "bin_labels": [f"{b:.4f}" for b in bin_edges[:-1]]
            },
            "qq_plot": {
                "theoretical": theoretical_quantiles.tolist(),
                "sample": sample_quantiles.tolist()
            },
            "acf": acf_values.tolist(),
            "price_history": {
                "dates": price_data['Date'].tolist(),
                "prices": price_data['Close'].tolist()
            },
            "statistics": calculate_statistics(returns)
        }

    return data

def save_data_to_json(data, output_file):
    """데이터를 JSON 파일로 저장"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    # 데이터 생성
    chart_data = generate_chart_data()
    
    # JSON 파일로 저장
    output_path = Path(__file__).resolve().parent / "data.json"
    save_data_to_json(chart_data, output_path)
    
    print(f"Successfully generated visualization data for {list(chart_data['tickers'].keys())}")
