let chartData = null;

const TICKER_COLORS = {
    'AAPL': '#555555',
    'MSFT': '#3498db',
    'TSLA': '#e74c3c',
    'SPY': '#27ae60'
};

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
        buildUI();
        renderAll();
        return true;
    } catch (error) {
        console.error('Error:', error);
        alert('데이터 로드 실패: ' + error.message);
        return false;
    }
}

// ===== 동적 UI 구성 =====
function buildUI() {
    if (!chartData || !chartData.tickers) return;

    const container = document.getElementById('container');
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
function renderAll() {
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

// ===== 이벤트 리스너 =====
document.getElementById('refreshBtn').addEventListener('click', () => {
    loadData();
});

// ===== 초기 로드 =====
window.addEventListener('DOMContentLoaded', loadData);
