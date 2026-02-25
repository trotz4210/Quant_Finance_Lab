let chartData = null;
let factorData = null;

const TICKER_COLORS = {
    'AAPL': '#555555',
    'MSFT': '#3498db',
    'TSLA': '#e74c3c',
    'SPY': '#27ae60'
};

// ===== 탭 네비게이션 =====
document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
        const tabName = e.target.dataset.tab;
        
        // 탭 활성화
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        
        // 컨텐츠 표시
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        document.getElementById(`${tabName}-tab`).classList.remove('hidden');
    });
});

// ===== 데이터 로드 =====
async function loadData() {
    try {
        console.log("API 호출 시작: /api/data");
        const response = await fetch('/api/data');
        console.log("API 응답 상태:", response.status);
        
        if (!response.ok) {
            const error = await response.text();
            console.error("API 오류:", response.status, error);
            throw new Error(`API 호출 실패: ${response.status}`);
        }
        
        chartData = await response.json();
        console.log("데이터 로드 완료:", chartData);
        buildTimeSeriesUI();
        renderAllCharts();
        await loadFactorAnalysis();
        return true;
    } catch (error) {
        console.error('Error:', error);
        alert('데이터 로드 실패: ' + error.message);
        return false;
    }
}

// ===== 동적 UI 구성 (시계열 분석) =====
function buildTimeSeriesUI() {
    if (!chartData || !chartData.tickers) return;

    const container = document.getElementById('timeseries-container');
    container.innerHTML = '';

    const tickers = Object.keys(chartData.tickers);

    tickers.forEach(ticker => {
        const section = document.createElement('div');
        section.className = 'ticker-section';
        section.id = `section-${ticker}`;

        section.innerHTML = `
            <div class="ticker-header">
                <h2>${ticker}</h2>
            </div>
            <div class="ticker-content">
                <div class="stats-insights">
                    <table class="stats-table">
                        <tr>
                            <td class="stat-label">평균</td>
                            <td class="stat-value stat-mean" data-ticker="${ticker}">-</td>
                            <td class="stat-label">변동성</td>
                            <td class="stat-value stat-std" data-ticker="${ticker}">-</td>
                            <td class="stat-label">최소</td>
                            <td class="stat-value stat-min" data-ticker="${ticker}">-</td>
                            <td class="stat-label">최대</td>
                            <td class="stat-value stat-max" data-ticker="${ticker}">-</td>
                        </tr>
                        <tr>
                            <td class="stat-label">왜도</td>
                            <td class="stat-value stat-skew" data-ticker="${ticker}">-</td>
                            <td class="stat-label">첨도</td>
                            <td class="stat-value stat-kurt" data-ticker="${ticker}">-</td>
                            <td colspan="4" class="jb-result" data-ticker="${ticker}">-</td>
                        </tr>
                    </table>
                    <div class="insights-compact">
                        <div class="insight-row">
                            <span class="insight-label">왜도:</span>
                            <span class="skewness-interpretation" data-ticker="${ticker}">-</span>
                        </div>
                        <div class="insight-row">
                            <span class="insight-label">첨도:</span>
                            <span class="kurtosis-interpretation" data-ticker="${ticker}">-</span>
                        </div>
                        <div class="insight-row">
                            <span class="insight-label">VaR(95%):</span>
                            <span class="risk-insight" data-ticker="${ticker}">-</span>
                        </div>
                    </div>
                </div>
                <div class="charts-compact">
                    <div class="chart-item"><div id="priceChart-${ticker}" class="chart"></div></div>
                    <div class="chart-item"><div id="histogramChart-${ticker}" class="chart"></div></div>
                    <div class="chart-item"><div id="qqChart-${ticker}" class="chart"></div></div>
                    <div class="chart-item"><div id="acfChart-${ticker}" class="chart"></div></div>
                </div>
            </div>
        `;

        container.appendChild(section);
    });
}

