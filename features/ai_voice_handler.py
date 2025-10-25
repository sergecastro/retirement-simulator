# features/ai_voice_handler.py
"""
AI Voice Handler - Text-to-Speech for ForeCash AI Advisor
Uses browser's built-in TTS (works on desktop and mobile)
"""

import streamlit as st
import streamlit.components.v1 as components

def create_voice_player(text: str, button_key: str = "read_aloud"):
    """
    Creates a Read Aloud button with voice controls

    Args:
        text: The text to read aloud
        button_key: Unique key for the button
    """

    # Clean text for speech (remove markdown, special chars)
    clean_text = text.replace('**', '').replace('*', '').replace('#', '')
    clean_text = clean_text.replace('\n', ' ').replace('  ', ' ')

    # Escape text for JavaScript
    clean_text = clean_text.replace("'", "\\'").replace('"', '\\"')

    # HTML + JavaScript for voice player
    voice_html = f"""
    <div style="margin: 15px 0; padding: 10px; background-color: #f0f2f6; border-radius: 8px;">
        <button id="play_{button_key}"
                onclick="speakText_{button_key}()"
                style="background-color: #003D5B; color: white; border: none; padding: 12px 24px;
                       border-radius: 6px; cursor: pointer; font-size: 16px; margin-right: 10px;">
            🔊 Read Aloud
        </button>

        <button id="pause_{button_key}"
                onclick="pauseSpeech_{button_key}()"
                style="background-color: #666; color: white; border: none; padding: 12px 20px;
                       border-radius: 6px; cursor: pointer; font-size: 16px; margin-right: 10px; display: none;">
            ⏸️ Pause
        </button>

        <button id="stop_{button_key}"
                onclick="stopSpeech_{button_key}()"
                style="background-color: #cc0000; color: white; border: none; padding: 12px 20px;
                       border-radius: 6px; cursor: pointer; font-size: 16px; display: none;">
            ⏹️ Stop
        </button>

        <div id="status_{button_key}" style="margin-top: 10px; font-size: 14px; color: #003D5B;"></div>
    </div>

    <script>
        var utterance_{button_key} = null;
        var isPaused_{button_key} = false;

        function speakText_{button_key}() {{
            // Stop any existing speech
            if (utterance_{button_key}) {{
                window.speechSynthesis.cancel();
            }}

            // Create new utterance
            utterance_{button_key} = new SpeechSynthesisUtterance("{clean_text}");

            // Voice settings - male, professional
            var voices = window.speechSynthesis.getVoices();
            var maleVoice = voices.find(voice =>
                voice.name.includes('Male') ||
                voice.name.includes('David') ||
                voice.name.includes('Daniel') ||
                voice.name.includes('Google US English Male')
            );

            if (maleVoice) {{
                utterance_{button_key}.voice = maleVoice;
            }}

            utterance_{button_key}.rate = 0.9;  // Slightly slower for financial content
            utterance_{button_key}.pitch = 1.0;
            utterance_{button_key}.volume = 1.0;

            // Event handlers
            utterance_{button_key}.onstart = function() {{
                document.getElementById('play_{button_key}').style.display = 'none';
                document.getElementById('pause_{button_key}').style.display = 'inline-block';
                document.getElementById('stop_{button_key}').style.display = 'inline-block';
                document.getElementById('status_{button_key}').innerText = '🎤 Speaking...';
            }};

            utterance_{button_key}.onend = function() {{
                document.getElementById('play_{button_key}').style.display = 'inline-block';
                document.getElementById('pause_{button_key}').style.display = 'none';
                document.getElementById('stop_{button_key}').style.display = 'none';
                document.getElementById('status_{button_key}').innerText = '✅ Finished';
                isPaused_{button_key} = false;
            }};

            utterance_{button_key}.onerror = function(e) {{
                document.getElementById('status_{button_key}').innerText = '❌ Error: ' + e.error;
                document.getElementById('play_{button_key}').style.display = 'inline-block';
                document.getElementById('pause_{button_key}').style.display = 'none';
                document.getElementById('stop_{button_key}').style.display = 'none';
            }};

            // Speak!
            window.speechSynthesis.speak(utterance_{button_key});
            isPaused_{button_key} = false;
        }}

        function pauseSpeech_{button_key}() {{
            if (window.speechSynthesis.speaking && !isPaused_{button_key}) {{
                window.speechSynthesis.pause();
                isPaused_{button_key} = true;
                document.getElementById('pause_{button_key}').innerText = '▶️ Resume';
                document.getElementById('status_{button_key}').innerText = '⏸️ Paused';
            }} else if (isPaused_{button_key}) {{
                window.speechSynthesis.resume();
                isPaused_{button_key} = false;
                document.getElementById('pause_{button_key}').innerText = '⏸️ Pause';
                document.getElementById('status_{button_key}').innerText = '🎤 Speaking...';
            }}
        }}

        function stopSpeech_{button_key}() {{
            window.speechSynthesis.cancel();
            document.getElementById('play_{button_key}').style.display = 'inline-block';
            document.getElementById('pause_{button_key}').style.display = 'none';
            document.getElementById('stop_{button_key}').style.display = 'none';
            document.getElementById('status_{button_key}').innerText = '⏹️ Stopped';
            isPaused_{button_key} = false;
        }}

        // Load voices when available
        window.speechSynthesis.onvoiceschanged = function() {{
            // Voices loaded
        }};
    </script>
    """

    # Render the voice player
    components.html(voice_html, height=120)


def test_voice():
    """Quick test function"""
    st.title("🎤 Voice Test")

    test_text = "Hello! This is ForeCash AI advisor. Based on your retirement savings of eight hundred thousand dollars, your projected annual expenses of seventy-five thousand dollars, and your planned retirement age of sixty-five, our Monte Carlo analysis shows a ninety-two percent success rate."

    st.write("**Test Text:**")
    st.write(test_text)

    create_voice_player(test_text, "test_voice")


if __name__ == "__main__":
    test_voice()
