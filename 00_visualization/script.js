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
        const response = await fetch('/api/data');
        if (!response.ok) {
            throw new Error('API 호출 실패');
        }
        chartData = await response.json();
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
            <h2>${ticker}</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-label">평균</span>
                    <span class="stat-value stat-mean" data-ticker="${ticker}">-</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">변동성</span>
                    <span class="stat-value stat-std" data-ticker="${ticker}">-</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">최소</span>
                    <span class="stat-value stat-min" data-ticker="${ticker}">-</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">최대</span>
                    <span class="stat-value stat-max" data-ticker="${ticker}">-</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">왜도</span>
                    <span class="stat-value stat-skew" data-ticker="${ticker}">-</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">첨도</span>
                    <span class="stat-value stat-kurt" data-ticker="${ticker}">-</span>
                </div>
            </div>
            <div class="charts-row">
                <div class="chart-item">
                    <div class="chart-title">가격</div>
                    <div id="priceChart-${ticker}" class="chart"></div>
                </div>
                <div class="chart-item">
                    <div class="chart-title">분포</div>
                    <div id="histogramChart-${ticker}" class="chart"></div>
                </div>
                <div class="chart-item">
                    <div class="chart-title">Q-Q</div>
                    <div id="qqChart-${ticker}" class="chart"></div>
                </div>
                <div class="chart-item">
                    <div class="chart-title">ACF</div>
                    <div id="acfChart-${ticker}" class="chart"></div>
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
        line: { color, width: 1 },
        fill: 'tozeroy',
        fillcolor: color + '20'
    };

    const layout = {
        margin: { l: 30, r: 10, t: 5, b: 30 },
        hovermode: 'x unified',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif', size: 9 },
        xaxis: { showgrid: true, gridwidth: 0.5, gridcolor: '#ecf0f1' },
        yaxis: { showgrid: true, gridwidth: 0.5, gridcolor: '#ecf0f1' }
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
            line: { color, width: 0.5 }
        }
    };

    const layout = {
        margin: { l: 30, r: 10, t: 5, b: 30 },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif', size: 9 },
        xaxis: { showgrid: true, gridwidth: 0.5, gridcolor: '#ecf0f1' },
        yaxis: { showgrid: true, gridwidth: 0.5, gridcolor: '#ecf0f1' }
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
        marker: { color, size: 4, opacity: 0.7 }
    };

    const minVal = Math.min(...qqData.theoretical);
    const maxVal = Math.max(...qqData.theoretical);
    const reference = {
        x: [minVal, maxVal],
        y: [minVal, maxVal],
        mode: 'lines',
        name: '',
        line: { color: '#bdc3c7', width: 1, dash: 'dash' }
    };

    const yMin = Math.min(...qqData.sample);
    const yMax = Math.max(...qqData.sample);
    const yRange = yMax - yMin;
    const yPadding = yRange * 0.1;

    const layout = {
        margin: { l: 30, r: 10, t: 5, b: 30 },
        hovermode: 'closest',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif', size: 9 },
        showlegend: false,
        xaxis: { showgrid: true, gridwidth: 0.5, gridcolor: '#ecf0f1' },
        yaxis: { showgrid: true, gridwidth: 0.5, gridcolor: '#ecf0f1', range: [yMin - yPadding, yMax + yPadding] }
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
        marker: { color, opacity: 0.75, line: { color, width: 0.5 } }
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
        margin: { l: 30, r: 10, t: 5, b: 30 },
        hovermode: 'x unified',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif', size: 9 },
        xaxis: { showgrid: true, gridwidth: 0.5, gridcolor: '#ecf0f1' },
        yaxis: { showgrid: true, gridwidth: 0.5, gridcolor: '#ecf0f1' }
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
