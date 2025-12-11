// app/static/js/python-practice.js
// Python practice JavaScript functions

/**
 * Initialize code editor with Monaco Editor
 */
function initializePythonEditor(elementId, initialCode, options = {}) {
    const defaultOptions = {
        value: initialCode || '# Write your code here\n',
        language: 'python',
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 14,
        scrollBeyondLastLine: false,
        lineNumbers: 'on',
        renderWhitespace: 'selection',
        tabSize: 4,
        wordWrap: 'on',
        ...options
    };
    
    require.config({ 
        paths: { 
            vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' 
        }
    });
    
    return new Promise((resolve, reject) => {
        require(['vs/editor/editor.main'], function() {
            try {
                const editor = monaco.editor.create(
                    document.getElementById(elementId), 
                    defaultOptions
                );
                resolve(editor);
            } catch (error) {
                reject(error);
            }
        });
    });
}

/**
 * Submit code for execution
 */
async function submitPythonCode(exerciseId, code, csrfToken) {
    try {
        const response = await fetch(`/python-practice/exercise/${exerciseId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ code: code })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to submit code');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error submitting code:', error);
        throw error;
    }
}

/**
 * Display execution results
 */
function displayExecutionResults(container, results) {
    if (!container) return;
    
    let html = '';
    
    // Status
    const statusClass = results.status === 'passed' ? 'success' : 
                        results.status === 'failed' ? 'warning' : 'danger';
    html += `<div class="alert alert-${statusClass}">`;
    html += `<strong>Status:</strong> ${results.status.toUpperCase()}`;
    html += `</div>`;
    
    // Output
    if (results.output) {
        html += `<div class="mb-3">`;
        html += `<strong>Output:</strong>`;
        html += `<pre class="bg-light p-3 mt-2">${escapeHtml(results.output)}</pre>`;
        html += `</div>`;
    }
    
    // Error
    if (results.error) {
        html += `<div class="mb-3">`;
        html += `<strong>Error:</strong>`;
        html += `<pre class="bg-danger text-white p-3 mt-2">${escapeHtml(results.error)}</pre>`;
        html += `</div>`;
    }
    
    // Test results
    if (results.test_results && results.test_results.length > 0) {
        html += `<div class="mb-3">`;
        html += `<strong>Test Results:</strong>`;
        results.test_results.forEach(test => {
            const testClass = test.passed ? 'success' : 'danger';
            html += `<div class="alert alert-${testClass} mt-2">`;
            html += `<strong>Test ${test.test_number}:</strong> ${test.description} `;
            html += test.passed ? '✓ Passed' : '✗ Failed';
            if (!test.passed) {
                html += `<br><small>Expected: ${escapeHtml(JSON.stringify(test.expected))}</small>`;
                html += `<br><small>Got: ${escapeHtml(JSON.stringify(test.actual))}</small>`;
            }
            html += `</div>`;
        });
        html += `</div>`;
    }
    
    // Summary
    if (results.tests_passed !== undefined) {
        const total = results.tests_passed + results.tests_failed;
        const percentage = total > 0 ? Math.round((results.tests_passed / total) * 100) : 0;
        html += `<div class="alert alert-info">`;
        html += `<strong>Score:</strong> ${results.tests_passed}/${total} tests passed (${percentage}%)`;
        html += `</div>`;
    }
    
    container.innerHTML = html;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

/**
 * Show loading spinner
 */
function showLoadingSpinner(button, spinnerElement) {
    if (button) button.disabled = true;
    if (spinnerElement) spinnerElement.style.display = 'inline';
}

/**
 * Hide loading spinner
 */
function hideLoadingSpinner(button, spinnerElement) {
    if (button) button.disabled = false;
    if (spinnerElement) spinnerElement.style.display = 'none';
}

/**
 * Format execution time
 */
function formatExecutionTime(ms) {
    if (ms < 1000) {
        return `${ms}ms`;
    }
    return `${(ms / 1000).toFixed(2)}s`;
}

/**
 * Copy code to clipboard
 */
function copyCodeToClipboard(code) {
    navigator.clipboard.writeText(code).then(() => {
        showNotification('Code copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy code:', err);
        showNotification('Failed to copy code', 'error');
    });
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Simple notification implementation
    // Can be replaced with a more sophisticated notification library
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializePythonEditor,
        submitPythonCode,
        displayExecutionResults,
        escapeHtml,
        showLoadingSpinner,
        hideLoadingSpinner,
        formatExecutionTime,
        copyCodeToClipboard,
        showNotification
    };
}
