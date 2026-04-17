const App = {
    state: {
        currentPage: 'dashboard',
        isAnalyzing: false,
        activeJobId: null,
        history: [],
        settings: {},
        chart: null
    },

    init() {
        this.cacheDOM();
        this.bindEvents();
        this.route('dashboard');
        this.loadSettings();
    },

    cacheDOM() {
        this.dom = {
            navItems: document.querySelectorAll('.nav-item'),
            dropZone: document.getElementById('drop-zone'),
            fileInput: document.getElementById('file-input'),
            logInput: document.getElementById('log-input'),
            modelSelect: document.getElementById('model-select'),
            xaiTrace: document.getElementById('xai-trace'),
            reviewZone: document.getElementById('review-zone'),
            resultsZone: document.getElementById('analysis-results-container'),
            inputZone: document.getElementById('analysis-input-container'),
            progressZone: document.getElementById('analysis-progress-container'),
            intermediateResults: document.getElementById('intermediate-results'),
            historyTable: document.getElementById('history-table-body'),
        };
    },

    bindEvents() {
        this.dom.navItems.forEach(item => {
            item.addEventListener('click', () => this.route(item.getAttribute('data-page')));
        });

        if (this.dom.dropZone) {
            this.dom.dropZone.onclick = () => this.dom.fileInput.click();
            this.dom.fileInput.onchange = (e) => this.handleFiles(e.target.files);
            this.dom.dropZone.ondragover = (e) => { e.preventDefault(); this.dom.dropZone.classList.add('drag-over'); };
            this.dom.dropZone.ondragleave = () => this.dom.dropZone.classList.remove('drag-over');
            this.dom.dropZone.ondrop = (e) => { e.preventDefault(); this.handleFiles(e.dataTransfer.files); };
        }
    },

    route(page) {
        this.state.currentPage = page;
        this.dom.navItems.forEach(item => item.classList.toggle('active', item.getAttribute('data-page') === page));
        document.querySelectorAll('.page-section').forEach(s => s.style.display = s.id === `page-${page}` ? 'block' : 'none');
        if (page === 'dashboard') this.loadDashboard();
        if (page === 'history') this.loadHistory();
        if (page === 'analysis') this.loadSampleLogs();
    },

    async loadDashboard() {
        const res = await fetch('/api/settings');
        const data = await res.json();
        document.getElementById('stat-total').innerText = data.stats.total_sessions;
        document.getElementById('stat-risk').innerText = data.stats.avg_risk + '%';
        document.getElementById('stat-ollama').innerText = data.ollama_status.toUpperCase();
        this.initChart();
    },

    initChart() {
        const canvas = document.getElementById('riskTrendChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (this.state.chart) this.state.chart.destroy();

        this.state.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00'],
                datasets: [{
                    label: 'Risk Level',
                    data: [12, 19, 34, 45, 23, 67, 74],
                    borderColor: '#00f5ff',
                    backgroundColor: 'rgba(0, 245, 255, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { display: false },
                    x: { grid: { color: 'rgba(255,255,255,0.05)' }, border: { display: false } }
                }
            }
        });
    },

    async loadSampleLogs() {
        const res = await fetch('/api/logs');
        const logs = await res.json();
        const container = document.getElementById('selected-files');
        if (logs.length > 0) {
            container.innerHTML = `<p style="margin-bottom:10px;">Available: ${logs.length} synthetic artifacts detected.</p>`;
        }
    },

    async loadSettings() {
        const res = await fetch('/api/settings');
        const data = await res.json();
        this.state.settings = data;
        this.dom.modelSelect.innerHTML = data.available_models.map(m => `<option value="${m}">${m === data.current_model ? 'selected' : ''}>${m}</option>`).join('');
    },

    handleFiles(files) {
        this.state.selectedFiles = files;
        document.getElementById('selected-files').innerText = Array.from(files).map(f => f.name).join(', ');
    },

    async startAnalysis() {
        const log = this.dom.logInput.value;
        const model = this.dom.modelSelect.value;
        
        if (!log && !this.state.selectedFiles) {
            // Trigger synthetic log logic if input is empty
            return this.runSyntheticDemo(model);
        }

        this.setUIState('analyzing');
        this.addTrace("NovaManager", "Triage mission initiated. Deploying agents...");

        const fd = new FormData();
        fd.append('log_text', log);
        fd.append('model_name', model);
        if (this.state.selectedFiles) Array.from(this.state.selectedFiles).forEach(f => fd.append('files', f));

        try {
            this.updateStepper(2);
            this.addTrace("ParserAgent", "Normalizing signals and extracting entities...");
            
            const res = await fetch('/api/analyze', { method: 'POST', body: fd });
            const job = await res.json();
            this.state.activeJobId = job.id;

            this.addTrace("AnalyzerAgent", "Mapping anomalies to MITRE ATT&CK techniques...");
            this.addTrace("RiskCalculator", "Computing severity and confidence metrics...");

            this.updateStepper(3);
            this.renderReview(job.intermediate_results);
            this.setUIState('review');
        } catch (e) {
            this.addTrace("SYSTEM", "Critical Error: " + e.message);
            this.setUIState('input');
        }
    },

    async runSyntheticDemo(model) {
        this.addTrace("NovaManager", "No manual log provided. Loading Phase 2 Synthetic Triage dataset...");
        const res = await fetch('/api/logs');
        const logs = await res.json();
        if (logs.length > 0) {
            this.dom.logInput.value = `[AUTO_INGEST] Loading artifact: ${logs[0].filename}`;
            this.startAnalysis();
        }
    },

    async confirmAnalysis() {
        const feedback = document.getElementById('analyst-feedback').value;
        this.setUIState('synthesis');
        this.updateStepper(4);
        this.addTrace("NovaManager", "Analyst feedback received. Synthesizing final report...");

        try {
            const res = await fetch(`/api/job/${this.state.activeJobId}/confirm`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ feedback })
            });
            const job = await res.json();
            this.renderFinal(job.result);
            this.setUIState('completed');
        } catch (e) {
            this.addTrace("SYSTEM", "Synthesis Failed: " + e.message);
        }
    },

    async markConfirmed(isConfirmed) {
        const doc = document.getElementById('report-content').innerText;
        await fetch('/api/memory/learn', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ document: doc, id: isConfirmed ? 'CONFIRMED' : 'FALSE_POSITIVE' })
        });
        alert(isConfirmed ? "Insight stored in long-term memory." : "Marked as False Positive. System learning updated.");
    },

    renderReview(markdown) {
        this.dom.intermediateResults.innerHTML = this.parseMd(markdown);
    },

    renderFinal(markdown) {
        document.getElementById('report-content').innerHTML = this.parseMd(markdown);
    },

    setUIState(state) {
        const views = {
            'input': [1, 0, 0, 0],
            'analyzing': [0, 1, 0, 0],
            'review': [0, 0, 1, 0],
            'completed': [0, 0, 0, 1]
        };
        const [i, p, r, f] = views[state] || views['input'];
        this.dom.inputZone.style.display = i ? 'block' : 'none';
        this.dom.progressZone.style.display = p ? 'block' : 'none';
        this.dom.reviewZone.style.display = r ? 'block' : 'none';
        this.dom.resultsZone.style.display = f ? 'block' : 'none';
    },

    updateStepper(step) {
        document.querySelectorAll('.step').forEach((s, idx) => {
            s.classList.toggle('active', idx + 1 === step);
            s.classList.toggle('completed', idx + 1 < step);
        });
    },

    addTrace(agent, msg) {
        const time = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
        this.dom.xaiTrace.innerHTML += `<div style="margin-bottom:5px;"><span style="color:var(--text-secondary)">[${time}]</span> <span style="color:var(--accent-cyan)">[${agent}]</span> ${msg}</div>`;
        this.dom.xaiTrace.scrollTop = this.dom.xaiTrace.scrollHeight;
    },

    parseMd(md) {
        if (!md) return '';
        return md.replace(/^# (.*$)/gim, '<h1>$1</h1>')
                 .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                 .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
                 .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
                 .replace(/\n/g, '<br>');
    },

    async loadHistory() {
        const res = await fetch('/api/history');
        const data = await res.json();
        this.dom.historyTable.innerHTML = data.map(h => `
            <tr>
                <td>${new Date(h.timestamp).toLocaleString()}</td>
                <td><span class="badge">${h.model}</span></td>
                <td style="color:var(--text-secondary); font-size: 0.8rem;">${h.summary}</td>
                <td><button class="btn btn-sm" onclick="App.viewReport('${h.id}')">View</button></td>
            </tr>
        `).join('') || '<tr><td colspan="4" style="text-align:center; padding: 20px;">No mission history found.</td></tr>';
    },

    viewReport(id) {
        // Simple logic to show report in result view
        this.route('results');
        const entry = this.state.history.find(h => h.id === id);
        if (entry) document.getElementById('report-view-content').innerHTML = this.parseMd(entry.report);
    }
};

window.onload = () => App.init();