// ===== 통계 업데이트 =====
function updateStats(ticker) {
    if (!chartData || !chartData.tickers[ticker]) return;

    const stats = chartData.tickers[ticker].statistics;
    document.querySelector(`.stat-mean[data-ticker="${ticker}"]`).textContent = (stats.mean * 100).toFixed(2) + '%';
    document.querySelector(`.stat-std[data-ticker="${ticker}"]`).textContent = (stats.std * 100).toFixed(2) + '%';
    document.querySelector(`.stat-min[data-ticker="${ticker}"]`).textContent = (stats.min * 100).toFixed(2) + '%';
    document.querySelector(`.stat-max[data-ticker="${ticker}"]`).textContent = (stats.max * 100).toFixed(2) + '%';
    document.querySelector(`.stat-skew[data-ticker="${ticker}"]`).textContent = stats.skewness.toFixed(3);
    document.querySelector(`.stat-kurt[data-ticker="${ticker}"]`).textContent = stats.kurtosis.toFixed(3);

    // 정규성 검정 결과 (간결하게)
    if (stats.normalcy_test) {
        const jbTest = stats.normalcy_test;
        const resultText = jbTest.is_normal ? '✓ 정규' : '✗ 비정규';
        document.querySelector(`.jb-result[data-ticker="${ticker}"]`).textContent = `${resultText} (p=${jbTest.p_value_str})`;
    }

    // 왜도/첨도 해석 (간결하게)
    if (stats.skewness_interpretation) {
        document.querySelector(`.skewness-interpretation[data-ticker="${ticker}"]`).textContent = stats.skewness_interpretation;
    }

    if (stats.kurtosis_interpretation) {
        document.querySelector(`.kurtosis-interpretation[data-ticker="${ticker}"]`).textContent = stats.kurtosis_interpretation;
    }

    // 위험도 지표 (간결하게, 한줄)
    if (stats.risk) {
        const varText = (stats.risk.var_95 * 100).toFixed(1) + '%';
        const sharpeText = stats.risk.sharpe_ratio.toFixed(3);
        const riskText = `VaR95%: ${varText} | Sharpe: ${sharpeText}`;
        document.querySelector(`.risk-insight[data-ticker="${ticker}"]`).textContent = riskText;
    }
}

// ===== 차트 렌더링 =====
function renderPriceChart(ticker) {
    if (!chartData || !chartData.tickers[ticker]) return;
    
    const data = chartData.tickers[ticker].price_history;
    const color = TICKER_COLORS[ticker] || '#555555';
    
    const trace = {
        x: data.dates,
        y: data.prices,
        type: 'scatter',
        mode: 'lines',
        name: ticker,
        line: { color, width: 0.8 },
        fill: 'tozeroy',
        fillcolor: color + '20'
    };

    const layout = {
        margin: { l: 20, r: 5, t: 2, b: 15 },
        hovermode: 'x unified',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif', size: 7 },
        xaxis: { showgrid: false },
        yaxis: { showgrid: true, gridwidth: 0.3, gridcolor: '#f0f0f0' }
    };

    Plotly.newPlot(`priceChart-${ticker}`, [trace], layout, { responsive: true, displayModeBar: false });
}

function renderHistogram(ticker) {
    if (!chartData || !chartData.tickers[ticker]) return;

    const hist = chartData.tickers[ticker].histogram;
    const color = TICKER_COLORS[ticker] || '#555555';
    
    const trace = {
        x: hist.bin_labels.map((_, i) => (i / hist.bin_labels.length).toFixed(4)),
        y: hist.counts,
        type: 'bar',
        marker: {
            color,
            opacity: 0.75,
            line: { color, width: 0.3 }
        }
    };

    const layout = {
        margin: { l: 20, r: 5, t: 2, b: 15 },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif', size: 7 },
        xaxis: { showgrid: false },
        yaxis: { showgrid: true, gridwidth: 0.3, gridcolor: '#f0f0f0' }
    };

    Plotly.newPlot(`histogramChart-${ticker}`, [trace], layout, { responsive: true, displayModeBar: false });
}

