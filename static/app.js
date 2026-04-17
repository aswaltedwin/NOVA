const App = {
    state: {
        currentPage: 'dashboard',
        activeJobId: null,
        isPolling: false,
        history: [],
        audit: [],
        chart: null
    },

    init() {
        this.cacheDOM();
        this.bindEvents();
        this.route('dashboard');
        this.loadSettings();
        
        // Initial data pull
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

    route(page) {
        this.state.currentPage = page;
        this.dom.navItems.forEach(item => {
            item.classList.toggle('active', item.getAttribute('data-page') === page);
        });
        this.dom.pageSections.forEach(sec => {
            sec.style.display = sec.id === `page-${page}` ? 'block' : 'none';
        });

        // Specific page load logic
        if (page === 'dashboard') this.refreshStats();
        if (page === 'defense') this.loadDefenseData();
        if (page === 'history') this.loadHistory();
    },

    async refreshStats() {
        try {
            const res = await fetch('/api/settings');
            const data = await res.json();
            this.dom.statTotal.innerText = data.stats.total_sessions;
            this.dom.statRisk.innerText = data.stats.avg_risk + '%';
            this.dom.statOllama.innerText = data.ollama_status.toUpperCase();
            this.initChart();
        } catch (e) {
            console.error("Failed to load stats", e);
        }
    },

    initChart() {
        const canvas = document.getElementById('riskTrendChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (this.state.chart) this.state.chart.destroy();

        // Premium Gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(212, 175, 55, 0.3)');
        gradient.addColorStop(1, 'rgba(212, 175, 55, 0)');

        this.state.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['-6h', '-5h', '-4h', '-3h', '-2h', '-1h', 'Now'],
                datasets: [{
                    label: 'Risk Score',
                    data: [15, 22, 18, 45, 30, 65, 74],
                    borderColor: '#d4af37',
                    borderWidth: 3,
                    pointBackgroundColor: '#d4af37',
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
                    x: { grid: { display : false }, ticks: { color: '#6e6e73' } },
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#6e6e73' }, min: 0, max: 100 }
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
        
        if (!log && !this.state.selectedFiles) {
            this.addTrace("SYSTEM", "Warning: No signals provided for triage.");
            return;
        }

        const fd = new FormData();
        fd.append('log_text', log);
        fd.append('model_name', model);
        if (this.state.selectedFiles) {
            Array.from(this.state.selectedFiles).forEach(f => fd.append('files', f));
        }

        this.dom.progressZone.style.display = 'block';
        this.dom.runBtn.disabled = true;
        this.addTrace("NovaManager", "Handshake confirmed. Deploying Parser and Analyzer agents...");

        try {
            const res = await fetch('/api/analyze', { method: 'POST', body: fd });
            const job = await res.json();
            this.state.activeJobId = job.id;
            this.pollJob(job.id);
        } catch (e) {
            this.addTrace("SYSTEM", "Mission deployment failed: " + e.message);
            this.dom.runBtn.disabled = false;
        }
    },

    async pollJob(jobId) {
        this.state.isPolling = true;
        const poll = async () => {
            if (!this.state.isPolling) return;
            const res = await fetch(`/api/job/${jobId}`);
            const job = await res.json();

            if (job.status === 'analyzing') {
                this.addTrace("AnalyzerAgent", "Cross-referencing RAG knowledge base for technique mapping...");
            } else if (job.status === 'review') {
                this.state.isPolling = false;
                this.addTrace("NovaManager", "Analysis phase complete. Proceeding to Analyst Validation Hub.");
                this.renderReview(job.intermediate_results);
                return;
            } else if (job.status === 'completed') {
                this.state.isPolling = false;
                this.renderFinal(job.result);
                return;
            } else if (job.status === 'failed') {
                this.state.isPolling = false;
                this.addTrace("SYSTEM", "Job Error: " + job.error);
                return;
            }

            setTimeout(poll, 2000);
        };
        poll();
    },

    renderReview(markdown) {
        this.dom.reviewZone.style.display = 'block';
        this.dom.intermediateResults.innerHTML = marked.parse(markdown || '');
        this.dom.reviewZone.scrollIntoView({ behavior: 'smooth' });
    },

    async confirmAnalysis() {
        const feedback = this.dom.analystFeedback.value;
        this.addTrace("NovaManager", "Analyst feedback integrated. Initiating final synthesis...");
        
        const fd = new FormData();
        fd.append('feedback', feedback);

        try {
            const res = await fetch(`/api/job/${this.state.activeJobId}/confirm`, { 
                method: 'POST', 
                body: fd
            });
            const job = await res.json();
            this.pollJob(job.id);
        } catch (e) {
            this.addTrace("SYSTEM", "Synthesis step failed: " + e.message);
        }
    },

    renderFinal(markdown) {
        this.dom.reportZone.style.display = 'block';
        this.dom.finalReport.innerHTML = marked.parse(markdown || '');
        this.dom.reportZone.scrollIntoView({ behavior: 'smooth' });
        this.addTrace("SYSTEM", "Mission Triage Successfully Concluded.");
        this.dom.runBtn.disabled = false;
    },

    addTrace(agent, msg) {
        const div = document.createElement('div');
        div.style.marginBottom = '8px';
        div.innerHTML = `<span style="color:var(--text-low)">[${new Date().toLocaleTimeString()}]</span> <span style="color:var(--accent-gold); font-weight:600;">[${agent}]</span> ${msg}`;
        this.dom.traceConsole.appendChild(div);
        this.dom.traceConsole.scrollTop = this.dom.traceConsole.scrollHeight;
    },

    // Vision Pipeline
    async handleVisionUpload(input) {
        const file = input.files[0];
        if (!file) return;

        // Preview
        const reader = new FileReader();
        reader.onload = (e) => {
            this.dom.visionPreview.innerHTML = `<img src="${e.target.result}" style="max-width:100%; border-radius:12px; border:1px solid var(--border-gold);">`;
        };
        reader.readAsDataURL(file);

        this.dom.visionResults.innerText = "Processing via Llama-Vision engine...";
        
        const fd = new FormData();
        fd.append('file', file);

        try {
            const res = await fetch('/api/vision/analyze', { method: 'POST', body: fd });
            const data = await res.json();
            this.dom.visionResults.innerHTML = marked.parse(data.result || 'No response from vision engine.');
        } catch (e) {
            this.dom.visionResults.innerText = "Vision analysis failed: " + e.message;
        }
    },

    // Defense Center
    async loadDefenseData() {
        try {
            const auditRes = await fetch('/api/history/audit');
            const auditData = await auditRes.json();
            
            this.dom.auditLog.innerHTML = auditData.reverse().map(l => `
                <div style="margin-bottom:15px; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 12px; border-left: 3px solid var(--accent-gold);">
                    <div style="font-size: 0.7rem; color: var(--text-low);">${new Date(l.timestamp).toLocaleString()}</div>
                    <div style="font-weight: 600; color: var(--accent-gold); margin: 5px 0;">${l.tool}</div>
                    <div style="font-size: 0.85rem;">Action: ${l.action}</div>
                    <div style="font-size: 0.8rem; color: var(--text-mid);">Target: ${l.target}</div>
                    <div style="margin-top:8px; font-family:'Fira Code'; font-size:0.75rem; color:var(--status-green);">${l.remediation_script || ''}</div>
                </div>
            `).join('') || '<div style="opacity:0.5; text-align:center; padding:20px;">No audit trail available.</div>';

            // Recommended Actions (Simulated)
            const actions = auditData.filter(a => a.state === 'SIMULATED');
            this.dom.actionsContainer.innerHTML = actions.map(a => `
                <div class="panel" style="margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-weight:600; color:var(--accent-gold);">${a.action}</div>
                        <div style="font-size:0.8rem; color:var(--text-mid);">${a.target}</div>
                    </div>
                    <button class="btn btn-primary" onclick="App.executeAction('${a.timestamp}')">Execute</button>
                </div>
            `).join('') || '<div style="opacity:0.5; text-align:center; padding:20px;">No pending actions.</div>';

        } catch (e) { console.error(e); }
    },

    async executeAction(timestamp) {
        alert("Action queued for kernel-level execution simulation.");
    },

    async loadHistory() {
        const res = await fetch('/api/history');
        const data = await res.json();
        this.dom.historyTable.innerHTML = data.map(h => `
            <tr>
                <td style="font-size:0.8rem;">${new Date(h.timestamp).toLocaleString()}</td>
                <td><span style="color:var(--accent-gold); font-size:0.8rem;">${h.model}</span></td>
                <td style="color:var(--text-mid); font-size: 0.8rem;">${h.summary}</td>
                <td><button class="btn" style="padding:4px 10px; font-size:0.7rem;" onclick="App.viewHistoricalReport('${h.id}')">View</button></td>
            </tr>
        `).join('') || '<tr><td colspan="4" style="text-align:center; opacity:0.5;">Empty mission archive.</td></tr>';
    },

    async initRAG() {
        const res = await fetch('/api/memory/learn?document=INITIALIZE'); // Simple trigger
        alert("Neural Knowledge Base Synchronized.");
    },

    loadSettings() {
        fetch('/api/settings').then(r => r.json()).then(data => {
            this.dom.modelSelect.innerHTML = data.available_models.map(m => `
                <option value="${m}" ${m === data.current_model ? 'selected' : ''}>${m}</option>
            `).join('');
        });
    }
};

window.onload = () => App.init();
