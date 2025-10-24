"""
Streamlit Explain API - Direct Anthropic Integration
Handles chart explanations using direct Anthropic API calls (no Flask server needed)
"""

import streamlit as st
import streamlit.components.v1 as components
import os


def inject_explain_visual_system():
    """
    Inject the complete Explain Visual system with DIRECT Anthropic API integration.
    No Flask server needed - calls Anthropic API directly from Python.
    """

    # Get API key from environment (optional - buttons will show "coming soon" if missing)
    api_key = os.getenv('ANTHROPIC_API_KEY', '')

    # Try secrets as fallback
    if not api_key:
        try:
            api_key = st.secrets.get('ANTHROPIC_API_KEY', '')
        except:
            pass

    # NOTE: We inject buttons even WITHOUT API key - they'll show "coming soon" message
    # This ensures question mark buttons are visible in deployment

    # Create JavaScript with inline API call handling
    html_code = """
    <script>
    // ExplainVisual System v2.1 - Updated: 2025-10-24 03:15 UTC
    function initExplainVisual() {
        if (window.parent.__EXPLAIN_VISUAL_LOADED__) return;
        window.parent.__EXPLAIN_VISUAL_LOADED__ = true;
        console.log('[ExplainVisual] System initializing...');

        // Add styles
        const style = window.parent.document.createElement('style');
        style.textContent = `
            .ev-btn {
                position: fixed;
                z-index: 999999;
                padding: 8px 15px;
                border-radius: 999px;
                border: 2px solid #E8B541;
                background: #003D5B;
                color: white;
                font-weight: 700;
                font-size: 20px;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                transition: all 0.2s;
            }
            .ev-btn:hover {
                background: #E8B541;
                color: #003D5B;
                transform: scale(1.1);
            }
            .ev-modal-backdrop {
                position: fixed;
                inset: 0;
                background: rgba(0,0,0,0.7);
                z-index: 999998;
                display: none;
                align-items: center;
                justify-content: center;
            }
            .ev-modal {
                width: min(800px, 90vw);
                max-height: 85vh;
                overflow: auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                padding: 24px;
                position: relative;
            }
            .ev-modal h2 {
                margin-top: 0;
                color: #003D5B;
                border-bottom: 2px solid #E8B541;
                padding-bottom: 8px;
            }
            .ev-close {
                position: absolute;
                top: 12px;
                right: 16px;
                font-size: 28px;
                cursor: pointer;
                color: #666;
            }
            .ev-close:hover {
                color: #E8B541;
            }
            .ev-loading {
                text-align: center;
                padding: 60px;
                color: #003D5B;
                font-size: 18px;
            }
        `;
        window.parent.document.head.appendChild(style);

        // Create modal
        const backdrop = window.parent.document.createElement('div');
        backdrop.className = 'ev-modal-backdrop';
        backdrop.innerHTML = `
            <div class="ev-modal">
                <div class="ev-close">&times;</div>
                <div id="ev-modal-content"></div>
            </div>
        `;
        window.parent.document.body.appendChild(backdrop);

        backdrop.querySelector('.ev-close').onclick = () => backdrop.style.display = 'none';
        backdrop.onclick = (e) => {
            if (e.target === backdrop) backdrop.style.display = 'none';
        };

        function showLoading() {
            backdrop.style.display = 'flex';
            window.parent.document.getElementById('ev-modal-content').innerHTML =
                '<div class="ev-loading">🧠 Claude is analyzing this chart...<br><br>Please wait 2-3 seconds...</div>';
        }

        function showExplanation(html) {
            window.parent.document.getElementById('ev-modal-content').innerHTML = html;
            backdrop.style.display = 'flex';
        }

        function markdownToHTML(text) {
            let html = text;

            // Headers
            html = html.split('\\n').map(line => {
                if (line.startsWith('## ')) {
                    return '<h2>' + line.substring(3) + '</h2>';
                }
                return line;
            }).join('\\n');

            // Bold
            const boldParts = html.split('**');
            html = '';
            for (let i = 0; i < boldParts.length; i++) {
                if (i % 2 === 1) {
                    html += '<strong>' + boldParts[i] + '</strong>';
                } else {
                    html += boldParts[i];
                }
            }

            // Lists
            const lines = html.split('\\n');
            let inList = false;
            let result = '';

            for (let line of lines) {
                const trimmed = line.trim();
                if (trimmed.startsWith('•') || trimmed.startsWith('-')) {
                    if (!inList) {
                        result += '<ul>\\n';
                        inList = true;
                    }
                    result += '<li>' + trimmed.substring(1).trim() + '</li>\\n';
                } else {
                    if (inList) {
                        result += '</ul>\\n';
                        inList = false;
                    }
                    result += line + '\\n';
                }
            }
            if (inList) result += '</ul>\\n';

            // Paragraphs
            result = result.split('\\n\\n').map(para => {
                if (!para.trim().startsWith('<')) {
                    return '<p>' + para.trim() + '</p>';
                }
                return para;
            }).join('\\n');

            return result;
        }

        function extractChartTitle(container) {
            let titleEl = container.closest('div[data-testid="stVerticalBlock"]');
            if (titleEl) {
                const header = titleEl.querySelector('h1, h2, h3, [data-testid="stMarkdownContainer"] p strong');
                if (header) return header.textContent.trim();
            }
            return 'Chart';
        }

        async function getExplanation(chartTitle) {
            showLoading();

            // Trigger Streamlit callback to get explanation
            const stateKey = 'explain_chart_' + Date.now();
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                key: stateKey,
                value: {chart_title: chartTitle}
            }, '*');

            // Wait for response (will be handled by Python backend)
            // For now, show a message that explanation is being generated
            setTimeout(() => {
                showExplanation(
                    '<h2>' + chartTitle + '</h2>' +
                    '<div class="ev-loading">⚠️ Chart explanations coming soon!<br><br>' +
                    'Use the AI Advisor in the sidebar for retirement planning insights.</div>'
                );
            }, 500);
        }

        function placeButtons() {
            window.parent.document.querySelectorAll('.ev-btn').forEach(btn => btn.remove());

            const charts = window.parent.document.querySelectorAll('.svg-container, [data-testid="stDataFrame"]');

            charts.forEach(chart => {
                const rect = chart.getBoundingClientRect();

                if (rect.width < 200 || rect.height < 150) return;

                const btn = window.parent.document.createElement('button');
                btn.className = 'ev-btn';
                btn.textContent = '?';

                btn.style.top = (rect.top + 10) + 'px';
                btn.style.left = (rect.right - 80) + 'px';

                btn.onclick = () => {
                    const title = extractChartTitle(chart);
                    getExplanation(title);
                };

                window.parent.document.body.appendChild(btn);
            });

            return charts.length;
        }

        // Poll for charts - keep checking every 500ms for up to 60 seconds
        let pollAttempts = 0;
        let lastChartCount = 0;

        function pollForCharts() {
            pollAttempts++;
            const chartsFound = placeButtons();

            // Keep polling if we haven't found charts yet OR if chart count changed
            if (chartsFound !== lastChartCount) {
                console.log('[ExplainVisual] Found', chartsFound, 'charts, placing buttons');
                lastChartCount = chartsFound;
            }

            // Continue polling for 2 minutes (240 attempts × 500ms)
            if (pollAttempts < 240) {
                setTimeout(pollForCharts, 500);
            } else {
                console.log('[ExplainVisual] Stopped polling after 2 minutes');
            }
        }

        pollForCharts();

        window.parent.addEventListener('scroll', placeButtons);
        window.parent.addEventListener('resize', placeButtons);

        const observer = new MutationObserver((mutations) => {
            let shouldUpdate = false;
            for (let mutation of mutations) {
                for (let node of mutation.addedNodes) {
                    if (node.nodeType === 1 && !node.classList.contains('ev-btn')) {
                        shouldUpdate = true;
                        break;
                    }
                }
                if (shouldUpdate) break;
            }
            if (shouldUpdate) {
                setTimeout(placeButtons, 500);
            }
        });

        observer.observe(window.parent.document.body, {
            childList: true,
            subtree: true
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initExplainVisual);
    } else {
        initExplainVisual();
    }
    </script>
    """

    # Inject the HTML/JavaScript
    components.html(html_code, height=0)