function renderQQPlot(ticker) {
    if (!chartData || !chartData.tickers[ticker]) return;

    const qqData = chartData.tickers[ticker].qq_plot;
    const color = TICKER_COLORS[ticker] || '#555555';
    
    const sample = {
        x: qqData.theoretical,
        y: qqData.sample,
        mode: 'markers',
        name: '',
        marker: { color, size: 2.5, opacity: 0.7 }
    };

    const minVal = Math.min(...qqData.theoretical);
    const maxVal = Math.max(...qqData.theoretical);
    const reference = {
        x: [minVal, maxVal],
        y: [minVal, maxVal],
        mode: 'lines',
        name: '',
        line: { color: '#bdc3c7', width: 0.8, dash: 'dash' }
    };

    const yMin = Math.min(...qqData.sample);
    const yMax = Math.max(...qqData.sample);
    const yRange = yMax - yMin;
    const yPadding = yRange * 0.1;

    const layout = {
        margin: { l: 20, r: 5, t: 2, b: 15 },
        hovermode: 'closest',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif', size: 7 },
        showlegend: false,
        xaxis: { showgrid: false },
        yaxis: { showgrid: true, gridwidth: 0.3, gridcolor: '#f0f0f0', range: [yMin - yPadding, yMax + yPadding] }
    };

    Plotly.newPlot(`qqChart-${ticker}`, [sample, reference], layout, { responsive: true, displayModeBar: false });
}

function renderACFPlot(ticker) {
    if (!chartData || !chartData.tickers[ticker]) return;

    const acf = chartData.tickers[ticker].acf;
    const color = TICKER_COLORS[ticker] || '#555555';
    const lags = Array.from({ length: acf.length }, (_, i) => i);

    const trace = {
        x: lags,
        y: acf,
        type: 'bar',
        marker: { color, opacity: 0.75, line: { color, width: 0.3 } }
    };

    const confidenceInterval = 1.96 / Math.sqrt(1000);
    const upperBound = {
        x: [0, Math.max(...lags)],
        y: [confidenceInterval, confidenceInterval],
        mode: 'lines',
        name: '',
        line: { color: '#bdc3c7', width: 0.5, dash: 'dash' }
    };

    const lowerBound = {
        x: [0, Math.max(...lags)],
        y: [-confidenceInterval, -confidenceInterval],
        mode: 'lines',
        line: { color: '#bdc3c7', width: 0.5, dash: 'dash' },
        showlegend: false
    };

    const layout = {
        margin: { l: 20, r: 5, t: 2, b: 15 },
        hovermode: 'x unified',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif', size: 7 },
        xaxis: { showgrid: false },
        yaxis: { showgrid: true, gridwidth: 0.3, gridcolor: '#f0f0f0' }
    };

    Plotly.newPlot(`acfChart-${ticker}`, [trace, upperBound, lowerBound], layout, { responsive: true, displayModeBar: false });
}

// ===== 모든 차트 렌더링 =====
function renderAllCharts() {
    if (!chartData || !chartData.tickers) return;

    const tickers = Object.keys(chartData.tickers);
    tickers.forEach(ticker => {
        renderPriceChart(ticker);
        renderHistogram(ticker);
        renderQQPlot(ticker);
        renderACFPlot(ticker);
        updateStats(ticker);
    });

    const updateTime = new Date(chartData.timestamp).toLocaleString('ko-KR');
    document.getElementById('updateTime').textContent = updateTime;
}

// ===== 팩터 분석 로드 =====
async function loadFactorAnalysis() {
    try {
        console.log("API 호출 시작: 팩터 분석");
        
        const container = document.getElementById('factors-container');
        container.innerHTML = '<p style="padding: 12px; color: #666;">로딩 중...</p>';
        
        // 개별 팩터 분석
        const tickers = Object.keys(chartData.tickers || {});
        const allResults = {};
        
        for (const ticker of tickers) {
            try {
                const response = await fetch(`/api/factor-analysis/${ticker}`);
                if (response.ok) {
                    allResults[ticker] = await response.json();
                }
            } catch (error) {
                console.error(`팩터 분석 오류 (${ticker}):`, error);
            }
        }
        
        // 포트폴리오 분석
        let portfolioResult = null;
        try {
            const response = await fetch('/api/portfolio-analysis');
            if (response.ok) {
                portfolioResult = await response.json();
            }
        } catch (error) {
            console.error('포트폴리오 분석 오류:', error);
        }
        
        // UI 구성
        buildFactorUI(allResults, portfolioResult);
        
    } catch (error) {
        console.error('팩터 분석 로드 오류:', error);
        document.getElementById('factors-container').innerHTML = 
            '<p style="padding: 12px; color: #e74c3c;">팩터 분석을 불러올 수 없습니다.</p>';
    }
}

