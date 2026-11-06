'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const menuToggle = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('sidebar');
  const shade = document.getElementById('sidebar-shade');
  const closeMenu = () => {
    sidebar?.classList.remove('is-open');
    menuToggle?.setAttribute('aria-expanded', 'false');
    if (shade) shade.hidden = true;
  };
  menuToggle?.addEventListener('click', () => {
    const open = menuToggle.getAttribute('aria-expanded') !== 'true';
    menuToggle.setAttribute('aria-expanded', String(open));
    sidebar?.classList.toggle('is-open', open);
    if (shade) shade.hidden = !open;
  });
  shade?.addEventListener('click', closeMenu);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
  document.querySelectorAll('.dismiss-flash').forEach((button) => {
    button.addEventListener('click', () => button.closest('.flash')?.remove());
  });

  const querySearch = document.getElementById('query-search');
  querySearch?.addEventListener('input', () => {
    const term = querySearch.value.toLocaleLowerCase().trim();
    let visible = 0;
    document.querySelectorAll('[data-query-search]').forEach((item) => {
      item.hidden = !item.dataset.querySearch.toLocaleLowerCase().includes(term);
      if (!item.hidden) visible += 1;
    });
    const empty = document.getElementById('query-search-empty');
    if (empty) empty.hidden = visible !== 0;
  });
  const copyButton = document.getElementById('copy-query');
  copyButton?.addEventListener('click', async () => {
    const code = document.getElementById('selected-sql');
    try {
      await navigator.clipboard.writeText(code.textContent);
      copyButton.textContent = 'Copied';
      window.setTimeout(() => { copyButton.textContent = 'Copy SQL'; }, 1800);
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(code);
      selection.removeAllRanges();
      selection.addRange(range);
      copyButton.textContent = 'SQL selected — press Ctrl+C';
    }
  });

  const chartIds = ['status-chart', 'field-chart', 'year-chart'];
  if (!document.getElementById('status-chart')) return;
  const fallback = document.getElementById('chart-fallback');
  const chartBodies = document.querySelectorAll('.chart-body');
  const chartTables = document.querySelectorAll('.chart-data');
  const showFallback = (message) => {
    fallback.hidden = false;
    fallback.textContent = message;
    chartTables.forEach((detail) => { detail.open = true; });
    chartBodies.forEach((body) => { body.hidden = true; });
  };
  showFallback('Interactive charts are loading. The complete chart data is available in the tables above.');

  const initializeCharts = () => {
    if (typeof window.Chart === 'undefined') return;
    const Chart = window.Chart;
    chartBodies.forEach((body) => { body.hidden = false; });
    Chart.defaults.color = '#9caac5';
    Chart.defaults.font.family = 'Segoe UI, system-ui, sans-serif';
    Chart.defaults.font.size = 11;
    const grid = 'rgba(148, 163, 184, 0.08)';
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      animation: reducedMotion ? false : { duration: 450 },
      plugins: { legend: { display: false }, tooltip: { backgroundColor: '#202940', titleColor: '#f5f7ff', bodyColor: '#c1cbe0', padding: 12, cornerRadius: 7 } },
    };
    chartIds.forEach((id) => {
      const data = JSON.parse(document.getElementById(`${id}-data`).textContent);
      const canvas = document.getElementById(id);
      if (id === 'status-chart') {
        new Chart(canvas, {
          type: 'doughnut',
          data: {
            labels: data.labels,
            datasets: [{
              data: data.values,
              backgroundColor: data.labels.map((label) => label === 'Solved' ? '#53d6d4' : '#a18aff'),
              borderColor: '#141c2e',
              borderWidth: 5,
              hoverOffset: 4,
            }],
          },
          options: {
            ...baseOptions,
            cutout: '78%',
            layout: { padding: 10 },
          },
        });
      } else if (id === 'field-chart') {
        new Chart(canvas, {
          type: 'bar',
          data: {
            labels: data.labels,
            datasets: [{
              data: data.values,
              backgroundColor: ['#a18aff', '#7d89e9', '#53d6d4', '#6abacb', '#b2a2f2', '#4c9fbc', '#9b9bd6'],
              borderRadius: 4,
              barThickness: 13,
            }],
          },
          options: {
            ...baseOptions,
            indexAxis: 'y',
            scales: {
              x: {
                beginAtZero: true,
                ticks: { precision: 0 },
                grid: { color: grid },
                border: { display: false },
              },
              y: {
                grid: { display: false },
                border: { display: false },
                ticks: { font: { size: 10 } },
              },
            },
          },
        });
      } else {
        new Chart(canvas, {
          type: 'line',
          data: {
            labels: data.labels,
            datasets: [{
              data: data.values,
              borderColor: '#a18aff',
              backgroundColor: 'rgba(161, 138, 255, 0.10)',
              fill: true,
              tension: 0.25,
              borderWidth: 2,
              pointBackgroundColor: '#a18aff',
              pointBorderColor: '#141c2e',
              pointBorderWidth: 2,
              pointRadius: 4,
            }],
          },
          options: {
            ...baseOptions,
            scales: {
              x: {
                grid: { display: false },
                border: { display: false },
                ticks: { maxTicksLimit: 8 },
              },
              y: {
                beginAtZero: true,
                ticks: { precision: 0 },
                grid: { color: grid },
                border: { display: false },
              },
            },
          },
        });
      }
    });
    fallback.hidden = true;
    chartTables.forEach((detail) => { detail.open = false; });
  };
  const loadCharts = () => {
    try {
      initializeCharts();
    } catch {
      chartIds.forEach((id) => window.Chart?.getChart?.(id)?.destroy());
      showFallback('Charts could not be displayed. All chart data remains available in the tables above.');
    }
  };
  if (typeof window.Chart !== 'undefined') {
    loadCharts();
    return;
  }
  // An asynchronous CDN request never blocks menus, forms, or the data tables.
  const script = document.createElement('script');
  script.id = 'chartjs-cdn';
  script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.8/dist/chart.umd.min.js';
  script.async = true;
  const timeout = window.setTimeout(() => {
    showFallback('Charts are taking longer to load. You can read all chart data in the tables above; an internet connection is required for Chart.js.');
  }, 6000);
  script.addEventListener('load', () => {
    window.clearTimeout(timeout);
    loadCharts();
  });
  script.addEventListener('error', () => {
    window.clearTimeout(timeout);
    showFallback('Chart.js could not load. All chart data remains available in the tables above.');
  });
  document.head.appendChild(script);
});
