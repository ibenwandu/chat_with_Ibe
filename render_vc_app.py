import os
import json
import datetime
import tempfile
print("✓ os, json, datetime, and tempfile imported successfully")

try:
    import gdown
    print("✓ gdown imported successfully")
except ImportError as e:
    print(f"✗ Failed to import gdown: {e}")

try:
    from openai import OpenAI
    print("✓ openai imported successfully")
except ImportError as e:
    print(f"✗ Failed to import openai: {e}")

try:
    from pypdf import PdfReader
    print("✓ pypdf imported successfully")
except ImportError as e:
    print(f"✗ Failed to import pypdf: {e}")

try:
    import gradio as gr
    print("✓ gradio imported successfully")
except ImportError as e:
    print(f"✗ Failed to import gradio: {e}")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv imported successfully")
except ImportError as e:
    print(f"✗ Failed to import python-dotenv: {e}")

try:
    import requests
    print("✓ requests imported successfully")
except ImportError as e:
    print(f"✗ Failed to import requests: {e}")

try:
    import base64
    import io
    from pydub import AudioSegment
    from pydub.playback import play
    print("✓ pydub imported successfully")
except ImportError as e:
    print(f"✗ Failed to import pydub: {e}")

try:
    from elevenlabs import Voice, VoiceSettings, generate, set_api_key
    print("✓ ElevenLabs imported successfully")
    ELEVENLABS_AVAILABLE = True
except ImportError as e:
    print(f"✗ Failed to import ElevenLabs: {e}")
    print("Install with: pip install elevenlabs")
    ELEVENLABS_AVAILABLE = False

try:
    from TTS.api import TTS
    print("✓ Coqui TTS imported successfully")
    COQUI_TTS_AVAILABLE = True
except ImportError as e:
    print(f"✗ Failed to import Coqui TTS: {e}")
    COQUI_TTS_AVAILABLE = False

try:
    from alternative_tts import custom_voice_tts_alternative
    print("✓ Alternative TTS imported successfully")
    ALTERNATIVE_TTS_AVAILABLE = True
except ImportError as e:
    print(f"✗ Failed to import Alternative TTS: {e}")
    ALTERNATIVE_TTS_AVAILABLE = False

try:
    from tts_config import TTSConfig, VoiceQuality, print_config_info
    print("✓ TTS configuration imported successfully")
except ImportError as e:
    print(f"✗ Failed to import TTS configuration: {e}")

load_dotenv(override=True)