// ===== 팩터 분석 UI 구성 =====
function buildFactorUI(results, portfolio) {
    const container = document.getElementById('factors-container');
    container.innerHTML = '';
    
    // 계설 섹션
    const intro = document.createElement('div');
    intro.className = 'factor-analysis-section';
    intro.innerHTML = `
        <h3>📊 Fama-French 3-Factor 모델</h3>
        <p style="font-size: 10px; line-height: 1.5; color: #555; margin-bottom: 8px;">
            <strong>모델:</strong> $R_i - R_f = α + β_{MKT}·(R_m - R_f) + β_{SMB}·SMB + β_{HML}·HML + ε$<br>
            <strong>해석:</strong>
            <ul style="margin: 4px 0 0 16px; padding: 0;">
                <li><strong>α (알파):</strong> 초과수익, 양수면 시장 초과 성과</li>
                <li><strong>β_MKT:</strong> 시장위험에 대한 민감도 (1보다 크면 높은 베타)</li>
                <li><strong>β_SMB:</strong> 규모 팩터, 소형주 선호도</li>
                <li><strong>β_HML:</strong> 가치 팩터, 가치주 선호도</li>
                <li><strong>R²:</strong> 모델의 설명력 (높을수록 좋음)</li>
            </ul>
        </p>
    `;
    container.appendChild(intro);
    
    // 개별 자산 분석
    const tickers = Object.keys(results || {});
    tickers.forEach(ticker => {
        const result = results[ticker];
        if (!result || result.error) return;
        
        const section = document.createElement('div');
        section.className = 'factor-analysis-section';
        section.innerHTML = renderFactorAnalysisHTML(ticker, result);
        container.appendChild(section);
    });
    
    // 포트폴리오 분석
    if (portfolio && !portfolio.error) {
        const section = document.createElement('div');
        section.className = 'factor-analysis-section';
        section.style.background = '#f0f8ff';
        section.style.borderLeft = '4px solid #3498db';
        section.innerHTML = renderPortfolioAnalysisHTML(portfolio);
        container.appendChild(section);
    }
}

// ===== 팩터 분석 HTML 렌더링 =====
function renderFactorAnalysisHTML(ticker, result) {
    const betas = result.betas || {};
    const pvals = result.p_values || {};
    const interpretation = result.interpretation || {};
    
    const alphaSig = pvals.alpha < 0.05 ? '★' : '·';
    const mktSig = pvals.MKT < 0.05 ? '★' : '·';
    const smbSig = pvals.SMB < 0.05 ? '★' : '·';
    const hmlSig = pvals.HML < 0.05 ? '★' : '·';
    
    return `
        <h3>${ticker} - Fama-French 분석</h3>
        <table class="factor-table">
            <tr>
                <td class="label" style="width: 25%;">계수</td>
                <td class="label" style="width: 20%;">값</td>
                <td class="label" style="width: 20%;">P-value</td>
                <td class="label" style="width: 35%;">해석</td>
            </tr>
            <tr>
                <td>α (알파)</td>
                <td class="value">${(betas.alpha || 0).toFixed(6)}</td>
                <td class="value">${(pvals.alpha || 1).toFixed(4)}</td>
                <td>${alphaSig} ${pvals.alpha < 0.05 ? '<span class="factor-significant">유의함</span>' : '<span class="factor-insignificant">유의하지 않음</span>'}</td>
            </tr>
            <tr>
                <td>β_MKT (시장위험)</td>
                <td class="value">${(betas.MKT || 0).toFixed(4)}</td>
                <td class="value">${(pvals.MKT || 1).toFixed(4)}</td>
                <td>${mktSig} ${pvals.MKT < 0.05 ? '<span class="factor-significant">시장 민감</span>' : '<span class="factor-insignificant">시장 민감하지 않음</span>'}</td>
            </tr>
            <tr>
                <td>β_SMB (규모)</td>
                <td class="value">${(betas.SMB || 0).toFixed(4)}</td>
                <td class="value">${(pvals.SMB || 1).toFixed(4)}</td>
                <td>${smbSig} ${betas.SMB > 0 ? '소형주 선호' : '대형주 선호'}</td>
            </tr>
            <tr>
                <td>β_HML (가치)</td>
                <td class="value">${(betas.HML || 0).toFixed(4)}</td>
                <td class="value">${(pvals.HML || 1).toFixed(4)}</td>
                <td>${hmlSig} ${betas.HML > 0 ? '가치주 선호' : '성장주 선호'}</td>
            </tr>
            <tr style="background: #f8f9fa; font-weight: 600;">
                <td>R² (설명력)</td>
                <td class="value">${(result.r_squared || 0).toFixed(4)}</td>
                <td class="value">Adj: ${(result.adj_r_squared || 0).toFixed(4)}</td>
                <td>${result.r_squared > 0.7 ? '우수' : result.r_squared > 0.4 ? '양호' : '약함'}</td>
            </tr>
        </table>
        <div class="factor-interpretation">
            <strong>📌 알파 해석:</strong> ${interpretation.alpha_interpretation || '-'}
        </div>
        <div class="factor-interpretation">
            <strong>📌 종합 평가:</strong> ${interpretation.overall_assessment || '-'}
        </div>
    `;
}

