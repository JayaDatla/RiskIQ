// API Configuration
// For HF Spaces, the API will be served from the same domain with /api prefix
const API_BASE_URL = window.location.origin + '/api';

// Global variables
let priceChart = null;
let portfolioChart = null;

// DOM Elements
const elements = {
    // Tabs
    singleTab: document.getElementById('single-tab'),
    portfolioTab: document.getElementById('portfolio-tab'),
    tabBtns: document.querySelectorAll('.tab-btn'),

    // Single stock elements
    tickerInput: document.getElementById('ticker-input'),
    analyzeBtn: document.getElementById('analyze-btn'),
    singleLoading: document.getElementById('single-loading'),
    singleResults: document.getElementById('single-results'),
    riskBadge: document.getElementById('risk-badge'),
    histVol: document.getElementById('hist-vol'),
    var95: document.getElementById('var-95'),
    cvar95: document.getElementById('cvar-95'),
    garchForecast: document.getElementById('garch-forecast'),
    xgboostForecast: document.getElementById('xgboost-forecast'),
    lstmForecast: document.getElementById('lstm-forecast'),
    priceChartCanvas: document.getElementById('price-chart'),
    aiSummary: document.getElementById('ai-summary'),

    // Portfolio elements
    tickersInput: document.getElementById('tickers-input'),
    analyzePortfolioBtn: document.getElementById('analyze-portfolio-btn'),
    portfolioLoading: document.getElementById('portfolio-loading'),
    portfolioResults: document.getElementById('portfolio-results'),
    portfolioRiskBadge: document.getElementById('portfolio-risk-badge'),
    portfolioCount: document.getElementById('portfolio-count'),
    avgVolatility: document.getElementById('avg-volatility'),
    avgVar: document.getElementById('avg-var'),
    avgCvar: document.getElementById('avg-cvar'),
    stocksGrid: document.getElementById('stocks-grid'),
    portfolioChartCanvas: document.getElementById('portfolio-chart'),
    portfolioAiSummary: document.getElementById('portfolio-ai-summary'),

    // Modal
    errorModal: document.getElementById('error-modal'),
    errorMessage: document.getElementById('error-message'),
    closeModal: document.querySelector('.close')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function () {
    initializeEventListeners();
    setupTabSwitching();
});

// Event Listeners
function initializeEventListeners() {
    // Single stock analysis
    elements.analyzeBtn.addEventListener('click', analyzeSingleStock);
    elements.tickerInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            analyzeSingleStock();
        }
    });

    // Portfolio analysis
    elements.analyzePortfolioBtn.addEventListener('click', analyzePortfolio);
    elements.tickersInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            analyzePortfolio();
        }
    });

    // Modal close
    elements.closeModal.addEventListener('click', closeErrorModal);
    window.addEventListener('click', function (e) {
        if (e.target === elements.errorModal) {
            closeErrorModal();
        }
    });
}

// Tab Switching
function setupTabSwitching() {
    elements.tabBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update tab buttons
    elements.tabBtns.forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Clear previous results
    clearResults();
}

// Single Stock Analysis
async function analyzeSingleStock() {
    const ticker = elements.tickerInput.value.trim().toUpperCase();

    if (!ticker) {
        showError('Please enter a stock ticker symbol');
        return;
    }

    showLoading('single');

    try {
        const response = await fetch(`${API_BASE_URL}/risk/${ticker}`);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displaySingleStockResults(data);

    } catch (error) {
        console.error('Error analyzing stock:', error);
        showError(`Failed to analyze ${ticker}: ${error.message}`);
    } finally {
        hideLoading('single');
    }
}

function displaySingleStockResults(data) {
    // Show results section
    elements.singleResults.style.display = 'block';

    // Update risk level
    updateRiskBadge(elements.riskBadge, data.risk_level);

    // Update metrics
    elements.histVol.textContent = formatPercentage(data.details[0].historical_volatility);
    elements.var95.textContent = formatPercentage(Math.abs(data.details[0].VaR_95));
    elements.cvar95.textContent = formatPercentage(Math.abs(data.details[0].CVaR_95));

    // Update forecasts
    elements.garchForecast.textContent = formatPercentage(data.details[0].forecasted_volatility_garch);
    elements.xgboostForecast.textContent = formatPercentage(data.details[0].forecasted_volatility_xgboost);
    elements.lstmForecast.textContent = formatPercentage(data.details[0].forecasted_volatility_lstm);

    // Create price chart with currency
    const currency = data.details[0].currency || 'USD';
    createPriceChart(data.details[0].historical_data, currency);

    // Update AI summary
    elements.aiSummary.textContent = data.summary;
}