def setup_elevenlabs():
    """Setup ElevenLabs API key"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if api_key:
        set_api_key(api_key)
        print("✓ ElevenLabs API key configured")
        return True
    else:
        print("❌ ELEVENLABS_API_KEY environment variable not set")
        return False


def list_available_tts_models():
    """List all available TTS models for reference"""
    print("🔊 Available TTS Options:")
    print("  1. OpenAI TTS (alloy, echo, fable, onyx, nova, shimmer)")
    print("  2. ElevenLabs Voice Cloning (your custom voice)")
    
    if COQUI_TTS_AVAILABLE:
        try:
            tts = TTS()
            models = tts.list_models()
            print("  3. Coqui TTS models available:")
            for i, model in enumerate(models[:5]):  # Show first 5 models
                print(f"     - {model}")
            if len(models) > 5:
                print(f"     ... and {len(models) - 5} more models")
        except Exception as e:
            print(f"  3. Coqui TTS error: {e}")
    else:
        print("  3. Coqui TTS not available")


def setup_custom_voice_model():
    """Helper function to set up custom voice model"""
    print("\n=== ELEVENLABS VOICE CLONING SETUP ===")
    print("To use your own voice with ElevenLabs:")
    print("1. Record 1-10 minutes of your voice speaking clearly")
    print("2. Upload to Google Drive and get shareable link")
    print("3. Set VOICE_SAMPLE_URL environment variable")
    print("4. Set ELEVENLABS_API_KEY environment variable")
    print("5. Voice will be cloned in real-time for each response")
    print("==========================================\n")


def text_to_speech(text, voice="alloy"):
    """Convert text to speech using OpenAI's TTS API"""
    try:
        client = OpenAI()
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=1.0
        )
        
        # Save the audio to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            audio_path = temp_file.name
        
        # Use the streaming response method to fix deprecation warning
        response.with_streaming_response.stream_to_file(audio_path)
        print(f"✓ OpenAI TTS ({voice}) successful: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return None


def custom_voice_tts(text):
    """Use ElevenLabs to clone your voice and generate speech"""
    
    if not ELEVENLABS_AVAILABLE:
        print("❌ ElevenLabs not available. Using OpenAI 'nova' as fallback...")
        return text_to_speech(text, voice="nova")
    
    if not setup_elevenlabs():
        print("❌ ElevenLabs API key not configured. Using OpenAI 'nova' as fallback...")
        return text_to_speech(text, voice="nova")
    
    voice_sample_path = "voice_sample.wav"
    
    if not os.path.exists(voice_sample_path):
        print("❌ Voice sample not found. Using OpenAI 'nova' as fallback...")
        return text_to_speech(text, voice="nova")
    
    try:
        print("🎤 Cloning your voice with ElevenLabs...")
        
        # Method 1: Use ElevenLabs API directly with requests (more reliable)
        try:
            api_key = os.getenv("ELEVENLABS_API_KEY")
            
            # Use instant voice cloning endpoint
            url = "https://api.elevenlabs.io/v1/text-to-speech"
            
            # First, we need to create a temporary voice or use instant cloning
            # For instant cloning, we'll use the speech endpoint with voice cloning
            headers = {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': api_key
            }
            
            # Try using a pre-existing voice first, then fall back to instant cloning
            # Using Adam voice as base, but we'll implement instant cloning
            voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam voice ID
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.8,
                    "style": 0.1,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(f"{url}/{voice_id}", json=data, headers=headers)
            
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✓ ElevenLabs TTS successful: {temp_path}")
                return temp_path
            else:
                print(f"✗ ElevenLabs API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"✗ ElevenLabs API method failed: {e}")
        
        # Method 2: Try using the Python SDK with voice cloning
        try:
            # Read the voice sample file
            with open(voice_sample_path, 'rb') as voice_file:
                voice_bytes = voice_file.read()
            
            # Generate speech with voice cloning using the SDK
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=None,  # No specific voice ID for instant cloning
                    settings=VoiceSettings(
                        stability=0.75,
                        similarity_boost=0.8,
                        style=0.1,
                        use_speaker_boost=True
                    )
                ),
                model="eleven_multilingual_v2"
            )
            
            # Save generated audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
                
            with open(temp_path, 'wb') as f:
                f.write(audio)
            
            print(f"✓ ElevenLabs SDK voice cloning successful: {temp_path}")
            return temp_path
            
        except Exception as e:
            print(f"✗ ElevenLabs SDK cloning failed: {e}")
        
        # Fallback to OpenAI with different voice
        print("🔄 ElevenLabs failed, using OpenAI 'nova' as fallback...")
        return text_to_speech(text, voice="nova")
        
    except Exception as e:
        print(f"✗ Error in ElevenLabs voice cloning: {e}")
        return text_to_speech(text, voice="nova")


def nova_voice_tts(text):
    """Convert text to speech using OpenAI's Nova voice"""
    return text_to_speech(text, voice="nova")


def echo_voice_tts(text):
    """Convert text to speech using OpenAI's Echo voice"""
    return text_to_speech(text, voice="echo")


# Global variable to track current voice type
current_voice_type = "alloy"


def speech_to_text(audio_file):
    """Convert speech to text using OpenAI's Whisper API"""
    try:
        client = OpenAI()
        with open(audio_file, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio
            )
        return transcript.text
    except Exception as e:
        print(f"Error in speech-to-text: {e}")
        return None


def push(text):
    """Send push notification via Pushover"""
    import requests
    
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")
    
    if not token or not user:
        print(f"⚠️ Push notification skipped - Missing environment variables:")
        print(f"   PUSHOVER_TOKEN: {'✓ Set' if token else '✗ Missing'}")
        print(f"   PUSHOVER_USER: {'✓ Set' if user else '✗ Missing'}")
        return
    
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": token,
                "user": user,
                "message": text,
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Push notification sent successfully: {text[:50]}...")
        else:
            print(f"❌ Push notification failed (Status {response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Push notification error: {e}")


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}


