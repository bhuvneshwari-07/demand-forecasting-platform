/* ==========================================================================
   AI Demand Forecasting & Inventory Intelligence Platform - Visualizations
   ========================================================================== */
// Global Chart styling configurations
const chartColors = {
    primary: '#22c55e',
    primaryGlow: 'rgba(34, 197, 94, 0.25)',
    success: '#4ade80',
    successGlow: 'rgba(74, 222, 128, 0.25)',
    warning: '#eab308',
    warningGlow: 'rgba(234, 179, 8, 0.25)',
    danger: '#ef4444',
    dangerGlow: 'rgba(239, 68, 68, 0.25)',
    info: '#06b6d4',
    infoGlow: 'rgba(6, 182, 212, 0.25)',
    gridColor: 'rgba(255, 255, 255, 0.05)',
    gridColorLight: 'rgba(0, 0, 0, 0.05)',
    textColor: '#9ca3af',
    textColorLight: '#4b5563'
};
function getGridColor() {
    return document.body.classList.contains('light-theme') ? chartColors.gridColorLight : chartColors.gridColor;
}
function getTextColor() {
    return document.body.classList.contains('light-theme') ? chartColors.textColorLight : chartColors.textColor;
}
// 1. Line Chart: Monthly Demand Trend
def_line_chart = function(canvasId, labels, historicalData, forecastedData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Create Gradients
    const gradHist = ctx.createLinearGradient(0, 0, 0, 400);
    gradHist.addColorStop(0, 'rgba(6, 182, 212, 0.4)');
    gradHist.addColorStop(1, 'rgba(6, 182, 212, 0.0)');
    
    const gradFore = ctx.createLinearGradient(0, 0, 0, 400);
    gradFore.addColorStop(0, 'rgba(16, 185, 129, 0.4)');
    gradFore.addColorStop(1, 'rgba(16, 185, 129, 0.0)');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Historical Sales',
                    data: historicalData,
                    borderColor: chartColors.info,
                    backgroundColor: gradHist,
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointBackgroundColor: chartColors.info,
                    pointHoverRadius: 6
                },
                {
                    label: 'Forecasted Demand',
                    data: forecastedData,
                    borderColor: chartColors.primary,
                    backgroundColor: gradFore,
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    borderDash: [5, 5],
                    pointBackgroundColor: chartColors.primary,
                    pointHoverRadius: 7
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: getTextColor(), font: { family: 'Plus Jakarta Sans' } }
                }
            },
            scales: {
                x: {
                    grid: { color: getGridColor() },
                    ticks: { color: getTextColor() }
                },
                y: {
                    grid: { color: getGridColor() },
                    ticks: { color: getTextColor() }
                }
            }
        }
    });
};
// 2. Bar Chart: Category-wise Distribution
def_category_chart = function(canvasId, categories, demandValues) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Forecasted Demand (Units)',
                data: demandValues,
                backgroundColor: [
                    'rgba(34, 197, 94, 0.75)',
                    'rgba(6, 182, 212, 0.75)',
                    'rgba(234, 179, 8, 0.75)',
                    'rgba(239, 68, 68, 0.75)',
                    'rgba(139, 92, 246, 0.75)'
                ],
                borderColor: [
                    chartColors.primary,
                    chartColors.info,
                    chartColors.warning,
                    chartColors.danger,
                    '#8b5cf6'
                ],
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: getGridColor() },
                    ticks: { color: getTextColor() }
                },
                y: {
                    grid: { color: getGridColor() },
                    ticks: { color: getTextColor() }
                }
            }
        }
    });
};
// 3. Doughnut Chart: Region-wise Distribution
def_region_chart = function(canvasId, regions, values) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: regions,
            datasets: [{
                data: values,
                backgroundColor: [
                    'rgba(34, 197, 94, 0.7)',
                    'rgba(6, 182, 212, 0.7)',
                    'rgba(234, 179, 8, 0.7)',
                    'rgba(239, 68, 68, 0.7)'
                ],
                borderColor: [
                    chartColors.primary,
                    chartColors.info,
                    chartColors.warning,
                    chartColors.danger
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: getTextColor(), font: { family: 'Plus Jakarta Sans' } }
                }
            },
            cutout: '65%'
        }
    });
};
// 4. Bar Chart: Promotion Impact comparison
def_promo_chart = function(canvasId, promoAvg, noPromoAvg) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Promotion Active', 'No Promotion'],
            datasets: [{
                label: 'Avg Demand (Units)',
                data: [promoAvg, noPromoAvg],
                backgroundColor: [chartColors.successGlow, 'rgba(255, 255, 255, 0.05)'],
                borderColor: [chartColors.success, chartColors.textColor],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: getGridColor() }, ticks: { color: getTextColor() } },
                y: { grid: { color: getGridColor() }, ticks: { color: getTextColor() } }
            }
        }
    });
};
// 5. Radar Chart: Seasonality patterns
def_season_chart = function(canvasId, seasons, values) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: seasons,
            datasets: [{
                label: 'Seasonality Index',
                data: values,
                backgroundColor: 'rgba(6, 182, 212, 0.15)',
                borderColor: chartColors.info,
                pointBackgroundColor: chartColors.info,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                r: {
                    grid: { color: getGridColor() },
                    angleLines: { color: getGridColor() },
                    pointLabels: { color: getTextColor(), font: { family: 'Plus Jakarta Sans' } },
                    ticks: { display: false }
                }
            }
        }
    });
};
// 6. Horizontal Bar: Feature Importance / Explainable AI (SHAP)
def_shap_chart = function(canvasId, features, values) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: features,
            datasets: [{
                label: 'Relative Contribution Score',
                data: values,
                backgroundColor: 'rgba(34, 197, 94, 0.35)',
                borderColor: chartColors.primary,
                borderWidth: 2,
                borderRadius: 5
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: getGridColor() }, ticks: { color: getTextColor() } },
                y: { grid: { color: getGridColor() }, ticks: { color: getTextColor() } }
            }
        }
    });
};
// 7. Radar/Bar: Model comparison MAE / RMSE
def_model_comparison_chart = function(canvasId, models, maeValues, rmseValues) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: models,
            datasets: [
                {
                    label: 'MAE (Mean Absolute Error)',
                    data: maeValues,
                    backgroundColor: 'rgba(6, 182, 212, 0.65)',
                    borderColor: chartColors.info,
                    borderWidth: 1,
                    borderRadius: 6
                },
                {
                    label: 'RMSE (Root Mean Squared Error)',
                    data: rmseValues,
                    backgroundColor: 'rgba(239, 68, 68, 0.65)',
                    borderColor: chartColors.danger,
                    borderWidth: 1,
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { grid: { color: getGridColor() }, ticks: { color: getTextColor() } },
                y: { grid: { color: getGridColor() }, ticks: { color: getTextColor() } }
            }
        }
    });
};
