import sys
import os
from datetime import datetime
import pandas as pd
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# 경로 설정
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_ENG_PATH = os.path.join(PROJECT_ROOT, '01_Data_Engineering')
ANALYSIS_PATH = os.path.join(PROJECT_ROOT, '02_Financial_Analysis')

sys.path.insert(0, DATA_ENG_PATH)
sys.path.insert(0, ANALYSIS_PATH)

from database_manager import DatabaseManager
from analyzer_engine import TimeSeriesAnalyzer

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

def get_ticker_data(ticker):
    """DB에서 종목 데이터 조회 및 분석"""
    try:
        with DatabaseManager(DB_PATH) as db:
            table_name = f'{ticker}_daily'
            df = db.read_dataframe(table_name)
            
            if df is None or df.empty:
                return None
            
            # TimeSeriesAnalyzer를 사용하여 모든 분석 수행
            return TimeSeriesAnalyzer.analyze_ticker(df)
    except Exception as e:
        print(f"Error getting data for {ticker}: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/api/data')
def get_data():
    """모든 ticker 데이터 조회"""
    try:
        print("\n=== API 호출: /api/data ===")
        tickers = get_ticker_tables()
        print(f"발견된 종목: {tickers}")
        
        if not tickers:
            print("✗ 종목을 찾을 수 없습니다.")
            return jsonify({'error': 'No tickers found', 'tickers': {}, 'timestamp': datetime.now().isoformat()}), 200
        
        data = {
            'tickers': {},
            'timestamp': datetime.now().isoformat()
        }
        
        for ticker in tickers:
            print(f"\n처리 중: {ticker}")
            ticker_data = get_ticker_data(ticker)
            if ticker_data:
                data['tickers'][ticker] = ticker_data
                print(f"  ✓ {ticker} 완료")
            else:
                print(f"  ✗ {ticker} 실패")
        
        print(f"\n총 {len(data['tickers'])}개 종목 데이터 반환")
        return jsonify(data), 200
    except Exception as e:
        print(f"API 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

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
    print("\n" + "="*50)
    print("Flask 서버 초기화 중...")
    print("="*50)
    print(f"현재 디렉토리: {os.path.abspath('.')}")
    print(f"DB 경로: {DB_PATH}")
    print(f"DB 파일 존재: {os.path.exists(DB_PATH)}")
    
    if os.path.exists(DB_PATH):
        print("\n종목 테이블 확인 중...")
        tickers = get_ticker_tables()
        print(f"발견된 종목: {tickers}")
    else:
        print("\n⚠️  DB 파일을 찾을 수 없습니다!")
    
    print("\n" + "="*50)
    print("Flask 서버 시작: http://127.0.0.1:8000")
    print("="*50 + "\n")
    
    app.run(debug=False, port=8000, host='127.0.0.1')

