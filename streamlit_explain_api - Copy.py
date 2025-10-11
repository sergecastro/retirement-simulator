"""
Streamlit Explain API - Bridge between frontend and Claude backend
Handles communication between JavaScript buttons and Python explanation handler
"""

import streamlit as st
import json
from explain_visual_handler import get_chart_explanation


def initialize_explain_visual():
    """
    Initialize session state for explain visual feature.
    Call this once at the start of your app.
    """
    if "explain_visual_request" not in st.session_state:
        st.session_state.explain_visual_request = None
    if "explain_visual_response" not in st.session_state:
        st.session_state.explain_visual_response = None


def inject_explain_visual_system():
    """
    Inject the complete Explain Visual system into the Streamlit app.
    This includes:
    - CSS styles for buttons and modal
    - JavaScript for button placement and interaction
    - Communication bridge to Python backend
    """
    
    # JavaScript + HTML component
    explain_visual_html = """
    <script>
    (function() {
        // Prevent multiple injections
        if (window.__EXPLAIN_VISUAL_LOADED__) return;
        window.__EXPLAIN_VISUAL_LOADED__ = true;
        
        console.log('[ExplainVisual] Initializing...');
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .ev-btn {
                position: absolute;
                z-index: 999999;
                padding: 8px 14px;
                border-radius: 999px;
                border: 2px solid rgba(0,0,0,0.2);
                background: #4CAF50;
                color: white;
                font-weight: 700;
                font-size: 16px;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.25);
                transition: all 0.2s;
            }
            .ev-btn:hover {
                background: #45a049;
                transform: scale(1.05);
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
            }
            .ev-modal h2 {
                margin-top: 0;
                color: #1f2937;
            }
            .ev-modal ul {
                line-height: 1.6;
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
                color: #000;
            }
            .ev-loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
        `;
        document.head.appendChild(style);
        
        // Create modal
        const backdrop = document.createElement('div');
        backdrop.className = 'ev-modal-backdrop';
        backdrop.innerHTML = `
            <div class="ev-modal">
                <div class="ev-close">&times;</div>
                <div id="ev-modal-content"></div>
            </div>
        `;
        document.body.appendChild(backdrop);
        
        // Close modal handlers
        backdrop.querySelector('.ev-close').onclick = () => backdrop.style.display = 'none';
        backdrop.onclick = (e) => {
            if (e.target === backdrop) backdrop.style.display = 'none';
        };
        
        // Function to show loading
        function showLoading() {
            backdrop.style.display = 'flex';
            document.getElementById('ev-modal-content').innerHTML = 
                '<div class="ev-loading">🧠 Claude is analyzing this chart...<br><br>This takes 2-3 seconds...</div>';
        }
        
        // Function to show explanation
        function showExplanation(html) {
            document.getElementById('ev-modal-content').innerHTML = html;
            backdrop.style.display = 'flex';
        }
        
        // Function to extract chart data
        function extractChartData(container) {
            const data = {
                chart_type: 'unknown',
                title: 'Chart',
                data: {}
            };
            
            // Get title
            let titleEl = container.closest('div[data-testid="stVerticalBlock"]');
            if (titleEl) {
                const header = titleEl.querySelector('h1, h2, h3, [data-testid="stMarkdownContainer"] p');
                if (header) data.title = header.textContent.trim();
            }
            
            // Detect chart type and extract data
            if (container.classList.contains('js-plotly-plot')) {
                data.chart_type = 'plotly';
                try {
                    const plotlyData = container.data;
                    if (plotlyData && plotlyData.length > 0) {
                        data.data = {
                            traces: plotlyData.length,
                            trace_types: plotlyData.map(t => t.type),
                            sample_values: plotlyData[0].y ? plotlyData[0].y.slice(0, 10) : []
                        };
                    }
                } catch (e) {
                    console.log('[ExplainVisual] Could not extract Plotly data:', e);
                }
            } else if (container.querySelector('[data-testid="stDataFrame"]')) {
                data.chart_type = 'table';
                data.data = { type: 'dataframe' };
            }
            
            return data;
        }
        
        // Function to call Python backend
        async function getExplanation(chartData) {
            showLoading();
            
            // Store request in Streamlit session state
            const stateKey = 'explain_visual_request_' + Date.now();
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                key: stateKey,
                value: JSON.stringify(chartData)
            }, '*');
            
            // Use the Python handler directly via Streamlit
            // In practice, we'll use a simpler direct API call
            try {
                const response = await fetch('https://api.anthropic.com/v1/messages', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'anthropic-version': '2023-06-01',
                        'x-api-key': window.__ANTHROPIC_KEY__
                    },
                    body: JSON.stringify({
                        model: 'claude-sonnet-4-20250514',
                        max_tokens: 1500,
                        messages: [{
                            role: 'user',
                            content: buildPrompt(chartData)
                        }]
                    })
                });
                
                const result = await response.json();
                const explanation = result.content[0].text;
                
                // Convert markdown to HTML (simple version)
                const html = explanation
                    .replace(/## (.+)/g, '<h2>$1</h2>')
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/• (.+)/g, '<li>$1</li>')
                    .replace(/<li>/g, '<ul><li>')
                    .replace(/<\/li>\n<li>/g, '</li><li>')
                    .replace(/<\/li>\n/g, '</li></ul>\n');
                
                showExplanation(html);
            } catch (error) {
                showExplanation('<h2>Error</h2><p>Could not get explanation: ' + error.message + '</p>');
            }
        }
        
        function buildPrompt(chartData) {
            return `You are helping explain a retirement planning visualization to a user.

**Chart Title:** ${chartData.title}

**Chart Type:** ${chartData.chart_type}

**Chart Data:** ${JSON.stringify(chartData.data, null, 2)}

Please provide a clear, friendly explanation that:

1. **What it shows:** Explain what this specific visualization displays (2-3 sentences)
2. **Key insights:** Identify the most important numbers or patterns in THIS data (3-4 bullet points)
3. **What it means:** Explain what these results mean for the user's retirement planning (2-3 sentences)
4. **Example interpretation:** Give one concrete example of how to read/interpret this chart using the actual data shown

Keep your tone warm and educational. Use plain English (avoid jargon). Focus on the SPECIFIC data provided, not generic explanations.

Format your response with clear sections using markdown headers (##) for readability.`;
        }
        
        // Function to place buttons
        function placeButtons() {
            // Remove old buttons
            document.querySelectorAll('.ev-btn').forEach(btn => btn.remove());
            
            // Find all charts
            const charts = document.querySelectorAll('.js-plotly-plot, [data-testid="stDataFrame"]');
            
            charts.forEach(chart => {
                const rect = chart.getBoundingClientRect();
                if (rect.width < 200 || rect.height < 150) return;
                
                const btn = document.createElement('button');
                btn.className = 'ev-btn';
                btn.textContent = '?';
                btn.style.top = (rect.top + window.scrollY + 10) + 'px';
                btn.style.left = (rect.right + window.scrollX - 50) + 'px';
                
                btn.onclick = () => {
                    const data = extractChartData(chart);
                    getExplanation(data);
                };
                
                document.body.appendChild(btn);
            });
            
            console.log('[ExplainVisual] Placed', charts.length, 'buttons');
        }
        
        // Initial placement
        setTimeout(placeButtons, 1000);
        
        // Re-place on scroll/resize
        window.addEventListener('scroll', placeButtons);
        window.addEventListener('resize', placeButtons);
        
        // Watch for Streamlit updates
        const observer = new MutationObserver(() => {
            setTimeout(placeButtons, 500);
        });
        observer.observe(document.body, { childList: true, subtree: true });
        
    })();
    </script>
    """
    
    # Inject with API key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Add API key to JavaScript
    full_html = f"""
    <script>
    window.__ANTHROPIC_KEY__ = '{api_key}';
    </script>
    """ + explain_visual_html
    
    # Inject into Streamlit
    st.components.v1.html(full_html, height=0)