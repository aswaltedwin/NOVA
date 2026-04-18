const App = {
    state: {
        currentPage: 'dashboard',
        activeJobId: null,
        websocket: null,
        history: [],
        audit: [],
        chart: null,
        apiKey: 'NOVA-SENTINEL-SECURE-KEY-2026' // Default for now
    },

    init() {
        this.cacheDOM();
        this.bindEvents();
        this.initWebSocket();
        this.route('dashboard');
        this.loadSettings();
        this.refreshStats();
    },

    cacheDOM() {
        this.dom = {
            navItems: document.querySelectorAll('.nav-item'),
            mainContent: document.getElementById('main-content'),
            pageSections: document.querySelectorAll('.page-section'),
            
            // Triage
            logInput: document.getElementById('log-input'),
            modelSelect: document.getElementById('model-select'),
            fileInput: document.getElementById('file-input'),
            selectedFiles: document.getElementById('selected-files'),
            dropZone: document.getElementById('drop-zone'),
            runBtn: document.getElementById('run-analysis-btn'),
            traceConsole: document.getElementById('xai-trace'),
            progressZone: document.getElementById('analysis-progress-container'),
            reviewZone: document.getElementById('review-zone'),
            reportZone: document.getElementById('analysis-results-container'),
            intermediateResults: document.getElementById('intermediate-results'),
            finalReport: document.getElementById('report-content'),
            analystFeedback: document.getElementById('analyst-feedback'),

            // Vision
            visionPreview: document.getElementById('vision-preview'),
            visionResults: document.getElementById('vision-results'),

            // Dashboard
            statTotal: document.getElementById('stat-total'),
            statRisk: document.getElementById('stat-risk'),
            statOllama: document.getElementById('stat-ollama'),

            // System
            historyTable: document.getElementById('history-table-body'),
            auditLog: document.getElementById('audit-log-container'),
            actionsContainer: document.getElementById('actions-container')
        };
    },

    bindEvents() {
        this.dom.navItems.forEach(item => {
            item.onclick = () => this.route(item.getAttribute('data-page'));
        });

        if (this.dom.dropZone) {
            this.dom.dropZone.ondragover = (e) => { e.preventDefault(); this.dom.dropZone.classList.add('drag-over'); };
            this.dom.dropZone.ondragleave = () => this.dom.dropZone.classList.remove('drag-over');
            this.dom.dropZone.ondrop = (e) => { e.preventDefault(); this.handleFiles(e.dataTransfer.files); };
        }
        
        if (this.dom.fileInput) {
            this.dom.fileInput.onchange = (e) => this.handleFiles(e.target.files);
        }
    },

    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.state.websocket = new WebSocket(`${protocol}//${window.location.host}/ws/jobs`);
        
        this.state.websocket.onmsg = (event) => {
            const data = JSON.parse(event.data);
            this.handleJobUpdate(data);
        };

        this.state.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleJobUpdate(data);
        };

        this.state.websocket.onclose = () => {
            console.warn("WebSocket closed. Reconnecting...");
            setTimeout(() => this.initWebSocket(), 3000);
        };
    },

    handleJobUpdate(data) {
        if (data.job_id !== this.state.activeJobId) return;

        if (data.status === 'analyzing') {
            this.addTrace("AnalyzerAgent", `Deep scanning telemetry... Coverage [${data.progress}%]`);
        } else if (data.status === 'review') {
            this.addTrace("NovaManager", "Analysis complete. Awaiting human validation.");
            this.renderReview(data.intermediate);
        } else if (data.status === 'completed') {
            this.addTrace("ReporterAgent", "Mission report finalized.");
            this.renderFinal(data.result);
        } else if (data.status === 'failed') {
            this.addTrace("SYSTEM", `CRITICAL FAILURE: ${data.error}`);
            this.dom.runBtn.disabled = false;
        }
    },

    route(page) {
        this.state.currentPage = page;
        this.dom.navItems.forEach(item => {
            item.classList.toggle('active', item.getAttribute('data-page') === page);
        });
        this.dom.pageSections.forEach(sec => {
            sec.style.display = sec.id === `page-${page}` ? 'block' : 'none';
        });

        if (page === 'dashboard') this.refreshStats();
        if (page === 'defense') this.loadDefenseData();
        if (page === 'history') this.loadHistory();
    },

    async secureFetch(url, options = {}) {
        options.headers = {
            ...options.headers,
            'X-API-KEY': this.state.apiKey
        };
        return fetch(url, options);
    },

    async refreshStats() {
        try {
            const res = await this.secureFetch('/api/settings');
            const data = await res.json();
            this.dom.statTotal.innerText = data.stats.total_sessions;
            this.dom.statRisk.innerText = data.stats.avg_risk + '%';
            this.dom.statOllama.innerText = data.ollama_status.toUpperCase();
            this.initChart();
        } catch (e) {
            console.error("Stats failure", e);
        }
    },

    initChart() {
        const canvas = document.getElementById('riskTrendChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (this.state.chart) this.state.chart.destroy();

        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(212, 175, 55, 0.4)');
        gradient.addColorStop(1, 'rgba(10, 11, 16, 0)');

        this.state.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['-6h', '-5h', '-4h', '-3h', '-2h', '-1h', 'Now'],
                datasets: [{
                    label: 'Risk Score',
                    data: [12, 25, 20, 52, 38, 70, 74],
                    borderColor: '#D4AF37',
                    borderWidth: 3,
                    pointBackgroundColor: '#D4AF37',
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display : false }, ticks: { color: '#65676B' } },
                    y: { grid: { color: 'rgba(212, 175, 55, 0.1)' }, ticks: { color: '#65676B' }, min: 0, max: 100 }
                }
            }
        });
    },

    handleFiles(files) {
        this.state.selectedFiles = files;
        this.dom.selectedFiles.innerText = `${files.length} artifact(s) staged.`;
    },

    async startAnalysis() {
        const log = this.dom.logInput.value;
        const model = this.dom.modelSelect.value;
        
        const fd = new FormData();
        fd.append('log_text', log);
        fd.append('model_name', model);
        if (this.state.selectedFiles) {
            Array.from(this.state.selectedFiles).forEach(f => fd.append('files', f));
        }

        this.dom.progressZone.style.display = 'block';
        this.dom.runBtn.disabled = true;
        this.addTrace("NovaManager", "Initiating secure mission handshake. Deploying agents...");

        try {
            const res = await this.secureFetch('/api/analyze', { method: 'POST', body: fd });
            const job = await res.json();
            this.state.activeJobId = job.id;
        } catch (e) {
            this.addTrace("SYSTEM", `Deployment error: ${e.message}`);
            this.dom.runBtn.disabled = false;
        }
    },

    renderReview(markdown) {
        this.dom.reviewZone.style.display = 'block';
        this.dom.intermediateResults.innerHTML = marked.parse(markdown || '');
        this.dom.reviewZone.scrollIntoView({ behavior: 'smooth' });
    },

    async confirmAnalysis() {
        const feedback = this.dom.analystFeedback.value;
        this.addTrace("NovaManager", "Feedback integrated. Commencing final synthesis.");
        
        const fd = new FormData();
        fd.append('feedback', feedback);

        try {
            await this.secureFetch(`/api/job/${this.state.activeJobId}/confirm`, { 
                method: 'POST', 
                body: fd
            });
        } catch (e) {
            this.addTrace("SYSTEM", `Synthesis failed: ${e.message}`);
        }
    },

    renderFinal(markdown) {
        this.dom.reportZone.style.display = 'block';
        this.dom.finalReport.innerHTML = marked.parse(markdown || '');
        this.dom.reportZone.scrollIntoView({ behavior: 'smooth' });
        this.addTrace("SYSTEM", "Mission Triage Finalized.");
        this.dom.runBtn.disabled = false;
    },

    addTrace(agent, msg) {
        const div = document.createElement('div');
        div.style.marginBottom = '10px';
        div.style.paddingLeft = '5px';
        div.innerHTML = `<span style="color:var(--text-low)">[${new Date().toLocaleTimeString()}]</span> <span style="color:var(--accent-gold); font-weight:600;">[${agent}]</span> ${msg}`;
        this.dom.traceConsole.appendChild(div);
        this.dom.traceConsole.scrollTop = this.dom.traceConsole.scrollHeight;
    },

    async handleVisionUpload(input) {
        const file = input.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            this.dom.visionPreview.innerHTML = `<img src="${e.target.result}" style="max-width:100%; border-radius:16px; border:1px solid var(--border-gold); box-shadow: var(--shadow-premium);">`;
        };
        reader.readAsDataURL(file);

        this.dom.visionResults.innerText = "Analyzing artifact via Llama-Vision...";
        
        const fd = new FormData();
        fd.append('file', file);

        try {
            const res = await this.secureFetch('/api/vision/analyze', { method: 'POST', body: fd });
            const data = await res.json();
            this.dom.visionResults.innerHTML = marked.parse(data.result || 'No signals detected.');
        } catch (e) {
            this.dom.visionResults.innerText = "Vision analysis failed: " + e.message;
        }
    },

    async loadDefenseData() {
        try {
            const auditRes = await this.secureFetch('/api/history/audit');
            const auditData = await auditRes.json();
            
            this.dom.auditLog.innerHTML = auditData.reverse().map(l => `
                <div style="margin-bottom:15px; background: rgba(255,255,255,0.02); padding: 15px; border-radius: 12px; border-left: 3px solid var(--accent-gold);">
                    <div style="font-size: 0.7rem; color: var(--text-low);">${new Date(l.timestamp).toLocaleString()}</div>
                    <div style="font-weight: 600; color: var(--accent-gold); margin: 5px 0;">${l.action}</div>
                    <div style="font-size: 0.8rem; color: var(--text-mid);">${l.details}</div>
                </div>
            `).join('') || '<div style="opacity:0.5; text-align:center; padding:20px;">Secure audit log empty.</div>';
        } catch (e) { console.error(e); }
    },

    async loadHistory() {
        const res = await this.secureFetch('/api/history');
        const data = await res.json();
        // Backend simplified history to Job records
        // Map Job table to the display
        this.dom.historyTable.innerHTML = data.map(h => `
            <tr>
                <td>${new Date(h.timestamp || Date.now()).toLocaleString()}</td>
                <td><span style="color:var(--accent-gold);">${h.model}</span></td>
                <td>${h.summary || 'Legacy Record'}</td>
                <td><button class="btn" onclick="App.viewHistoricalReport('${h.id}')">View</button></td>
            </tr>
        `).join('');
    },

    loadSettings() {
        this.secureFetch('/api/settings').then(r => r.json()).then(data => {
            this.dom.modelSelect.innerHTML = data.available_models.map(m => `
                <option value="${m}" ${m === data.current_model ? 'selected' : ''}>${m}</option>
            `).join('');
        });
    }
};

window.onload = () => App.init();
