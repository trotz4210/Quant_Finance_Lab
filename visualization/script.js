let chartData = null;
let currentTicker = 'AAPL';

const TICKER_COLORS = {
    'AAPL': '#555555',
    'MSFT': '#3498db',
    'TSLA': '#e74c3c',
    'SPY': '#27ae60'
};

// ===== 데이터 로드 =====
async function loadData() {
    try {
        const response = await fetch('data.json');
        if (!response.ok) {
            throw new Error('data.json을 찾을 수 없습니다. generate_data.py를 실행하세요.');
        }
        chartData = await response.json();
        renderAll();
        return true;
    } catch (error) {
        console.error('Error:', error);
        alert('데이터 로드 실패: ' + error.message);
        return false;
    }
}

// ===== 통계 업데이트 =====
function updateStats(ticker) {
    if (!chartData || !chartData.tickers[ticker]) return;

    const stats = chartData.tickers[ticker].statistics;
    document.getElementById('stat-mean').textContent = (stats.mean * 100).toFixed(2) + '%';
    document.getElementById('stat-std').textContent = (stats.std * 100).toFixed(2) + '%';
    document.getElementById('stat-min').textContent = (stats.min * 100).toFixed(2) + '%';
    document.getElementById('stat-max').textContent = (stats.max * 100).toFixed(2) + '%';
    document.getElementById('stat-skew').textContent = stats.skewness.toFixed(3);
    document.getElementById('stat-kurt').textContent = stats.kurtosis.toFixed(3);
}

// ===== 차트 렌더링 =====
function renderPriceChart(ticker) {
    if (!chartData || !chartData.tickers[ticker]) return;
    
    const data = chartData.tickers[ticker].price_history;
    const trace = {
        x: data.dates,
        y: data.prices,
        type: 'scatter',
        mode: 'lines',
        name: ticker,
        line: {
            color: TICKER_COLORS[ticker],
            width: 2.5
        },
        fill: 'tozeroy',
        fillcolor: TICKER_COLORS[ticker] + '20'
    };

    const layout = {
        margin: { l: 50, r: 30, t: 30, b: 50 },
        hovermode: 'x unified',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif' },
        xaxis: {
            title: '날짜',
            showgrid: true,
            gridwidth: 1,
            gridcolor: '#ecf0f1'
        },
        yaxis: {
            title: '가격 (USD)',
            showgrid: true,
            gridwidth: 1,
            gridcolor: '#ecf0f1'
        }
    };

    Plotly.newPlot('priceChart', [trace], layout, { responsive: true, displayModeBar: false });
}

function renderHistogram(ticker) {
    if (!chartData || !chartData.tickers[ticker]) return;

    const hist = chartData.tickers[ticker].histogram;
    const trace = {
        x: hist.bin_labels.map((_, i) => (i / hist.bin_labels.length).toFixed(4)),
        y: hist.counts,
        type: 'bar',
        marker: {
            color: TICKER_COLORS[ticker],
            opacity: 0.75,
            line: { color: TICKER_COLORS[ticker], width: 0.5 }
        }
    };

    const layout = {
        margin: { l: 50, r: 30, t: 30, b: 50 },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif' },
        xaxis: {
            title: '수익률',
            showgrid: true,
            gridwidth: 1,
            gridcolor: '#ecf0f1'
        },
        yaxis: {
            title: '빈도',
            showgrid: true,
            gridwidth: 1,
            gridcolor: '#ecf0f1'
        }
    };

    Plotly.newPlot('histogramChart', [trace], layout, { responsive: true, displayModeBar: false });
}

function renderQQPlot(ticker) {
    if (!chartData || !chartData.tickers[ticker]) return;

    const qqData = chartData.tickers[ticker].qq_plot;
    
    // 샘플 데이터
    const sample = {
        x: qqData.theoretical,
        y: qqData.sample,
        mode: 'markers',
        name: '',
        marker: {
            color: TICKER_COLORS[ticker],
            size: 5,
            opacity: 0.7
        }
    };

    // 참조선 (y = x)
    const minVal = Math.min(...qqData.theoretical);
    const maxVal = Math.max(...qqData.theoretical);
    const reference = {
        x: [minVal, maxVal],
        y: [minVal, maxVal],
        mode: 'lines',
        name: '이상적 직선',
        line: {
            color: '#bdc3c7',
            width: 2,
            dash: 'dash'
        }
    };

    const layout = {
        margin: { l: 50, r: 30, t: 30, b: 50 },
        hovermode: 'closest',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif' },
        showlegend: false,
        xaxis: {
            title: '이론적 분위수',
            showgrid: true,
            gridwidth: 1,
            gridcolor: '#ecf0f1'
        },
        yaxis: {
            title: '표본 분위수',
            showgrid: true,
            gridwidth: 1,
            gridcolor: '#ecf0f1'
        }
    };

    Plotly.newPlot('qqChart', [sample, reference], layout, { responsive: true, displayModeBar: false });
}

function renderACFPlot(ticker) {
    if (!chartData || !chartData.tickers[ticker]) return;

    const acf = chartData.tickers[ticker].acf;
    const lags = Array.from({ length: acf.length }, (_, i) => i);

    const trace = {
        x: lags,
        y: acf,
        type: 'bar',
        marker: {
            color: TICKER_COLORS[ticker],
            opacity: 0.75,
            line: { color: TICKER_COLORS[ticker], width: 0.5 }
        }
    };

    // 신뢰도 구간 (95%)
    const confidenceInterval = 1.96 / Math.sqrt(1000);
    const upperBound = {
        x: [0, Math.max(...lags)],
        y: [confidenceInterval, confidenceInterval],
        mode: 'lines',
        name: '95% CI',
        line: { color: '#bdc3c7', width: 1.5, dash: 'dash' }
    };

    const lowerBound = {
        x: [0, Math.max(...lags)],
        y: [-confidenceInterval, -confidenceInterval],
        mode: 'lines',
        line: { color: '#bdc3c7', width: 1.5, dash: 'dash' },
        showlegend: false
    };

    const layout = {
        margin: { l: 50, r: 30, t: 30, b: 50 },
        hovermode: 'x unified',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif' },
        xaxis: {
            title: '지연 (Lags)',
            showgrid: true,
            gridwidth: 1,
            gridcolor: '#ecf0f1'
        },
        yaxis: {
            title: 'ACF',
            showgrid: true,
            gridwidth: 1,
            gridcolor: '#ecf0f1'
        }
    };

    Plotly.newPlot('acfChart', [trace, upperBound, lowerBound], layout, { responsive: true, displayModeBar: false });
}

// ===== 모든 차트 렌더링 =====
function renderAll() {
    if (!chartData) return;

    // 차트 렌더링
    renderPriceChart(currentTicker);
    renderHistogram(currentTicker);
    renderQQPlot(currentTicker);
    renderACFPlot(currentTicker);
    
    // 통계 업데이트
    updateStats(currentTicker);

    // 타이머 업데이트
    const updateTime = new Date(chartData.timestamp).toLocaleString('ko-KR');
    document.getElementById('updateTime').textContent = updateTime;
}

// ===== 이벤트 리스너 =====
document.querySelectorAll('.ticker-card').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.ticker-card').forEach(b => b.classList.remove('active'));
        e.target.closest('.ticker-card').classList.add('active');
        currentTicker = e.target.closest('.ticker-card').dataset.ticker;
        renderAll();
    });
});

document.getElementById('refreshBtn').addEventListener('click', () => {
    loadData();
});

// ===== 초기 로드 =====
window.addEventListener('DOMContentLoaded', loadData);
