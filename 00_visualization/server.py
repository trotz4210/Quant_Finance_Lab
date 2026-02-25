import sys
import os
import json
from datetime import datetime
import numpy as np
import pandas as pd
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from scipy import stats
from statsmodels.tsa.stattools import acf

# 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '01_Data_Engineering'))

from database_manager import DatabaseManager

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # CORS 활성화

# DB 경로
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '01_Data_Engineering', 'market_data.db')

def get_ticker_tables():
    """DB의 모든 ticker 테이블 조회"""
    try:
        with DatabaseManager(DB_PATH) as db:
            cursor = db.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_daily'")
            tables = cursor.fetchall()
            return [table[0].replace('_daily', '') for table in tables]
    except Exception as e:
        print(f"Error getting ticker tables: {e}")
        return []

def calculate_statistics(returns):
    """일일 수익률 통계 계산"""
    return {
        'mean': float(np.mean(returns)),
        'std': float(np.std(returns)),
        'min': float(np.min(returns)),
        'max': float(np.max(returns)),
        'skewness': float(stats.skew(returns)),
        'kurtosis': float(stats.kurtosis(returns))
    }

def calculate_histogram(returns, bins=20):
    """수익률 분포"""
    counts, bin_edges = np.histogram(returns, bins=bins)
    bin_labels = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges)-1)]
    return {
        'bin_labels': [float(x) for x in bin_labels],
        'counts': [int(x) for x in counts]
    }

def calculate_qq_plot(returns):
    """Q-Q Plot 데이터"""
    sorted_returns = np.sort(returns)
    N = len(sorted_returns)
    theoretical_quantiles = stats.norm.ppf(np.arange(1, N+1) / (N+1))
    
    return {
        'theoretical': [float(x) for x in theoretical_quantiles],
        'sample': [float(x) for x in sorted_returns]
    }

def calculate_acf(returns, nlags=30):
    """자기상관 (ACF)"""
    acf_values = acf(returns, nlags=nlags, fft=False)
    return [float(x) for x in acf_values]

def get_ticker_data(ticker):
    """DB에서 종목 데이터 조회 및 분석"""
    try:
        with DatabaseManager(DB_PATH) as db:
            table_name = f'{ticker}_daily'
            df = db.read_dataframe(table_name)
            
            if df is None or df.empty:
                return None
            
            # 가격 데이터
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            
            # 일일 수익률 계산
            returns = df['Close'].pct_change().dropna().values
            
            if len(returns) == 0:
                return None
            
            # 통계 계산
            price_history = {
                'dates': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
                'prices': df['Close'].tolist()
            }
            
            statistics = calculate_statistics(returns)
            histogram = calculate_histogram(returns)
            qq_plot = calculate_qq_plot(returns)
            acf_values = calculate_acf(returns)
            
            return {
                'statistics': statistics,
                'price_history': price_history,
                'histogram': histogram,
                'qq_plot': qq_plot,
                'acf': acf_values
            }
    except Exception as e:
        print(f"Error getting data for {ticker}: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/api/data')
def get_data():
    """모든 ticker 데이터 조회"""
    print("API 호출: /api/data")
    tickers = get_ticker_tables()
    print(f"발견된 종목: {tickers}")
    
    data = {
        'tickers': {},
        'timestamp': datetime.now().isoformat()
    }
    
    for ticker in tickers:
        print(f"처리 중: {ticker}")
        ticker_data = get_ticker_data(ticker)
        if ticker_data:
            data['tickers'][ticker] = ticker_data
            print(f"  ✓ {ticker} 완료")
        else:
            print(f"  ✗ {ticker} 실패")
    
    print(f"총 {len(data['tickers'])}개 종목 데이터 반환")
    return jsonify(data)

@app.route('/api/ticker/<ticker>')
def get_single_ticker(ticker):
    """특정 ticker 데이터 조회"""
    ticker_data = get_ticker_data(ticker)
    
    if ticker_data is None:
        return jsonify({'error': f'Ticker {ticker} not found'}), 404
    
    return jsonify({
        'ticker': ticker,
        'data': ticker_data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def serve_index():
    """index.html 서빙"""
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    print(f"DB 경로: {DB_PATH}")
    print(f"DB 파일 존재: {os.path.exists(DB_PATH)}")
    print(f"종목 테이블 확인 중...")
    tickers = get_ticker_tables()
    print(f"발견된 종목: {tickers}")
    print("\n Flask 서버 시작 중... (http://localhost:8000)")
    app.run(debug=False, port=8000, host='127.0.0.1')

