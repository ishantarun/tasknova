/**
 * TaskNova — Productivity Analytics Visualizations
 */

document.addEventListener('DOMContentLoaded', () => {
  initAnalyticsCharts();
});

function initAnalyticsCharts() {
  if (!window.analyticsChartsData) return;

  const data = window.analyticsChartsData;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(15, 23, 42, 0.06)';
  const textColor = isDark ? '#94a3b8' : '#64748b';

  // 1. Weekly Completion Line Chart
  const weeklyCanvas = document.getElementById('analyticsWeeklyChart');
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

  // 2. Priority Distribution Bar Chart
  const priorityCanvas = document.getElementById('analyticsPriorityChart');
  if (priorityCanvas && data.priority_distribution) {
    new Chart(priorityCanvas, {
      type: 'bar',
      data: {
        labels: data.priority_distribution.labels,
        datasets: [{
          label: 'Tasks',
          data: data.priority_distribution.data,
          backgroundColor: data.priority_distribution.backgroundColor,
          borderRadius: 8,
          barThickness: 32
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            padding: 10,
            cornerRadius: 8
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: textColor, font: { family: 'Inter', size: 12, weight: '600' } }
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
}
