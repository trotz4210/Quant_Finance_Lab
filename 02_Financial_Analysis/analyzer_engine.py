import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import acf

class InsightGenerator:
    """
    통계 지표를 기반으로 의미있는 인사이트를 생성합니다.
    """
    
    @staticmethod
    def interpret_skewness(skewness):
        """왜도 해석"""
        if abs(skewness) < 0.5:
            return "거의 대칭적 분포 (정규분포에 가까움)"
        elif skewness > 0.5:
            return f"우측 꼬리가 긴 분포 → 극단적 상승장이 드물게 발생"
        else:  # skewness < -0.5
            return f"좌측 꼬리가 긴 분포 → 극단적 하락장이 자주 발생 (위험)"
    
    @staticmethod
    def interpret_kurtosis(kurtosis):
        """첨도 해석 (초과 첨도)"""
        if abs(kurtosis) < 0.5:
            return "정규분포 수준의 꼬리 두께"
        elif kurtosis > 0.5:
            return "뚱뚱한 꼬리 (극단값 자주 발생) → 극한 사건 위험 높음"
        else:  # kurtosis < -0.5
            return "가는 꼬리 (극단값 드물게 발생) → 예측 가능한 수익률"
    
    @staticmethod
    def jarque_bera_test(returns):
        """
        Jarque-Bera 정규성 검정
        Returns: {p_value, is_normal, interpretation}
        """
        jb_stat, p_value = stats.jarque_bera(returns)
        is_normal = bool(p_value > 0.05)  # 유의수준 5%
        
        # p-value가 충분히 작으면 과학적 표기법 사용
        if p_value < 0.001:
            p_value_str = f"{p_value:.2e}"
        else:
            p_value_str = f"{p_value:.4f}"
        
        interpretation = (
            "✓ 정규분포로 보아도 무방합니다. (p-value > 0.05)"
            if is_normal
            else "✗ 유의미하게 정규분포를 벗어났습니다. (p-value < 0.05) "
            "→ 극단값이 정규분포보다 자주 발생할 수 있습니다."
        )
        
        return {
            'jb_statistic': float(jb_stat),
            'p_value': float(p_value),
            'p_value_str': p_value_str,  # 포매팅된 문자열 추가
            'is_normal': int(is_normal),  # JSON serializable하게 int로 변환
            'interpretation': interpretation
        }
    
    @staticmethod
    def portfolio_risk_insights(returns, mean, std):
        """
        포트폴리오 관점의 위험 평가
        """
        var_95 = np.percentile(returns, 5)  # 95% VaR
        sharpe = mean / std if std != 0 else 0  # Sharpe Ratio (무위험이율=0)
        
        return {
            'var_95': float(var_95),  # 하루 5% 확률로 이 이상 손실 가능
            'sharpe_ratio': float(sharpe),
            'var_interpretation': f"95% 신뢰도: 하루에 {var_95*100:.2f}% 이상 손실 가능성 5%"
        }


class TimeSeriesAnalyzer:
    """
    금융 시계열 분석 엔진
    모든 분석 로직을 한 곳에서 관리
    """
    
    @staticmethod
    def calculate_statistics(returns):
        """일일 수익률의 기본 통계"""
        return {
            'mean': float(np.mean(returns)),
            'std': float(np.std(returns)),
            'min': float(np.min(returns)),
            'max': float(np.max(returns)),
            'skewness': float(stats.skew(returns)),
            'kurtosis': float(stats.kurtosis(returns))
        }

    @staticmethod
    def calculate_histogram(returns, bins=20):
        """수익률 분포 (히스토그램 데이터)"""
        counts, bin_edges = np.histogram(returns, bins=bins)
        bin_labels = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges)-1)]
        return {
            'bin_labels': [float(x) for x in bin_labels],
            'counts': [int(x) for x in counts]
        }

    @staticmethod
    def calculate_qq_plot(returns):
        """Q-Q Plot 데이터 (정규성 검정)"""
        sorted_returns = np.sort(returns)
        N = len(sorted_returns)
        theoretical_quantiles = stats.norm.ppf(np.arange(1, N+1) / (N+1))
        
        return {
            'theoretical': [float(x) for x in theoretical_quantiles],
            'sample': [float(x) for x in sorted_returns]
        }

    @staticmethod
    def calculate_acf(returns, nlags=30):
        """자기상관 분석 (ACF)"""
        acf_values = acf(returns, nlags=nlags, fft=False)
        return [float(x) for x in acf_values]

    @staticmethod
    def analyze_ticker(df):
        """
        공통 분석 파이프라인
        df: Date, Close 컬럼을 포함한 DataFrame
        Returns: 모든 분석 결과를 담은 dict
        """
        if df is None or df.empty or 'Close' not in df.columns:
            return None
        
        # 날짜 정렬
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        
        # 일일 수익률 계산
        returns = df['Close'].pct_change().dropna().values
        
        if len(returns) == 0:
            return None
        
        # 가격 이력
        price_history = {
            'dates': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
            'prices': df['Close'].tolist()
        }
        
        # 기본 통계
        statistics = TimeSeriesAnalyzer.calculate_statistics(returns)
        
        # 정규성 검정 및 인사이트 추가
        jb_test = InsightGenerator.jarque_bera_test(returns)
        statistics['normalcy_test'] = jb_test
        
        # 왜도/첨도 해석 추가
        skewness_interpretation = InsightGenerator.interpret_skewness(statistics['skewness'])
        kurtosis_interpretation = InsightGenerator.interpret_kurtosis(statistics['kurtosis'])
        
        statistics['skewness_interpretation'] = skewness_interpretation
        statistics['kurtosis_interpretation'] = kurtosis_interpretation
        
        # 위험도 지표 추가
        risk_insights = InsightGenerator.portfolio_risk_insights(returns, statistics['mean'], statistics['std'])
        statistics['risk'] = risk_insights
        
        # 모든 분석 수행
        return {
            'price_history': price_history,
            'statistics': statistics,
            'histogram': TimeSeriesAnalyzer.calculate_histogram(returns),
            'qq_plot': TimeSeriesAnalyzer.calculate_qq_plot(returns),
            'acf': TimeSeriesAnalyzer.calculate_acf(returns)
        }
