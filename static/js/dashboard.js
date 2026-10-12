/**
 * TaskNova — Dashboard Charts & Micro-interactions
 */

document.addEventListener('DOMContentLoaded', () => {
  initDashboardCharts();
});

function initDashboardCharts() {
  if (!window.dashboardChartsData) return;

  const data = window.dashboardChartsData;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(15, 23, 42, 0.06)';
  const textColor = isDark ? '#94a3b8' : '#64748b';

  // 1. Weekly Completion Line Chart
  const weeklyCanvas = document.getElementById('weeklyTrendChart');
  if (weeklyCanvas && data.weekly_trend) {
    new Chart(weeklyCanvas, {
      type: 'line',
      data: data.weekly_trend,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            padding: 10,
            titleFont: { size: 12, family: 'Inter' },
            bodyFont: { size: 12, family: 'Inter' },
            cornerRadius: 8
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: textColor, font: { family: 'Inter', size: 11 } }
          },
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1, color: textColor, font: { family: 'Inter', size: 11 } },
            grid: { color: gridColor }
          }
        }
      }
    });
  }

  // 2. Status Distribution Doughnut Chart
  const statusCanvas = document.getElementById('statusDoughnutChart');
  if (statusCanvas && data.status_distribution) {
    new Chart(statusCanvas, {
      type: 'doughnut',
      data: {
        labels: data.status_distribution.labels,
        datasets: [{
          data: data.status_distribution.data,
          backgroundColor: data.status_distribution.backgroundColor,
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            padding: 8,
            cornerRadius: 8
          }
        }
      }
    });
  }
}
