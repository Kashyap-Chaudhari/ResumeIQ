/* ResumeIQ Chart.js Dashboard Visualizations - Luxury Warm Theme */

function getChartGridColor() {
  const theme = document.documentElement.getAttribute('data-theme') || 'dark';
  return theme === 'light' ? '#ECE5DD' : 'rgba(255, 255, 255, 0.08)';
}

function getChartTextColor() {
  const theme = document.documentElement.getAttribute('data-theme') || 'dark';
  return theme === 'light' ? '#8C7565' : '#C5A98B';
}

function renderATSChart(canvasId, atsHistory) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const labels = atsHistory.map(item => item.date);
  const data = atsHistory.map(item => item.score);

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels.length ? labels : ['V1', 'V2', 'V3', 'V4'],
      datasets: [{
        label: 'ATS Resume Score',
        data: data.length ? data : [65, 72, 80, 88],
        borderColor: '#D39858',
        backgroundColor: 'rgba(211, 152, 88, 0.15)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#EACEAA',
        pointRadius: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          grid: { color: getChartGridColor() },
          ticks: { color: getChartTextColor() }
        },
        x: {
          grid: { color: getChartGridColor() },
          ticks: { color: getChartTextColor() }
        }
      }
    }
  });
}

function renderReadinessRadarChart(canvasId, domainScores) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const scores = domainScores || {
    technical: 70,
    problem_solving: 65,
    experience: 60,
    resume_quality: 75,
    interview_prep: 55
  };

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Technical Stack', 'Problem Solving', 'Match Relevance', 'Resume ATS', 'Interview Prep'],
      datasets: [{
        label: 'Domain Skill Score',
        data: [
          scores.technical || 65,
          scores.problem_solving || 60,
          scores.experience || 70,
          scores.resume_quality || 75,
          scores.interview_prep || 55
        ],
        backgroundColor: 'rgba(211, 152, 88, 0.25)',
        borderColor: '#D39858',
        pointBackgroundColor: '#EACEAA',
        pointBorderColor: '#34150F',
        pointHoverBackgroundColor: '#FFF7ED',
        pointHoverBorderColor: '#D39858'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          angleLines: { color: getChartGridColor() },
          grid: { color: getChartGridColor() },
          pointLabels: {
            color: getChartTextColor(),
            font: { size: 12, weight: '600' }
          },
          ticks: { display: false }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function renderPipelineDonutChart(canvasId, statusCounts) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const counts = statusCounts || { SAVED: 2, APPLIED: 5, INTERVIEWING: 2, OFFER: 1, REJECTED: 1 };

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Saved', 'Applied', 'Interviewing', 'Offer', 'Rejected'],
      datasets: [{
        data: [
          counts.SAVED || 0,
          counts.APPLIED || 0,
          counts.INTERVIEWING || 0,
          counts.OFFER || 0,
          counts.REJECTED || 0
        ],
        backgroundColor: ['#8C7565', '#D39858', '#EACEAA', '#85431E', '#A56532'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: getChartTextColor(), padding: 15 }
        }
      }
    }
  });
}