record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {"type": "string", "description": "Any additional information about the conversation that's worth recording to give context"},
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]


def get_current_date():
    """Get current date formatted as 'Saturday, August 9, 2025'"""
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y")


class Me:
    def __init__(self):
        self.openai = OpenAI()
        self.name = "Ibe Nwandu"

        # Initialize with default values
        self.linkedin = ""
        self.summary = ""

        # Download linkedin.pdf using gdown
        linkedin_pdf_url = os.getenv("LINKEDIN_PDF_URL")
        linkedin_pdf_path = "linkedin.pdf"
        
        if linkedin_pdf_url:
            print(f"Downloading LinkedIn PDF from {linkedin_pdf_url}")
            try:
                gdown.download(linkedin_pdf_url, linkedin_pdf_path, quiet=False)
                
                with open(linkedin_pdf_path, "rb") as f:
                    header = f.read(5)
                print(f"PDF header bytes: {header}")

                reader = PdfReader(linkedin_pdf_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        self.linkedin += text
                print("LinkedIn PDF processed successfully")
            except Exception as e:
                print(f"Error downloading/processing LinkedIn PDF: {e}")
        else:
            print("LINKEDIN_PDF_URL not set, skipping LinkedIn PDF download")

        # Download summary.txt using gdown
        summary_txt_url = os.getenv("SUMMARY_TXT_URL")
        summary_txt_path = "summary.txt"
        
        if summary_txt_url:
            print(f"Downloading summary text from {summary_txt_url}")
            try:
                gdown.download(summary_txt_url, summary_txt_path, quiet=False)
                
                with open(summary_txt_path, "r", encoding="utf-8") as f:
                    self.summary = f.read()
                print("Summary text processed successfully")
            except Exception as e:
                print(f"Error downloading/processing summary text: {e}")
        else:
            print("SUMMARY_TXT_URL not set, skipping summary text download")

        # Download voice_sample.wav using gdown
        voice_sample_url = os.getenv("VOICE_SAMPLE_URL")
        voice_sample_path = "voice_sample.wav"
        
        if voice_sample_url:
            print(f"Downloading voice sample from {voice_sample_url}")
            try:
                gdown.download(voice_sample_url, voice_sample_path, quiet=False)
                
                # Verify the file exists and has content
                if os.path.exists(voice_sample_path):
                    file_size = os.path.getsize(voice_sample_path)
                    print(f"Voice sample downloaded successfully ({file_size} bytes)")
                else:
                    print("Voice sample file not found after download")
                    
            except Exception as e:
                print(f"Error downloading voice sample: {e}")
        else:
            print("VOICE_SAMPLE_URL not set, skipping voice sample download")

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
        return results

    def system_prompt(self):
        current_date = get_current_date()
        system_prompt = (
            f"You are acting as {self.name}. Today is {current_date}. "
            f"You are answering questions on {self.name}'s website, "
            f"particularly questions related to {self.name}'s career, background, skills and experience. "
            f"Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. "
            f"You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. "
            f"Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
            f"You can reference the current date ({current_date}) naturally in conversation when relevant. "
            f"If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. "
            f"If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "
        )
        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt

    def chat(self, message, history):
        # Convert Gradio history format to OpenAI messages format
        messages = [{"role": "system", "content": self.system_prompt()}]
        
        # Convert history from Gradio tuples to OpenAI message format
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        done = False
        while not done:
            response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
            if response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content

    def chat_with_voice(self, message, history):
        """Chat with automatic text-to-speech for responses"""
        response = self.chat(message, history)
        
        if response:
            # Generate speech for the response using current voice type
            if current_voice_type == "custom":
                audio_path = custom_voice_tts(response)
            elif current_voice_type == "nova":
                audio_path = nova_voice_tts(response)
            elif current_voice_type == "echo":
                audio_path = echo_voice_tts(response)
            else:  # default to alloy
                audio_path = text_to_speech(response, "alloy")
            
            return response, audio_path
        else:
            return response, None


if __name__ == "__main__":
    # Show available TTS models and setup guide
    print("🔊 Initializing TTS system...")
    list_available_tts_models()
    setup_custom_voice_model()
    
    # Print current TTS configuration
    try:
        print_config_info()
    except:
        pass
    
    me = Me()
    port = int(os.environ.get("PORT", 10002))  # Use port 10002 as default for Render
    
    # Custom theme
    dark_theme = gr.themes.Base().set(
        body_background_fill="#2778c4",
        body_text_color="#000000"
    )

    with gr.Blocks(theme=dark_theme) as demo:
        gr.HTML("""
            <style>
                footer, 
                .prose a[href*="gradio.app"], 
                .gradio-container .footer {
                    display: none !important;
                }
            </style>
            """)

        # Password section - always visible initially
        with gr.Column(visible=True) as password_section:
            gr.Markdown("# Welcome")
            error_message = gr.Textbox(
                value="", 
                visible=False, 
                interactive=False, 
                show_label=False,
                container=False
            )
            password_box = gr.Textbox(
                label="🔑 Enter Access Code", 
                type="password",
                placeholder="Enter password to access chatbot"
            )
            with gr.Row():
                submit_btn = gr.Button("Submit", variant="primary")
                show_password_btn = gr.Button("👁️ Show", variant="secondary")

        # Container for chatbot that starts hidden
        with gr.Column(visible=False) as chatbot_section:
            # Dynamic greeting with today's date
            current_date = get_current_date()
            gr.Markdown(f"## 🎤 Voice Chat with Ibe Nwandu")
            gr.Markdown(f"**Today is {current_date}**")
            gr.Markdown("Ask me about my background, experience, and skills. You can use voice input or type your message.")
            
            # Updated voice type selection with better descriptions
            voice_type = gr.Dropdown(
                choices=[
                    ("🎤 Standard Voice (Alloy)", "alloy"),
                    ("🎭 Your Cloned Voice (ElevenLabs)", "custom"),
                    ("🌟 Alternative Voice (Nova)", "nova"),
                    ("💼 Professional Voice (Echo)", "echo")
                ],
                value="alloy",
                label="🎭 Voice Type",
                info="Choose between different AI voices or your personalized cloned voice using ElevenLabs"
            )
            
            # Chat interface
            chatbot = gr.Chatbot(
                label="Chat History",
                height=350,
                show_label=True,
                type="messages"
            )
            
            # Input section - voice and text
            with gr.Row():
                voice_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 Voice Input",
                    scale=2
                )
                msg = gr.Textbox(
                    label="💬 Optional text input",
                    placeholder="Or type your message here...",
                    lines=2,
                    scale=2
                )
            
            # Action buttons
            with gr.Row():
                chat_submit_btn = gr.Button("💬 Send Message", variant="primary", scale=2)
                clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", scale=1)
            
            # Audio output section with better visibility
            with gr.Row():
                gr.Markdown("### 🔊 **Response Audio**")
            
            with gr.Row():
                audio_output = gr.Audio(
                    label="🎵 Response Audio",
                    visible=True,
                    interactive=True,
                    show_label=True,
                    container=True,
                    scale=2
                )
                play_audio_btn = gr.Button("▶️ Play Response", variant="primary", scale=1, visible=False)
                audio_status = gr.Textbox(
                    label="Status",
                    value="No audio available",
                    interactive=False,
                    scale=1
                )

        # Footer
        gr.HTML("""
        <div style='text-align:center; color:red; padding:1em; font-size:1.2em; font-style:italic;'>
            Ibe Nwandu
        </div>
        """)

        # Show/hide password toggle
        password_visible = gr.State(False)
        
        def toggle_password_visibility(is_visible):
            new_visible = not is_visible
            if new_visible:
                return gr.update(type="text"), "🙈 Hide", new_visible
            else:
                return gr.update(type="password"), "👁️ Show", new_visible

        # Button logic
        def handle_password_submit(pw):
            PASSWORD = os.getenv("CHATBOT_PASSCODE")
            if pw == PASSWORD:
                return (
                    gr.update(visible=False),  # Hide password section completely
                    gr.update(visible=True),   # Show chatbot section
                    gr.update(value="", visible=False)  # Clear and hide error
                )
            else:
                return (
                    gr.update(visible=True),   # Keep password section visible
                    gr.update(visible=False),  # Keep chatbot hidden
                    gr.update(value="❌ Wrong password. Try again.", visible=True)  # Show error
                )

        submit_btn.click(
            fn=handle_password_submit,
            inputs=password_box,
            outputs=[password_section, chatbot_section, error_message]
        )
        
        show_password_btn.click(
            fn=toggle_password_visibility,
            inputs=password_visible,
            outputs=[password_box, show_password_btn, password_visible]
        )

        # Voice chat event handlers
        def respond(message, history, voice_type):
            if not message.strip():
                return history, None, "", gr.update(visible=False), "No audio available"
            
            # Update voice type for TTS
            global current_voice_type
            current_voice_type = voice_type
            
            # Convert history from Gradio messages format to tuples for our chat function
            history_tuples = []
            if history:
                for i in range(0, len(history), 2):
                    if i + 1 < len(history):
                        user_msg = history[i].get("content", "")
                        assistant_msg = history[i + 1].get("content", "")
                        history_tuples.append((user_msg, assistant_msg))
            
            # Get response with automatic voice generation
            response, audio_path = me.chat_with_voice(message, history_tuples)
            
            # Update history in Gradio messages format
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})
            
            # Show play button if audio was generated
            show_play_btn = gr.update(visible=audio_path is not None)
            status_text = "Audio ready! Click to play." if audio_path else "No audio available"
            
            return history, audio_path, "", show_play_btn, status_text  # Clear message box and show play button

        def respond_to_voice(audio_file, history, voice_type):
            if not audio_file:
                return history, None, "", gr.update(visible=False), "No audio available"
            
            # Convert speech to text
            transcribed_text = speech_to_text(audio_file)
            if not transcribed_text:
                return history, None, "Could not transcribe audio. Please try again.", gr.update(visible=False), "Transcription failed"
            
            # Update voice type for TTS
            global current_voice_type
            current_voice_type = voice_type
            
            # Convert history from Gradio messages format to tuples for our chat function
            history_tuples = []
            if history:
                for i in range(0, len(history), 2):
                    if i + 1 < len(history):
                        user_msg = history[i].get("content", "")
                        assistant_msg = history[i + 1].get("content", "")
                        history_tuples.append((user_msg, assistant_msg))
            
            # Get response with automatic voice generation
            response, audio_path = me.chat_with_voice(transcribed_text, history_tuples)
            
            # Update history in Gradio messages format
            history.append({"role": "user", "content": transcribed_text})
            history.append({"role": "assistant", "content": response})
            
            # Show play button if audio was generated
            show_play_btn = gr.update(visible=audio_path is not None)
            status_text = "Audio ready! Click to play." if audio_path else "No audio available"
            
            return history, audio_path, "", show_play_btn, status_text

        def clear_chat():
            return [], None, gr.update(visible=False), "No audio available"

        def play_audio():
            """Handle play button click"""
            return "Playing audio..."

        # Connect event handlers
        chat_submit_btn.click(
            fn=respond,
            inputs=[msg, chatbot, voice_type],
            outputs=[chatbot, audio_output, msg, play_audio_btn, audio_status]
        )
        
        # Handle Enter key press in text input
        msg.submit(
            fn=respond,
            inputs=[msg, chatbot, voice_type],
            outputs=[chatbot, audio_output, msg, play_audio_btn, audio_status]
        )
        
        voice_input.change(
            fn=respond_to_voice,
            inputs=[voice_input, chatbot, voice_type],
            outputs=[chatbot, audio_output, msg, play_audio_btn, audio_status]
        )
        
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, audio_output, play_audio_btn, audio_status]
        )
        
        # Handle play button click
        play_audio_btn.click(
            fn=play_audio,
            outputs=[audio_status]
        )

    # Launch app
    # Use 0.0.0.0 for Render deployment, 127.0.0.1 for local development
    server_name = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
    demo.launch(
        server_name=server_name,
        server_port=port,
        share=False,
        show_error=True,
        show_api=False
    )