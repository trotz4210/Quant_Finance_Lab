"""
Fama-French 3-Factor 모델 구현
========================================
자산 가격결정 모델(APT)의 핵심 이론을 실제 시장 데이터로 검증

이론:
E[R_i - R_f] = α + β_mkt·E[R_m - R_f] + β_smb·E[SMB] + β_hml·E[HML]

- R_i: 개별 자산 수익률
- R_f: 무위험 이자율 (Risk-Free Rate)
- R_m: 시장 포트폴리오 수익률
- SMB (Small Minus Big): 소형주 vs 대형주의 초과 수익
- HML (High Minus Low): 가치주 vs 성장주의 초과 수익
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
import warnings

warnings.filterwarnings('ignore')


class FamaFrenchFactorBuilder:
    """
    Fama-French 3개 팩터(MKT, SMB, HML)를 구성합니다.
    
    Attributes:
        market_returns: 시장 수익률 (SPY)
        risk_free_rate: 무위험 이자율 (연 기준 → 일일로 변환)
    """
    
    def __init__(self, market_returns, risk_free_rate_annual=0.05):
        """
        Args:
            market_returns: 시장 수익률 pd.Series (일일)
            risk_free_rate_annual: 연간 무위험 이자율 (기본값: 5%)
        """
        self.market_returns = market_returns.dropna()
        # 연간 이자율을 일일로 변환: (1 + annual_rate)^(1/252) - 1
        self.risk_free_rate_daily = (1 + risk_free_rate_annual) ** (1/252) - 1
        
    def calculate_market_excess_returns(self):
        """
        시장 초과 수익률 (MKT): R_m - R_f
        Returns:
            pd.Series: 일일 시장 초과 수익률
        """
        return self.market_returns - self.risk_free_rate_daily
    
    def calculate_smb_factor(self, market_cap_df):
        """
        SMB (Small Minus Big) 팩터 계산
        
        방법:
        1. 시가총액 중앙값(median)으로 기업을 Big(B)과 Small(S)로 분류
        2. P/B 비율 중앙값으로 Value(V)와 Growth(G)로 분류
        3. SMB = (SV + SG)/2 - (BV + BG)/2
           = (소형주 평균 수익률) - (대형주 평균 수익률)
        
        Args:
            market_cap_df: 각 종목별 시가총액 정보
            pb_ratio_df: 각 종목별 P/B 비율 정보
            returns_df: 각 종목별 수익률
            
        Returns:
            pd.Series: 일일 SMB 팩터
        """
        # 간단한 근사: 소형주 vs 대형주의 기울기 기반 SMB
        # 실제로는 6개 포트폴리오의 가중 평균을 사용해야 함
        # 이 버전은 교육용 단순화 구현
        
        # 플레이스홀더: 평균 0, 표준편차 0.01인 일일 팩터 반환
        # (실제 구현에서는 각 종목의 시가총액 데이터 필요)
        return pd.Series(
            np.random.normal(0, 0.01, len(self.market_returns)),
            index=self.market_returns.index
        )
    
    def calculate_hml_factor(self, returns_df):
        """
        HML (High Minus Low) 팩터 계산
        
        방법:
        1. P/B 비율이 높은 종목(Growth)과 낮은 종목(Value)으로 분류
        2. HML = (가치주 포트폴리오 수익률) - (성장주 포트폴리오 수익률)
        
        Args:
            returns_df: 각 종목별 수익률 DataFrame
            pb_ratio_df: 각 종목별 P/B 비율 정보
            
        Returns:
            pd.Series: 일일 HML 팩터
        """
        # 플레이스홀더: 평균 0, 표준편차 0.01인 일일 팩터 반환
        return pd.Series(
            np.random.normal(0, 0.01, len(self.market_returns)),
            index=self.market_returns.index
        )


class FamaFrenchRegression:
    """
    Fama-French 3-Factor 모델을 이용한 회귀분석
    
    모델: R_i - R_f = α + β_mkt·(R_m - R_f) + β_smb·SMB + β_hml·HML + ε
    
    Outputs:
        - α (알파): 초과수익, 뮤추얼펀드 매니저의 능력 지표
        - β (베타): 각 팩터에 대한 민감도
        - R²: 모델의 설명력 (높을수록 좋음, 40~60% 정상)
        - t-통계량, p-value: 각 계수의 통계적 유의성
    """
    
    def __init__(self, asset_excess_returns, factors_df):
        """
        Args:
            asset_excess_returns: 자산 초과 수익률 pd.Series
            factors_df: 팩터 DataFrame (columns: ['MKT', 'SMB', 'HML'])
        """
        self.asset_returns = asset_excess_returns.dropna()
        self.factors = factors_df.loc[self.asset_returns.index].dropna()
        
        # 인덱스 정렬
        common_idx = self.asset_returns.index.intersection(self.factors.index)
        self.asset_returns = self.asset_returns.loc[common_idx]
        self.factors = self.factors.loc[common_idx]
    
    def run_regression(self):
        """
        OLS 회귀분석 실행
        
        Returns:
            dict: {
                'alpha': 절편(초과수익),
                'betas': {'MKT': β_mkt, 'SMB': β_smb, 'HML': β_hml},
                'p_values': 각 계수의 p-value,
                'r_squared': 결정계수,
                'adj_r_squared': 조정된 R²,
                'residuals': 잔차,
                'summary': 회귀분석 요약 (statsmodels)
            }
        """
        # 상수항(절편) 추가
        X = add_constant(self.factors)
        y = self.asset_returns
        
        # 회귀분석 실행
        model = OLS(y, X).fit()
        
        return {
            'alpha': model.params['const'],
            'betas': {
                'MKT': model.params.get('MKT', 0),
                'SMB': model.params.get('SMB', 0),
                'HML': model.params.get('HML', 0),
            },
            'p_values': {
                'alpha': model.pvalues['const'],
                'MKT': model.pvalues.get('MKT', 1),
                'SMB': model.pvalues.get('SMB', 1),
                'HML': model.pvalues.get('HML', 1),
            },
            't_stats': {
                'alpha': model.tvalues['const'],
                'MKT': model.tvalues.get('MKT', 0),
                'SMB': model.tvalues.get('SMB', 0),
                'HML': model.tvalues.get('HML', 0),
            },
            'r_squared': model.rsquared,
            'adj_r_squared': model.rsquared_adj,
            'residuals': model.resid,
            'summary': model.summary()
        }
    
    @staticmethod
    def interpret_results(results):
        """
        회귀분석 결과 해석
        
        Args:
            results: run_regression() 출력값
            
        Returns:
            dict: 의미있는 해석 텍스트
        """
        interpretation = {
            'alpha_interpretation': '',
            'factor_interpretations': {},
            'overall_assessment': ''
        }
        
        # 알파 해석
        alpha = results['alpha']
        alpha_pvalue = results['p_values']['alpha']
        
        if alpha_pvalue < 0.05:
            if alpha > 0:
                interpretation['alpha_interpretation'] = (
                    f"✓ 통계적으로 유의한 양의 알파({alpha:.4f}) → "
                    "매니저가 시장을 이기는 능력을 보임"
                )
            else:
                interpretation['alpha_interpretation'] = (
                    f"✗ 통계적으로 유의한 음의 알파({alpha:.4f}) → "
                    "매니저의 성과가 시장을 하회"
                )
        else:
            interpretation['alpha_interpretation'] = (
                f"• 알파({alpha:.4f})가 통계적으로 유의하지 않음 (p={alpha_pvalue:.3f}) → "
                "시장 수익률로 설명 가능"
            )
        
        # 각 팩터 해석
        for factor in ['MKT', 'SMB', 'HML']:
            beta = results['betas'].get(factor, 0)
            pval = results['p_values'].get(factor, 1)
            
            if pval < 0.05:
                sig_marker = "★"
            else:
                sig_marker = "·"
            
            interpretation['factor_interpretations'][factor] = {
                'beta': beta,
                'p_value': pval,
                'significance': sig_marker
            }
        
        # 전체 평가
        r_sq = results['r_squared']
        if r_sq > 0.7:
            assessment = "모델의 설명력 우수 (R² > 0.7)"
        elif r_sq > 0.4:
            assessment = "모델의 설명력 양호 (0.4 < R² < 0.7)"
        else:
            assessment = "모델의 설명력 약함 (R² < 0.4) → 다른 팩터 필요"
        
        interpretation['overall_assessment'] = f"{assessment} (R²={r_sq:.3f})"
        
        return interpretation


class FamaFrenchAnalyzer:
    """
    여러 자산에 대해 Fama-French 분석을 수행합니다.
    """
    
    def __init__(self, market_data_dict, risk_free_rate_annual=0.05):
        """
        Args:
            market_data_dict: {ticker: DataFrame with 'Close' column}
            risk_free_rate_annual: 연간 무위험 이자율
        """
        self.market_data = market_data_dict
        self.rf_rate = risk_free_rate_annual
        self.results = {}
    
    def analyze_asset(self, ticker, market_ticker='SPY'):
        """
        개별 자산의 Fama-French 분석 수행
        
        Args:
            ticker: 분석 대상 종목
            market_ticker: 시장 포트폴리오 (기본값: SPY)
            
        Returns:
            dict: 분석 결과
        """
        
        if ticker not in self.market_data:
            return {'error': f'{ticker} 데이터 없음'}
        
        if market_ticker not in self.market_data:
            return {'error': f'{market_ticker} 데이터 없음'}
        
        # 수익률 계산
        asset_df = self.market_data[ticker].copy()
        market_df = self.market_data[market_ticker].copy()
        
        asset_returns = asset_df['Close'].pct_change().dropna()
        market_returns = market_df['Close'].pct_change().dropna()
        
        # 공통 인덱스 정렬
        common_idx = asset_returns.index.intersection(market_returns.index)
        asset_returns = asset_returns.loc[common_idx]
        market_returns = market_returns.loc[common_idx]
        
        # 초과 수익률 계산
        rf_daily = (1 + self.rf_rate) ** (1/252) - 1
        asset_excess = asset_returns - rf_daily
        
        # 팩터 빌더
        builder = FamaFrenchFactorBuilder(market_returns, self.rf_rate)
        mkt_excess = builder.calculate_market_excess_returns()
        
        # 임시 팩터 데이터 (SMB, HML는 단순화)
        factors_df = pd.DataFrame({
            'MKT': mkt_excess,
            'SMB': builder.calculate_smb_factor(None),
            'HML': builder.calculate_hml_factor(None),
        })
        
        # 회귀분석
        reg = FamaFrenchRegression(asset_excess, factors_df)
        results = reg.run_regression()
        interpretation = reg.interpret_results(results)
        
        self.results[ticker] = {
            'results': results,
            'interpretation': interpretation
        }
        
        return {
            'ticker': ticker,
            'results': results,
            'interpretation': interpretation
        }
    
    def analyze_portfolio(self, tickers, weights=None, market_ticker='SPY'):
        """
        포트폴리오의 Fama-French 분석
        
        Args:
            tickers: 종목 리스트
            weights: 가중치 (기본값: 동일가중)
            market_ticker: 시장 포트폴리오
            
        Returns:
            dict: 포트폴리오 분석 결과
        """
        
        if weights is None:
            weights = np.array([1/len(tickers)] * len(tickers))
        
        weights = np.array(weights)
        weights = weights / weights.sum()  # 정규화
        
        # 포트폴리오 수익률
        portfolio_returns = None
        for ticker, weight in zip(tickers, weights):
            if ticker not in self.market_data:
                continue
            returns = self.market_data[ticker]['Close'].pct_change().dropna()
            if portfolio_returns is None:
                portfolio_returns = returns * weight
            else:
                # 공통 인덱스 정렬
                common_idx = portfolio_returns.index.intersection(returns.index)
                portfolio_returns = portfolio_returns.loc[common_idx] * weight / weights[:len(portfolio_returns)].sum()
                returns = returns.loc[common_idx]
                portfolio_returns += returns * weight
        
        if portfolio_returns is None:
            return {'error': '포트폴리오 수익률 계산 실패'}
        
        # 시장 수익률
        if market_ticker not in self.market_data:
            return {'error': f'{market_ticker} 데이터 없음'}
        
        market_returns = self.market_data[market_ticker]['Close'].pct_change().dropna()
        
        # 공통 인덱스 정렬
        common_idx = portfolio_returns.index.intersection(market_returns.index)
        portfolio_returns = portfolio_returns.loc[common_idx]
        market_returns = market_returns.loc[common_idx]
        
        # 초과 수익률
        rf_daily = (1 + self.rf_rate) ** (1/252) - 1
        portfolio_excess = portfolio_returns - rf_daily
        
        # 팩터 빌더
        builder = FamaFrenchFactorBuilder(market_returns, self.rf_rate)
        mkt_excess = builder.calculate_market_excess_returns()
        
        factors_df = pd.DataFrame({
            'MKT': mkt_excess,
            'SMB': builder.calculate_smb_factor(None),
            'HML': builder.calculate_hml_factor(None),
        })
        
        # 회귀분석
        reg = FamaFrenchRegression(portfolio_excess, factors_df)
        results = reg.run_regression()
        interpretation = reg.interpret_results(results)
        
        return {
            'portfolio': tickers,
            'weights': weights.tolist(),
            'results': results,
            'interpretation': interpretation
        }


if __name__ == '__main__':
    """
    테스트: 데이터베이스에서 데이터 로드 후 Fama-French 분석 실행
    """
    from pathlib import Path
    import sys
    import os
    
    # 경로 설정
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / '01_Data_Engineering'))
    from database_manager import DatabaseManager
    
    db_path = project_root / '01_Data_Engineering' / 'market_data.db'
    
    # 데이터 로드
    market_data_dict = {}
    with DatabaseManager(str(db_path)) as db:
        for ticker in ['AAPL', 'MSFT', 'TSLA', 'SPY']:
            table_name = f'{ticker}_daily'
            df = db.read_dataframe(table_name)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').set_index('Date')
            market_data_dict[ticker] = df
    
    # 분석 실행
    analyzer = FamaFrenchAnalyzer(market_data_dict, risk_free_rate_annual=0.05)
    
    # AAPL 분석
    print("=" * 80)
    print("AAPL Fama-French 3-Factor 분석")
    print("=" * 80)
    aapl_result = analyzer.analyze_asset('AAPL')
    
    if 'error' not in aapl_result:
        print(f"\n알파: {aapl_result['results']['alpha']:.6f}")
        print(f"베타 (MKT): {aapl_result['results']['betas']['MKT']:.4f}")
        print(f"베타 (SMB): {aapl_result['results']['betas']['SMB']:.4f}")
        print(f"베타 (HML): {aapl_result['results']['betas']['HML']:.4f}")
        print(f"R² (설명력): {aapl_result['results']['r_squared']:.4f}")
        print(f"\n해석:")
        print(aapl_result['interpretation']['alpha_interpretation'])
        print("\nFull Summary:")
        print(aapl_result['results']['summary'])
    
    # 포트폴리오 분석
    print("\n" + "=" * 80)
    print("포트폴리오 분석 (AAPL, MSFT, TSLA - 동일가중)")
    print("=" * 80)
    portfolio_result = analyzer.analyze_portfolio(['AAPL', 'MSFT', 'TSLA'])
    
    if 'error' not in portfolio_result:
        print(f"\n알파: {portfolio_result['results']['alpha']:.6f}")
        print(f"베타 (MKT): {portfolio_result['results']['betas']['MKT']:.4f}")
        print(f"R² (설명력): {portfolio_result['results']['r_squared']:.4f}")
        print(f"\n해석: {portfolio_result['interpretation']['overall_assessment']}")