// Portfolio Analysis
async function analyzePortfolio() {
    const tickersText = elements.tickersInput.value.trim();

    if (!tickersText) {
        showError('Please enter stock ticker symbols');
        return;
    }

    const tickers = tickersText.split(',').map(t => t.trim().toUpperCase()).filter(t => t);

    if (tickers.length === 0) {
        showError('Please enter valid stock ticker symbols');
        return;
    }

    if (tickers.length > 10) {
        showError('Please limit to 10 stocks maximum for portfolio analysis');
        return;
    }

    showLoading('portfolio');

    try {
        const response = await fetch(`${API_BASE_URL}/portfolio_risk`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tickers)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayPortfolioResults(data);

    } catch (error) {
        console.error('Error analyzing portfolio:', error);
        showError(`Failed to analyze portfolio: ${error.message}`);
    } finally {
        hideLoading('portfolio');
    }
}

function displayPortfolioResults(data) {
    // Show results section
    elements.portfolioResults.style.display = 'block';

    // Update portfolio risk level
    updateRiskBadge(elements.portfolioRiskBadge, data.risk_level);

    // Update portfolio summary
    const validStocks = data.details.filter(stock => !stock.error);
    elements.portfolioCount.textContent = validStocks.length;
    elements.avgVolatility.textContent = formatPercentage(data.portfolio_summary.average_volatility);
    elements.avgVar.textContent = formatPercentage(Math.abs(data.portfolio_summary.average_VaR_95));
    elements.avgCvar.textContent = formatPercentage(Math.abs(data.portfolio_summary.average_CVaR_95));

    // Display individual stocks
    displayIndividualStocks(validStocks);

    // Create portfolio chart
    createPortfolioChart(validStocks);

    // Update AI summary
    elements.portfolioAiSummary.textContent = data.summary;
}

function displayIndividualStocks(stocks) {
    elements.stocksGrid.innerHTML = '';

    stocks.forEach(stock => {
        const stockCard = document.createElement('div');
        stockCard.className = 'stock-card';

        const riskLevel = getRiskLevelFromVolatility(stock.historical_volatility);

        stockCard.innerHTML = `
            <div class="stock-header">
                <div class="stock-ticker">${stock.ticker}</div>
                <div class="stock-risk ${riskLevel.toLowerCase().replace('-', '-')}">${riskLevel}</div>
            </div>
            <div class="stock-metrics">
                <div class="stock-metric">
                    <div class="stock-metric-label">Volatility</div>
                    <div class="stock-metric-value">${formatPercentage(stock.historical_volatility)}</div>
                </div>
                <div class="stock-metric">
                    <div class="stock-metric-label">VaR (95%)</div>
                    <div class="stock-metric-value">${formatPercentage(Math.abs(stock.VaR_95))}</div>
                </div>
                <div class="stock-metric">
                    <div class="stock-metric-label">CVaR (95%)</div>
                    <div class="stock-metric-value">${formatPercentage(Math.abs(stock.CVaR_95))}</div>
                </div>
                <div class="stock-metric">
                    <div class="stock-metric-label">GARCH Forecast</div>
                    <div class="stock-metric-value">${formatPercentage(stock.forecasted_volatility_garch)}</div>
                </div>
            </div>
        `;

        elements.stocksGrid.appendChild(stockCard);
    });
}

