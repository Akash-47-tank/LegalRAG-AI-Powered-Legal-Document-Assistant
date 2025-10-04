/**
 * LegalRAG Frontend Application
 */

class LegalRAGApp {
    constructor() {
        this.uploadedFiles = [];
        this.isIndexed = false;
        this.initializeElements();
        this.attachEventListeners();
        this.loadStats();
    }

    initializeElements() {
        // Upload elements
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.indexBtn = document.getElementById('indexBtn');
        this.clearBtn = document.getElementById('clearBtn');

        // Query elements
        this.queryInput = document.getElementById('queryInput');
        this.queryBtn = document.getElementById('queryBtn');
        this.responseArea = document.getElementById('responseArea');

        // Stats elements
        this.docCount = document.getElementById('doc-count');
        this.chunkCount = document.getElementById('chunk-count');

        // Loading overlay
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.loadingText = document.getElementById('loadingText');
    }

    attachEventListeners() {
        // Upload events
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.indexBtn.addEventListener('click', () => this.indexDocuments());
        this.clearBtn.addEventListener('click', () => this.clearAll());

        // Query events
        this.queryBtn.addEventListener('click', () => this.handleQuery());
        this.queryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.handleQuery();
            }
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.style.borderColor = '#3b82f6';
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.style.borderColor = '';
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.style.borderColor = '';
            this.handleFileDrop(e.dataTransfer.files);
        });
    }

    showLoading(message = 'Processing...') {
        this.loadingText.textContent = message;
        this.loadingOverlay.classList.add('active');
    }

    hideLoading() {
        this.loadingOverlay.classList.remove('active');
    }

    showAlert(message, type = 'info') {
        const icons = {
            success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>`,
            error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>`,
            info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>`
        };

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            ${icons[type]}
            <p>${message}</p>
        `;

        this.responseArea.innerHTML = '';
        this.responseArea.appendChild(alertDiv);

        // Auto-remove after 5 seconds for success/info
        if (type !== 'error') {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.addFiles(files);
    }

    handleFileDrop(files) {
        const fileArray = Array.from(files);
        this.addFiles(fileArray);
    }

    addFiles(files) {
        files.forEach(file => {
            // Check file type
            const ext = file.name.split('.').pop().toLowerCase();
            if (!['pdf', 'docx', 'txt'].includes(ext)) {
                this.showAlert(`File ${file.name} is not supported. Only PDF, DOCX, and TXT files are allowed.`, 'error');
                return;
            }

            // Check if already added
            if (this.uploadedFiles.some(f => f.name === file.name)) {
                this.showAlert(`File ${file.name} is already added.`, 'info');
                return;
            }

            this.uploadedFiles.push(file);
        });

        this.renderFileList();
        this.indexBtn.disabled = this.uploadedFiles.length === 0;
        this.fileInput.value = ''; // Reset input
    }

    removeFile(index) {
        this.uploadedFiles.splice(index, 1);
        this.renderFileList();
        this.indexBtn.disabled = this.uploadedFiles.length === 0;
    }

    renderFileList() {
        if (this.uploadedFiles.length === 0) {
            this.fileList.innerHTML = '';
            return;
        }

        const fileIcons = {
            pdf: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
            </svg>`,
            docx: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
            </svg>`,
            txt: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>`
        };

        this.fileList.innerHTML = this.uploadedFiles.map((file, index) => {
            const ext = file.name.split('.').pop().toLowerCase();
            return `
                <div class="file-item">
                    <div class="file-info">
                        ${fileIcons[ext] || fileIcons.txt}
                        <span class="file-name">${file.name}</span>
                    </div>
                    <button class="file-remove" onclick="app.removeFile(${index})">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
            `;
        }).join('');
    }

    async indexDocuments() {
        if (this.uploadedFiles.length === 0) {
            this.showAlert('Please upload documents first.', 'error');
            return;
        }

        try {
            this.showLoading('Uploading documents...');

            // Upload files
            const formData = new FormData();
            this.uploadedFiles.forEach(file => {
                formData.append('files', file);
            });

            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                throw new Error('Failed to upload documents');
            }

            // Index documents
            this.loadingText.textContent = 'Indexing documents...';
            const indexResponse = await fetch('/api/index', {
                method: 'POST'
            });

            if (!indexResponse.ok) {
                throw new Error('Failed to index documents');
            }

            const result = await indexResponse.json();

            this.hideLoading();
            this.showAlert(
                `Successfully indexed ${result.files.length} document(s) into ${result.total_chunks} chunks!`,
                'success'
            );

            this.isIndexed = true;
            this.loadStats();

        } catch (error) {
            this.hideLoading();
            this.showAlert(`Error: ${error.message}`, 'error');
            console.error('Indexing error:', error);
        }
    }

    async handleQuery() {
        const query = this.queryInput.value.trim();

        if (!query) {
            this.showAlert('Please enter a question.', 'error');
            return;
        }

        if (!this.isIndexed) {
            this.showAlert('Please upload and index documents first.', 'error');
            return;
        }

        try {
            this.showLoading('Searching documents...');

            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });

            if (!response.ok) {
                throw new Error('Failed to query documents');
            }

            const result = await response.json();

            this.hideLoading();
            this.displayAnswer(result);

        } catch (error) {
            this.hideLoading();
            this.showAlert(`Error: ${error.message}`, 'error');
            console.error('Query error:', error);
        }
    }

    displayAnswer(result) {
        const { answer, sources, query } = result;

        const sourcesHTML = sources.length > 0 ? `
            <div class="sources-card">
                <h3 class="sources-header">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                    Sources
                </h3>
                ${sources.map(source => `
                    <div class="source-item">
                        <div class="source-info">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14 2 14 8 20 8"></polyline>
                            </svg>
                            <div class="source-details">
                                <h4>${source.document}</h4>
                                <p>${source.page ? `Page ${source.page}` : 'Full document'}</p>
                            </div>
                        </div>
                        <span class="source-relevance">${(source.relevance * 100).toFixed(0)}% match</span>
                    </div>
                `).join('')}
            </div>
        ` : '';

        this.responseArea.innerHTML = `
            <div class="answer-card">
                <h3 class="answer-header">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    Answer
                </h3>
                <div class="answer-text">${this.formatAnswer(answer)}</div>
            </div>
            ${sourcesHTML}
        `;
    }

    formatAnswer(text) {
        // Convert markdown-style formatting to HTML
        return text
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }

    async clearAll() {
        if (!confirm('Are you sure you want to clear all documents and data?')) {
            return;
        }

        try {
            this.showLoading('Clearing data...');

            const response = await fetch('/api/clear', {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error('Failed to clear data');
            }

            this.hideLoading();
            this.uploadedFiles = [];
            this.isIndexed = false;
            this.renderFileList();
            this.indexBtn.disabled = true;
            this.responseArea.innerHTML = `
                <div class="empty-state">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <p>Your answers will appear here</p>
                </div>
            `;
            this.queryInput.value = '';
            this.loadStats();
            this.showAlert('All data cleared successfully!', 'success');

        } catch (error) {
            this.hideLoading();
            this.showAlert(`Error: ${error.message}`, 'error');
            console.error('Clear error:', error);
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            if (!response.ok) return;

            const data = await response.json();

            if (data.indexed && data.stats) {
                this.docCount.textContent = data.stats.total_documents || 0;
                this.chunkCount.textContent = data.stats.total_vectors || 0;
            } else {
                this.docCount.textContent = '0';
                this.chunkCount.textContent = '0';
            }

        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
}

// Initialize app
const app = new LegalRAGApp();