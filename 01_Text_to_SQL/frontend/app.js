document.addEventListener('DOMContentLoaded', () => {
    // State Variables
    let currentChart = null;
    let currentResponseData = null;

    // DOM Elements
    const queryInput = document.getElementById('query-input');
    const btnSubmit = document.getElementById('btn-submit-query');
    const pillsWrapper = document.getElementById('pills-wrapper');
    const loadingState = document.getElementById('loading-state');
    const responseContainer = document.getElementById('response-container');

    // Metrics DOM
    const metricTotalMs = document.getElementById('metric-total-ms');
    const metricExecMs = document.getElementById('metric-exec-ms');
    const metricRowCount = document.getElementById('metric-row-count');
    const metricAstBadge = document.getElementById('metric-ast-badge');
    const selfCorrectionItem = document.getElementById('self-correction-item');
    const selfCorrectionBadge = document.getElementById('self-correction-badge');

    // Explanation & Output DOM
    const explanationText = document.getElementById('explanation-text');
    const tableHead = document.getElementById('table-head');
    const tableBody = document.getElementById('table-body');
    const tableRowsInfo = document.getElementById('table-rows-info');
    const sqlCodeDisplay = document.getElementById('sql-code-display');
    const pipelineStepper = document.getElementById('pipeline-stepper');

    // Modals
    const btnOpenSchema = document.getElementById('btn-open-schema');
    const btnCloseSchema = document.getElementById('btn-close-schema');
    const schemaModal = document.getElementById('schema-modal');
    const schemaModalBody = document.getElementById('schema-modal-body');

    const btnRunEval = document.getElementById('btn-run-eval');
    const btnCloseEval = document.getElementById('btn-close-eval');
    const evalModal = document.getElementById('eval-modal');
    const evalModalBody = document.getElementById('eval-modal-body');

    // Header Badges
    const dbTypeLabel = document.getElementById('db-type-label');
    const providerLabel = document.getElementById('provider-label');
    const btnExportCsv = document.getElementById('btn-export-csv');
    const btnCopySql = document.getElementById('btn-copy-sql');

    // Initialize App
    init();

    async function init() {
        await fetchSystemHealth();
        await fetchSampleQueries();
        setupEventListeners();
    }

    async function fetchSystemHealth() {
        try {
            const res = await fetch('/api/v1/health');
            const data = await res.json();
            if (dbTypeLabel) dbTypeLabel.textContent = data.database_type.toUpperCase();
            if (providerLabel) {
                if (data.llm_provider === 'gemini') {
                    providerLabel.textContent = `Gemini (${data.gemini_model})`;
                } else if (data.llm_provider === 'openai') {
                    providerLabel.textContent = 'OpenAI (GPT-4o)';
                } else {
                    providerLabel.textContent = 'Local Engine (Zero API Key)';
                }
            }
        } catch (e) {
            console.warn('Could not fetch health status', e);
        }
    }

    async function fetchSampleQueries() {
        try {
            const res = await fetch('/api/v1/sample-queries');
            const data = await res.json();
            if (data.sample_queries && pillsWrapper) {
                pillsWrapper.innerHTML = '';
                data.sample_queries.forEach(q => {
                    const pill = document.createElement('button');
                    pill.className = 'query-pill';
                    pill.textContent = q.question;
                    pill.addEventListener('click', () => {
                        queryInput.value = q.question;
                        submitQuery();
                    });
                    pillsWrapper.appendChild(pill);
                });
            }
        } catch (e) {
            console.warn('Could not fetch sample queries', e);
        }
    }

    function setupEventListeners() {
        btnSubmit.addEventListener('click', submitQuery);

        queryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitQuery();
            }
        });

        // Tab Switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                btn.classList.add('active');
                const targetTab = btn.getAttribute('data-tab');
                document.getElementById(targetTab).classList.add('active');
            });
        });

        // Modals
        btnOpenSchema.addEventListener('click', openSchemaModal);
        btnCloseSchema.addEventListener('click', () => schemaModal.classList.add('hidden'));

        btnRunEval.addEventListener('click', openEvalModal);
        btnCloseEval.addEventListener('click', () => evalModal.classList.add('hidden'));

        // CSV Export & SQL Copy
        btnExportCsv.addEventListener('click', exportCsv);
        btnCopySql.addEventListener('click', copySql);
    }

    async function submitQuery() {
        const question = queryInput.value.trim();
        if (!question) return;

        // UI Loading state
        loadingState.classList.remove('hidden');
        responseContainer.classList.add('hidden');

        try {
            const res = await fetch('/api/v1/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question, allow_retry: true })
            });

            const data = await res.json();
            currentResponseData = data;
            renderResponse(data);
        } catch (err) {
            alert('Pipeline execution failed: ' + err.message);
        } finally {
            loadingState.classList.add('hidden');
        }
    }

    function renderResponse(data) {
        responseContainer.classList.remove('hidden');

        // Metrics
        metricTotalMs.textContent = `${data.total_latency_ms} ms`;
        metricExecMs.textContent = `${data.execution_time_ms} ms`;
        metricRowCount.textContent = data.row_count;

        // AST Guardrail Status
        if (data.is_valid) {
            metricAstBadge.className = 'metric-badge success';
            metricAstBadge.innerHTML = '<i class="fa-solid fa-shield-halved"></i> AST Verified';
        } else {
            metricAstBadge.className = 'metric-badge warning';
            metricAstBadge.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Safety Warning';
        }

        // Self Correction Badge
        if (data.self_correction_attempts > 0) {
            selfCorrectionItem.classList.remove('hidden');
            selfCorrectionBadge.textContent = `${data.self_correction_attempts} Repairs`;
        } else {
            selfCorrectionItem.classList.add('hidden');
        }

        // Executive Explanation
        explanationText.textContent = data.explanation || 'No explanation generated.';

        // Render Table
        renderDataTable(data.columns, data.data);

        // Render SQL
        sqlCodeDisplay.textContent = data.validated_sql || data.generated_sql;

        // Render Chart
        renderChart(data.chart_config);

        // Render Pipeline Stepper
        renderPipelineStepper(data.pipeline_steps);
    }

    function renderDataTable(columns, rows) {
        tableHead.innerHTML = '';
        tableBody.innerHTML = '';

        if (!columns || columns.length === 0 || !rows) {
            tableRowsInfo.textContent = '0 results returned';
            tableHead.innerHTML = '<tr><th>No Results</th></tr>';
            tableBody.innerHTML = '<tr><td>Query returned zero rows.</td></tr>';
            return;
        }

        tableRowsInfo.textContent = `Showing ${rows.length} results`;

        // Head
        const trHead = document.createElement('tr');
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col.replace(/_/g, ' ').toUpperCase();
            trHead.appendChild(th);
        });
        tableHead.appendChild(trHead);

        // Body
        rows.forEach(row => {
            const tr = document.createElement('tr');
            columns.forEach(col => {
                const td = document.createElement('td');
                const val = row[col];
                td.textContent = val !== null && val !== undefined ? val : 'NULL';
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });
    }

    function renderChart(chartConfig) {
        const ctx = document.getElementById('analyticsChart').getContext('2d');
        if (currentChart) {
            currentChart.destroy();
            currentChart = null;
        }

        if (!chartConfig || !chartConfig.chart_js_spec || !chartConfig.chart_js_spec.data) {
            return;
        }

        try {
            currentChart = new Chart(ctx, chartConfig.chart_js_spec);
        } catch (e) {
            console.warn('Could not render Chart.js:', e);
        }
    }

    function renderPipelineStepper(steps) {
        pipelineStepper.innerHTML = '';
        if (!steps || steps.length === 0) return;

        steps.forEach(step => {
            const row = document.createElement('div');
            row.className = 'step-row';
            row.innerHTML = `
                <div class="step-info">
                    <div class="step-icon"><i class="fa-solid fa-check"></i></div>
                    <div>
                        <div class="step-name">${step.step_name}</div>
                        <div class="hint">${step.status.toUpperCase()}</div>
                    </div>
                </div>
                <div class="step-duration">${step.duration_ms} ms</div>
            `;
            pipelineStepper.appendChild(row);
        });
    }

    async function openSchemaModal() {
        schemaModalBody.innerHTML = '<div class="spinner"></div>';
        schemaModal.classList.remove('hidden');

        try {
            const res = await fetch('/api/v1/schema');
            const schemaData = await res.json();

            let html = `<p style="margin-bottom: 16px; color: var(--text-secondary);">Database Type: <strong>${schemaData.database_type.toUpperCase()}</strong> | Total Tables: <strong>${schemaData.total_tables}</strong></p>`;

            schemaData.tables.forEach(tbl => {
                html += `
                    <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                        <h4 style="color: #6ee7b7; font-size: 16px; margin-bottom: 8px;"><i class="fa-solid fa-table"></i> ${tbl.table_name} (${tbl.row_count} rows)</h4>
                        <table class="data-table" style="margin-bottom: 12px;">
                            <thead>
                                <tr><th>Column</th><th>Type</th><th>Key</th></tr>
                            </thead>
                            <tbody>
                                ${tbl.columns.map(c => `
                                    <tr>
                                        <td><code>${c.name}</code></td>
                                        <td>${c.type}</td>
                                        <td>${c.primary_key ? '<span style="color: #fde047;">PK</span>' : (c.foreign_key ? `<span style="color: #93c5fd;">FK -> ${c.foreign_key}</span>` : '-')}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            });

            schemaModalBody.innerHTML = html;
        } catch (e) {
            schemaModalBody.innerHTML = `<p style="color: var(--accent-rose)">Failed to load schema: ${e.message}</p>`;
        }
    }

    async function openEvalModal() {
        evalModalBody.innerHTML = '<div class="spinner"></div><p style="text-align:center;">Running Evaluation Benchmark Suite across test questions...</p>';
        evalModal.classList.remove('hidden');

        try {
            const res = await fetch('/api/v1/eval');
            const evalData = await res.json();

            let html = `
                <div class="metrics-bar" style="margin-bottom: 20px;">
                    <div class="metric-item">
                        <span class="metric-label">Execution Accuracy</span>
                        <span class="metric-val" style="color: #6ee7b7;">${evalData.execution_accuracy}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Valid SQL Rate</span>
                        <span class="metric-val" style="color: #93c5fd;">${evalData.valid_sql_rate}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Self-Correction Rate</span>
                        <span class="metric-val" style="color: #fde047;">${evalData.self_correction_recovery_rate}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Avg Latency</span>
                        <span class="metric-val">${evalData.avg_latency_ms} ms</span>
                    </div>
                </div>

                <h4 style="margin-bottom: 12px;">Benchmark Test Cases (${evalData.total_cases})</h4>
                <div class="table-scroll">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th>Question</th>
                                <th>Valid SQL</th>
                                <th>Executed</th>
                                <th>Latency</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${evalData.results_detail.map(item => `
                                <tr>
                                    <td><span style="font-size:11px; padding:2px 8px; border-radius:10px; background:rgba(255,255,255,0.06);">${item.category}</span></td>
                                    <td>${item.question}</td>
                                    <td>${item.is_valid ? '<span style="color:#6ee7b7;">PASS</span>' : '<span style="color:#ef4444;">FAIL</span>'}</td>
                                    <td>${item.execution_success ? '<span style="color:#6ee7b7;">SUCCESS</span>' : '<span style="color:#ef4444;">FAIL</span>'}</td>
                                    <td>${item.total_latency_ms} ms</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;

            evalModalBody.innerHTML = html;
        } catch (e) {
            evalModalBody.innerHTML = `<p style="color: var(--accent-rose)">Failed to run benchmark suite: ${e.message}</p>`;
        }
    }

    function exportCsv() {
        if (!currentResponseData || !currentResponseData.data || currentResponseData.data.length === 0) {
            alert('No data available to export.');
            return;
        }
        const cols = currentResponseData.columns;
        const rows = currentResponseData.data;

        let csvContent = "data:text/csv;charset=utf-8," + cols.join(",") + "\n";
        rows.forEach(r => {
            const rowValues = cols.map(c => `"${String(r[c] || '').replace(/"/g, '""')}"`);
            csvContent += rowValues.join(",") + "\n";
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "text_to_sql_results.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    function copySql() {
        const sqlText = sqlCodeDisplay.textContent;
        navigator.clipboard.writeText(sqlText).then(() => {
            btnCopySql.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {
                btnCopySql.innerHTML = '<i class="fa-solid fa-copy"></i> Copy SQL';
            }, 2000);
        });
    }
});