// Chart Functions
function createPriceChart(historicalData, currency) {
    if (priceChart) {
        priceChart.destroy();
    }

    const ctx = elements.priceChartCanvas.getContext('2d');

    const labels = historicalData.map(d => d.Date);
    const prices = historicalData.map(d => d.Close);
    const returns = historicalData.map(d => d.Return);

    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Price',
                data: prices,
                borderColor: '#22c55e',
                backgroundColor: 'rgba(34, 197, 94, 0.08)',
                tension: 0.4,
                yAxisID: 'y'
            }, {
                label: 'Returns',
                data: returns,
                borderColor: '#7c3aed',
                backgroundColor: 'rgba(124, 58, 237, 0.08)',
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2, // wider than tall to avoid vertical stretch
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: `Price (${currency})`
                    },
                    ticks: {
                        color: '#9ca3af'
                    },
                    grid: {
                        color: 'rgba(124,58,237,0.15)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Returns'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: 'rgba(124,58,237,0.15)'
                    },
                    suggestedMin: -0.08,
                    suggestedMax: 0.08,
                    ticks: {
                        callback: function (value) { return (value * 100).toFixed(1) + '%'; },
                        color: '#9ca3af'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: { color: '#d1d5db' }
                }
            }
        }
    });
}

function createPortfolioChart(stocks) {
    if (portfolioChart) {
        portfolioChart.destroy();
    }

    const ctx = elements.portfolioChartCanvas.getContext('2d');

    const labels = stocks.map(s => s.ticker);
    const volatilities = stocks.map(s => s.historical_volatility);
    const colors = stocks.map(() => 'rgba(34,197,94,0.6)');

    portfolioChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Historical Volatility',
                data: volatilities,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.7', '1')),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Volatility'
                    },
                    ticks: {
                        callback: function (value) {
                            return formatPercentage(value);
                        },
                        color: '#9ca3af'
                    },
                    grid: { color: 'rgba(124,58,237,0.15)' }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Stock Ticker'
                    },
                    ticks: { color: '#9ca3af' },
                    grid: { color: 'rgba(124,58,237,0.15)' }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${formatPercentage(context.parsed.y)}`;
                        }
                    },
                    backgroundColor: 'rgba(17,24,39,0.95)',
                    titleColor: '#e5e7eb',
                    bodyColor: '#d1d5db',
                    borderColor: 'rgba(124,58,237,0.3)',
                    borderWidth: 1
                }
            }
        }
    });
}

// Utility Functions
function updateRiskBadge(element, riskLevel) {
    element.textContent = riskLevel;
    element.className = 'risk-badge ' + riskLevel.toLowerCase().replace('_', '-');
}

function getRiskLevelFromVolatility(volatility) {
    if (volatility > 0.5) return 'HIGH';
    if (volatility > 0.4) return 'MODERATE-HIGH';
    if (volatility > 0.3) return 'MODERATE';
    if (volatility > 0.2) return 'LOW-MODERATE';
    return 'LOW';
}

function formatPercentage(value) {
    if (value === null || value === undefined || isNaN(value)) return 'N/A';
    return (value * 100).toFixed(2) + '%';
}

function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        const hue = (i * 360 / count) % 360;
        colors.push(`hsla(${hue}, 70%, 60%, 0.7)`);
    }
    return colors;
}

function showLoading(type) {
    if (type === 'single') {
        elements.singleLoading.style.display = 'block';
        elements.singleResults.style.display = 'none';
    } else if (type === 'portfolio') {
        elements.portfolioLoading.style.display = 'block';
        elements.portfolioResults.style.display = 'none';
    }
}

function hideLoading(type) {
    if (type === 'single') {
        elements.singleLoading.style.display = 'none';
    } else if (type === 'portfolio') {
        elements.portfolioLoading.style.display = 'none';
    }
}

function clearResults() {
    // Clear single stock results
    elements.singleResults.style.display = 'none';
    elements.tickerInput.value = '';

    // Clear portfolio results
    elements.portfolioResults.style.display = 'none';
    elements.tickersInput.value = '';

    // Destroy charts
    if (priceChart) {
        priceChart.destroy();
        priceChart = null;
    }
    if (portfolioChart) {
        portfolioChart.destroy();
        portfolioChart = null;
    }
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorModal.style.display = 'block';
}

function closeErrorModal() {
    elements.errorModal.style.display = 'none';
}

// Export functions for potential external use
window.RiskIQ = {
    analyzeSingleStock,
    analyzePortfolio,
    switchTab,
    clearResults
};