// ===== 포트폴리오 분석 HTML 렌더링 =====
function renderPortfolioAnalysisHTML(portfolio) {
    const betas = portfolio.betas || {};
    const pvals = portfolio.p_values || {};
    const interpretation = portfolio.interpretation || {};
    const tickers = portfolio.portfolio || [];
    const weights = portfolio.weights || [];
    
    let weightHTML = '<div style="margin: 8px 0; font-size: 10px;">';
    tickers.forEach((t, i) => {
        weightHTML += `<span style="display: inline-block; margin-right: 12px;">${t}: ${(weights[i] * 100).toFixed(1)}%</span>`;
    });
    weightHTML += '</div>';
    
    const alphaSig = pvals.alpha < 0.05 ? '★' : '·';
    const mktSig = pvals.MKT < 0.05 ? '★' : '·';
    
    return `
        <h3>🎯 포트폴리오 분석 (${tickers.join(', ')})</h3>
        ${weightHTML}
        <table class="factor-table">
            <tr>
                <td class="label" style="width: 25%;">계수</td>
                <td class="label" style="width: 20%;">값</td>
                <td class="label" style="width: 20%;">P-value</td>
                <td class="label" style="width: 35%;">해석</td>
            </tr>
            <tr>
                <td>α (포트폴리오 알파)</td>
                <td class="value">${(betas.alpha || 0).toFixed(6)}</td>
                <td class="value">${(pvals.alpha || 1).toFixed(4)}</td>
                <td>${alphaSig} ${pvals.alpha < 0.05 ? '<span class="factor-significant">유의 초과수익</span>' : '<span class="factor-insignificant">초과수익 부재</span>'}</td>
            </tr>
            <tr>
                <td>β_MKT (포트폴리오 베타)</td>
                <td class="value">${(betas.MKT || 0).toFixed(4)}</td>
                <td class="value">${(pvals.MKT || 1).toFixed(4)}</td>
                <td>${mktSig} ${betas.MKT < 1 ? '저베타' : '고베타'}</td>
            </tr>
            <tr style="background: #f8f9fa; font-weight: 600;">
                <td>R² (설명력)</td>
                <td class="value">${(portfolio.r_squared || 0).toFixed(4)}</td>
                <td class="value">Adj: ${(portfolio.adj_r_squared || 0).toFixed(4)}</td>
                <td>${portfolio.r_squared > 0.7 ? '우수' : portfolio.r_squared > 0.4 ? '양호' : '약함'}</td>
            </tr>
        </table>
        <div class="factor-interpretation">
            <strong>📌 포트폴리오 평가:</strong> ${interpretation.overall_assessment || '-'}
        </div>
    `;
}

// ===== 이벤트 리스너 =====
document.getElementById('refreshBtn').addEventListener('click', () => {
    loadData();
});

// ===== 초기 로드 =====
window.addEventListener('DOMContentLoaded', loadData);
