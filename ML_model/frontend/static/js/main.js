// static/js/main.js
document.addEventListener("DOMContentLoaded", function () {
  const apiUrl = "/api/predictions";
  const downloadUrl = "/api/predictions/download";
  const refreshBtn = document.getElementById("refreshBtn");
  const exportBtn = document.getElementById("exportBtn");
  const searchInput = document.getElementById("searchInput");
  const categoryFilter = document.getElementById("categoryFilter");
  const chartView = document.getElementById("chartView");
  const tableView = document.getElementById("tableView");
  const toggleButtons = document.querySelectorAll(".toggle");
  const predTableBody = document.querySelector("#predTable tbody");
  const totalForecastEl = document.getElementById("totalForecast");
  const numCategoriesEl = document.getElementById("numCategories");
  const topCategoryEl = document.getElementById("topCategory");

  let rawPredictions = [];
  let barChart = null;

  async function fetchData() {
    showLoading(refreshBtn, true);
    try {
      const resp = await fetch(apiUrl);
      const data = await resp.json();
      rawPredictions = data.predictions || [];
      const summary = data.category_summary || [];
      populateCategoryFilter(summary);
      renderSummary(summary);
      renderTable(rawPredictions);
      renderChart(summary);
    } catch (err) {
      console.error("Load error", err);
    } finally {
      showLoading(refreshBtn, false);
    }
  }

  // Loading spinner toggle
  function showLoading(btn, flag) {
    if (flag) {
      btn.disabled = true;
      btn.innerHTML = '<i data-feather="loader"></i> Loading';
      feather.replace();
    } else {
      btn.disabled = false;
      btn.innerHTML = '<i data-feather="refresh-cw"></i> Refresh';
      feather.replace();
    }
  }

  function populateCategoryFilter(summaryRows) {
    categoryFilter.innerHTML = '<option value="">All categories</option>';
    summaryRows.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s.category;
      opt.innerText = s.category;
      categoryFilter.appendChild(opt);
    });
  }

  // animate counter
  function animateCount(el, value) {
    const start = 0;
    const end = Number(value);
    const duration = 900;
    const stepTime = Math.max(10, Math.floor(duration / Math.abs(end - start || 1)));
    let current = start;
    const inc = Math.ceil(end / (duration / stepTime));
    const timer = setInterval(() => {
      current += inc;
      if (current >= end) {
        el.innerText = end.toLocaleString();
        clearInterval(timer);
      } else {
        el.innerText = current.toLocaleString();
      }
    }, stepTime);
  }

  function renderSummary(summaryRows) {
    const total = summaryRows.reduce((s, r) => s + Number(r.predicted_amount), 0);
    animateCount(totalForecastEl, Math.round(total));
    numCategoriesEl.innerText = summaryRows.length;
    if (summaryRows.length) {
      const top = summaryRows.slice().sort((a, b) => b.predicted_amount - a.predicted_amount)[0];
      topCategoryEl.innerText = `${top.category} (${Number(top.predicted_amount).toLocaleString()})`;
    } else {
      topCategoryEl.innerText = "-";
    }
  }

  function renderChart(summaryRows) {
    const ctx = document.getElementById("barChart").getContext("2d");
    const labels = summaryRows.map(r => r.category);
    const values = summaryRows.map(r => Math.round(Number(r.predicted_amount)));

    if (barChart) {
      barChart.data.labels = labels;
      barChart.data.datasets[0].data = values;
      barChart.update();
      return;
    }

    barChart = new Chart(ctx, {
      type: "bar",
      data: { labels, datasets: [{ label: "Predicted", data: values, borderRadius: 8 }] },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => ctx.raw.toLocaleString() } }
        },
        scales: {
          y: { beginAtZero: true, ticks: { callback: val => Number(val).toLocaleString() } }
        },
        animation: { duration: 800, easing: "easeOutQuart" }
      }
    });
  }

  // fill table, create sparkline canvases and action buttons
  function renderTable(rows) {
    predTableBody.innerHTML = "";
    rows.forEach((r, idx) => {
      const tr = document.createElement("tr");
      const month = (r.year_month || "").split("T")[0];
      tr.innerHTML = `
        <td>${r.company_id}</td>
        <td>${r.category}</td>
        <td>${month}</td>
        <td>${Number(r.predicted_amount).toLocaleString()}</td>
        <td><canvas id="spark-${idx}" class="spark"></canvas></td>
        <td class="row-action">
          <button class="btn small outline details-btn" data-idx="${idx}"><i data-feather="eye"></i> Details</button>
        </td>
      `;
      predTableBody.appendChild(tr);
    });

    // after DOM appended -- render sparklines and attach details listeners
    feather.replace();
    rows.forEach((r, idx) => {
      const canvas = document.getElementById(`spark-${idx}`);
      if (!canvas) return;
      // create mock series using predicted_amount as scale
      const base = Math.round(Number(r.predicted_amount));
      const mock = generateMockSeries(base, 6);
      new Chart(canvas.getContext("2d"), {
        type: "line",
        data: { labels: mock.map((_,i)=>i+1), datasets:[{ data: mock, tension:0.3, pointRadius:0, borderWidth:2 }] },
        options: { responsive:true, maintainAspectRatio:false, scales:{x:{display:false},y:{display:false}}, plugins:{legend:{display:false}}, elements:{line:{borderColor:'rgba(90,169,230,0.9)'}}}
      });
    });

    // attach details
    document.querySelectorAll(".details-btn").forEach(btn=>{
      btn.addEventListener("click", (e)=>{
        const idx = Number(btn.getAttribute("data-idx"));
        openDetailModal(rows[idx]);
      });
    });
  }

  // Simple mock historical generator (for modal) — in real app use historical actuals
  function generateMockSeries(scale, n=6) {
    const arr = [];
    let v = Math.max(10, Math.round(scale * 0.7));
    for (let i=0;i<n;i++){
      v = Math.round(v * (0.95 + Math.random()*0.1));
      arr.push(v);
    }
    // tweak last to approach scale
    arr[n-1] = Math.round(scale * (0.9 + Math.random()*0.15));
    return arr;
  }

  // Modal logic
  const modal = document.getElementById("detailModal");
  const modalClose = document.getElementById("modalClose");
  const modalTitle = document.getElementById("modalTitle");
  const modalChartCtx = document.getElementById("modalChart").getContext("2d");
  let modalChart = null;

  function openDetailModal(row) {
    modal.classList.remove("hidden");
    modalTitle.innerText = `${row.category} — ${row.company_id}`;
    // Assemble fake actuals vs predicted series
    const predicted = Math.round(Number(row.predicted_amount));
    const actuals = generateMockSeries(predicted, 8);
    const labels = actuals.map((_,i)=>`M-${8-i}`);

    const predSeries = Array(actuals.length-1).fill(null).concat([predicted]);
    if (modalChart) modalChart.destroy();
    modalChart = new Chart(modalChartCtx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          { label: "Actual", data: actuals, borderColor: 'rgba(60,150,120,0.95)', tension:0.3, fill:false },
          { label: "Predicted (next)", data: predSeries, borderColor: 'rgba(90,169,230,0.95)', borderDash:[6,4], tension:0.3, fill:false }
        ]
      },
      options: { responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{ticks:{callback: v => v.toLocaleString()}}} }
    });

    // modal export handler: create a CSV for this category (mocked)
    document.getElementById("modalExport").onclick = () => {
      const csvRows = [["month","actual","predicted"]];
      for (let i=0;i<actuals.length;i++){
        const m = labels[i];
        const p = (i === actuals.length - 1) ? predicted : "";
        csvRows.push([m, actuals[i], p]);
      }
      const csvStr = csvRows.map(r=>r.join(",")).join("\n");
      downloadBlob(csvStr, `${row.category}_history.csv`);
    };
  }

  document.getElementById("modalClose").addEventListener("click", ()=> modal.classList.add("hidden"));

  // utility download blob
  function downloadBlob(text, filename) {
    const blob = new Blob([text], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  // export full CSV endpoint
  exportBtn.addEventListener("click", () => {
    window.location.href = downloadUrl;
  });

  // search & filter
  searchInput.addEventListener("input", ()=> applyFilters());
  categoryFilter.addEventListener("change", ()=> applyFilters());

  function applyFilters() {
    const q = searchInput.value.trim().toLowerCase();
    const cat = categoryFilter.value;
    let filtered = rawPredictions.slice();
    if (cat) filtered = filtered.filter(r => r.category === cat);
    if (q) filtered = filtered.filter(r => (r.company_id + " " + r.category + " " + (r.year_month||"")).toLowerCase().includes(q));
    renderTable(filtered);
  }

  // toggle view
  toggleButtons.forEach(btn=>{
    btn.addEventListener("click", ()=>{
      toggleButtons.forEach(b=>b.classList.remove("active"));
      btn.classList.add("active");
      const view = btn.getAttribute("data-toggle");
      if (view === "chart") {
        chartView.classList.remove("hidden");
        tableView.classList.add("hidden");
      } else {
        chartView.classList.add("hidden");
        tableView.classList.remove("hidden");
      }
    });
  });

  // refresh
  refreshBtn.addEventListener("click", fetchData);

  // initial load
  fetchData();
});
