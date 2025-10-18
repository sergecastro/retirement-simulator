"""
Streamlit Explain API - Bridge between frontend and Claude backend
Handles communication between JavaScript buttons and Python explanation handler
"""

import streamlit as st
import os
from dotenv import load_dotenv


def inject_explain_visual_system():
    """
    Inject the complete Explain Visual system into the Streamlit app.
    """

    # Get Flask API URL from environment/secrets (Railway URL for production, localhost for dev)
    api_url = os.getenv('FLASK_API_URL', 'http://localhost:8502')

    # If using Streamlit secrets, prefer that over environment variable
    if hasattr(st, 'secrets') and 'FLASK_API_URL' in st.secrets:
        api_url = st.secrets['FLASK_API_URL']

    # Create the HTML/JavaScript as a regular string
    html_code = f"""
    <script>
    function initExplainVisual() {
        if (window.parent.__EXPLAIN_VISUAL_LOADED__) return;
        window.parent.__EXPLAIN_VISUAL_LOADED__ = true;

        // console.log('[ExplainVisual] Initializing...');
        
        // CRITICAL: Add styles to PARENT document, not iframe
        const style = window.parent.document.createElement('style');
        style.textContent = `
            .ev-btn {
                position: fixed;
                z-index: 999999;
                padding: 20px 30px;
                border-radius: 999px;
                border: 5px solid black;
                background: red;
                color: white;
                font-weight: 700;
                font-size: 40px;
                cursor: pointer;
                box-shadow: 0 5px 15px rgba(0,0,0,0.5);
                transition: all 0.2s;
            }
            .ev-btn:hover {
                background: darkred;
                transform: scale(1.1);
            }
            .ev-modal-backdrop {
                position: fixed;
                inset: 0;
                background: rgba(0,0,0,0.5);
                z-index: 999998;
                display: none;
                align-items: center;
                justify-content: center;
            }
            .ev-modal {
                width: min(900px, 90vw);
                max-height: 85vh;
                overflow: auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                padding: 24px;
                position: relative;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                line-height: 1.6;
            }
            .ev-modal h2 {
                margin-top: 0;
                color: #1f2937;
                border-bottom: 2px solid #e5e7eb;
                padding-bottom: 8px;
            }
            .ev-modal ul {
                line-height: 1.8;
                margin: 12px 0;
            }
            .ev-modal strong {
                color: #1f2937;
            }
            .ev-close {
                position: absolute;
                top: 12px;
                right: 16px;
                font-size: 28px;
                cursor: pointer;
                color: #666;
                line-height: 1;
            }
            .ev-close:hover {
                color: #000;
            }
            .ev-loading {
                text-align: center;
                padding: 60px 40px;
                color: #666;
                font-size: 18px;
            }
        `;
        window.parent.document.head.appendChild(style);
        
        // Create modal in PARENT document
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
                '<div class="ev-loading">🧠 Claude is analyzing this chart...<br><br>This takes 2-3 seconds...</div>';
        }
        
        function showExplanation(html) {
            window.parent.document.getElementById('ev-modal-content').innerHTML = html;
            backdrop.style.display = 'flex';
        }
        
        function markdownToHTML(text) {
            let html = text;
            
            html = html.split('\\n').map(line => {
                if (line.startsWith('## ')) {
                    return '<h2>' + line.substring(3) + '</h2>';
                }
                return line;
            }).join('\\n');
            
            const boldParts = html.split('**');
            html = '';
            for (let i = 0; i < boldParts.length; i++) {
                if (i % 2 === 1) {
                    html += '<strong>' + boldParts[i] + '</strong>';
                } else {
                    html += boldParts[i];
                }
            }
            
            const lines = html.split('\\n');
            let inList = false;
            let result = '';
            
            for (let line of lines) {
                const trimmed = line.trim();
                if (trimmed.startsWith('•')) {
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
            
            result = result.split('\\n\\n').map(para => {
                if (!para.trim().startsWith('<')) {
                    return '<p>' + para.trim() + '</p>';
                }
                return para;
            }).join('\\n');
            
            return result;
        }
        
        function extractChartData(container) {
            const data = {
                chart_type: 'unknown',
                title: 'Chart',
                data: {}
            };

            // STEP 1: Extract title from nearby headers
            let titleEl = container.closest('div[data-testid="stVerticalBlock"]');
            if (titleEl) {
                const header = titleEl.querySelector('h1, h2, h3, [data-testid="stMarkdownContainer"] p strong, [data-testid="stMarkdownContainer"] p');
                if (header) data.title = header.textContent.trim();
            }

            // STEP 2: Check if this is a Plotly chart
            if (container.classList.contains('svg-container')) {
                data.chart_type = 'plotly';

                // STEP 3: Try to identify which specific chart this is by looking for Streamlit key
                let chartKey = null;

                // Look up the DOM tree for elements with data-test-id that contain our chart keys
                let parent = container;
                while (parent && parent !== window.parent.document.body) {
                    // Check for Streamlit's key in various attributes
                    const testId = parent.getAttribute('data-testid');
                    const key = parent.getAttribute('key');

                    if (testId || key) {
                        // Check if it matches our chart keys
                        if (testId && testId.includes('financial_trajectories')) {
                            chartKey = 'financial_trajectories';
                            break;
                        } else if (testId && testId.includes('monte_carlo')) {
                            chartKey = 'monte_carlo_simulation';
                            break;
                        } else if (testId && testId.includes('sankey')) {
                            chartKey = 'sankey_cash_flow';
                            break;
                        } else if (testId && testId.includes('irmaa_magi')) {
                            chartKey = 'irmaa_magi_trajectory';
                            break;
                        } else if (testId && testId.includes('irmaa_costs')) {
                            chartKey = 'irmaa_annual_costs';
                            break;
                        }
                    }
                    parent = parent.parentElement;
                }

                // STEP 4: Try to access the chart registry (injected by Python)
                // console.log('[ExplainVisual] Checking chart registry...');
                // console.log('[ExplainVisual] Registry exists:', !!window.parent.__CHART_DATA_REGISTRY__);
                // console.log('[ExplainVisual] Detected chart key:', chartKey);

                if (window.parent.__CHART_DATA_REGISTRY__) {
                    // console.log('[ExplainVisual] Registry keys:', Object.keys(window.parent.__CHART_DATA_REGISTRY__));

                    let matchedChart = null;

                    // First, try to match by detected chart key
                    if (chartKey && window.parent.__CHART_DATA_REGISTRY__[chartKey]) {
                        matchedChart = window.parent.__CHART_DATA_REGISTRY__[chartKey];
                        // console.log('[ExplainVisual] ✅ Matched by key:', chartKey);
                    }
                    // Try to match by position (order in which charts appear)
                    else {
                        // Get all chart containers on the page
                        const allCharts = Array.from(window.parent.document.querySelectorAll('.svg-container'));
                        const chartIndex = allCharts.indexOf(container);
                        const registryKeys = Object.keys(window.parent.__CHART_DATA_REGISTRY__);

                        if (chartIndex >= 0 && chartIndex < registryKeys.length) {
                            const keyByPosition = registryKeys[chartIndex];
                            matchedChart = window.parent.__CHART_DATA_REGISTRY__[keyByPosition];
                            // console.log('[ExplainVisual] ✅ Matched by position:', chartIndex, '→', keyByPosition);
                        }
                    }

                    if (matchedChart && matchedChart.data_summary) {
                        data.title = matchedChart.title || data.title;
                        data.data = matchedChart.data_summary;
                        // console.log('[ExplainVisual] ✅ Extracted chart data:', data.data);
                        return data;
                    }
                }

                // FALLBACK: Try to extract from Plotly DOM
                try {
                    const plotDiv = container.querySelector('.js-plotly-plot, .plotly');
                    if (plotDiv && plotDiv.data && plotDiv.layout) {
                        const traces = plotDiv.data;
                        data.data = {
                            num_traces: traces.length,
                            traces: traces.map(trace => ({
                                name: trace.name,
                                type: trace.type,
                                x_length: trace.x ? trace.x.length : 0,
                                y_min: trace.y ? Math.min(...trace.y) : null,
                                y_max: trace.y ? Math.max(...trace.y) : null,
                                y_avg: trace.y ? (trace.y.reduce((a,b) => a+b, 0) / trace.y.length) : null
                            }))
                        };
                        // console.log('[ExplainVisual] ✅ Extracted from Plotly DOM');
                        return data;
                    }
                } catch (e) {
                    // console.warn('[ExplainVisual] DOM extraction failed:', e);
                }

                // Final fallback
                data.data = {
                    chart_detected: true,
                    type: 'plotly_visualization',
                    note: 'Could not access chart data - registry not populated yet'
                };
            } else if (container.querySelector('[data-testid="stDataFrame"]')) {
                data.chart_type = 'table';
                data.data = { type: 'dataframe' };
            }

            return data;
        }
        
        function buildPrompt(chartData) {
            // Build a more detailed prompt based on whether we have actual trace data
            let dataDescription = '';

            if (chartData.data.traces && chartData.data.traces.length > 0) {
                // We have actual Plotly data!
                dataDescription = `**Data Traces:**\n`;
                chartData.data.traces.forEach((trace, idx) => {
                    dataDescription += `\nTrace ${idx + 1}: ${trace.name || 'Unnamed'}\n`;
                    dataDescription += `- Type: ${trace.type}\n`;
                    dataDescription += `- Data points: ${trace.x_length}\n`;
                    if (trace.y_min !== null && trace.y_max !== null) {
                        dataDescription += `- Range: $${trace.y_min.toLocaleString()} to $${trace.y_max.toLocaleString()}\n`;
                        dataDescription += `- Average: $${trace.y_avg.toLocaleString()}\n`;
                    }
                    if (trace.x_sample && trace.x_sample.length > 0) {
                        dataDescription += `- First few X values: ${trace.x_sample.join(', ')}\n`;
                    }
                    if (trace.y_sample && trace.y_sample.length > 0) {
                        dataDescription += `- First few Y values: ${trace.y_sample.map(v => '$' + v.toLocaleString()).join(', ')}\n`;
                    }
                });
            } else {
                dataDescription = `**Chart Data:** ${JSON.stringify(chartData.data, null, 2)}`;
            }

            return `You are helping explain a retirement planning visualization to a user.

**Chart Title:** ${chartData.title}

**Chart Type:** ${chartData.chart_type}

${dataDescription}

Please provide a clear, friendly explanation that:

1. **What it shows:** Explain what this specific visualization displays (2-3 sentences)
2. **Key insights:** Identify the most important numbers or patterns in THIS data (3-4 bullet points with ACTUAL numbers from the data)
3. **What it means:** Explain what these results mean for the user's retirement planning (2-3 sentences)
4. **Example interpretation:** Give one concrete example of how to read/interpret this chart using the actual data shown

Keep your tone warm and educational. Use plain English (avoid jargon). Focus on the SPECIFIC data provided, not generic explanations.

Format your response with clear sections using markdown headers (##) for readability.`;
        }
        
        async function getExplanation(chartData) {
            showLoading();

            try {
                const prompt = buildPrompt(chartData);
                // console.log('[ExplainVisual] Sending to Flask server:');
                // console.log('[ExplainVisual] Prompt length:', prompt.length, 'chars');
                // console.log('[ExplainVisual] Chart data summary:', {
                //     title: chartData.title,
                //     type: chartData.chart_type,
                //     has_traces: chartData.data.traces ? chartData.data.traces.length : 0
                // });

                // FIXED: Call our Python backend instead of Anthropic directly (fixes CORS!)
                // API URL configured from Python (Railway for production, localhost for dev)
                const response = await fetch('{api_url}/explain', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        prompt: prompt
                    }})
                }});
                
                if (!response.ok) {
                    throw new Error('Backend request failed: ' + response.status);
                }
                
                const result = await response.json();
                const explanation = result.explanation;
                
                const html = markdownToHTML(explanation);
                
                showExplanation(html);
            }} catch (error) {{
                console.error('[ExplainVisual] Error:', error);
                showExplanation('<h2>Error</h2><p>Could not get explanation: ' + error.message + '</p><p>Make sure the Flask API server is running at: {api_url}</p>');
            }}
        }
        
        function placeButtons() {
            // Remove old buttons from PARENT document
            window.parent.document.querySelectorAll('.ev-btn').forEach(btn => btn.remove());
            
            // Find charts in PARENT document
            const charts = window.parent.document.querySelectorAll('.svg-container, [data-testid="stDataFrame"]');
            
            charts.forEach(chart => {
                const rect = chart.getBoundingClientRect();
                
                // Skip tiny charts
                if (rect.width < 200 || rect.height < 150) return;
                
                // Create button
                const btn = window.parent.document.createElement('button');
                btn.className = 'ev-btn';
                btn.textContent = '?';
                
                // Use FIXED positioning with viewport coordinates
                btn.style.top = (rect.top + 10) + 'px';
                btn.style.left = (rect.right - 100) + 'px';
                
                btn.onclick = () => {
                    const data = extractChartData(chart);
                    // console.log('[ExplainVisual] Button clicked - Extracted data:', JSON.stringify(data, null, 2));
                    getExplanation(data);
                };
                
                window.parent.document.body.appendChild(btn);
            });

            // console.log('[ExplainVisual] Placed', charts.length, 'buttons');

            return charts.length; // Return count for polling
        }

        // FIXED: Active polling instead of relying on MutationObserver
        let pollAttempts = 0;
        const maxPollAttempts = 100; // 100 attempts × 300ms = 30 seconds max

        function pollForCharts() {
            pollAttempts++;
            const chartsFound = placeButtons();

            if (chartsFound > 0) {
                // console.log('[ExplainVisual] ✅ Charts detected! Buttons placed after', pollAttempts * 300, 'ms');
                return; // Stop polling once charts are found
            }

            if (pollAttempts < maxPollAttempts) {
                setTimeout(pollForCharts, 300); // Check again in 300ms
            } else {
                // console.log('[ExplainVisual] ⚠️ No charts found after 30 seconds');
            }
        }
        
        // Start polling immediately
        pollForCharts();
        
        // Re-place on scroll (in parent window)
        window.parent.addEventListener('scroll', () => {
            placeButtons();
        });
        
        window.parent.addEventListener('resize', placeButtons);
        
        // Keep MutationObserver for dynamic updates (new charts appearing later)
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
    
    # Inject into Streamlit
    st.components.v1.html(html_code, height=0)