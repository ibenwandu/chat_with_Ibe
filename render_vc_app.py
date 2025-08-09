
import os
import json
import datetime
print("✓ os, json, and datetime imported successfully")

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

load_dotenv(override=True)


def text_to_speech(text, voice="alloy"):
    """Convert text to speech using OpenAI's TTS API"""
    try:
        client = OpenAI()
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Save the audio to a temporary file
        audio_path = "temp_speech.mp3"
        response.stream_to_file(audio_path)
        return audio_path
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return None


def custom_voice_tts(text):
    """Placeholder function for custom voice TTS - ready for your own model/TTS file"""
    # TODO: Implement custom voice TTS when you have your own recorded voice model
    # This could be:
    # 1. A path to your own TTS model
    # 2. An API call to a custom voice service
    # 3. A recorded voice file that gets processed
    
    print(f"Custom voice TTS called with text: {text[:50]}...")
    print("Note: Custom voice not yet implemented. Using default 'alloy' voice.")
    
    # For now, fallback to default voice
    return text_to_speech(text, "alloy")


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
    import requests
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


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
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
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

    def chat_with_voice(self, message, history, voice_enabled=True):
        """Chat with optional text-to-speech for responses"""
        response = self.chat(message, history)
        
        if voice_enabled and response:
            # Generate speech for the response using current voice type
            if current_voice_type == "custom":
                audio_path = custom_voice_tts(response)
            else:
                audio_path = text_to_speech(response, current_voice_type)
            
            if audio_path:
                return response, audio_path
            else:
                return response, None
        else:
            return response, None


if __name__ == "__main__":
    me = Me()
    port = int(os.environ.get("PORT", 10000))  # Use port 10000 as default for Render
    
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
            gr.Markdown("Ask me about my background, experience, and skills. You can type your message or use voice input.")
            
            # Voice controls in a cleaner layout
            with gr.Row():
                voice_toggle = gr.Checkbox(
                    label="🔊 Enable Voice Responses", 
                    value=True,
                    info="Toggle text-to-speech for responses"
                )
                voice_type = gr.Dropdown(
                    choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer", "custom"],
                    value="alloy",
                    label="🎭 Voice Type",
                    info="Choose the voice for responses (Custom = your own voice model)"
                )
            
            # Chat interface with cleaner layout
            chatbot = gr.Chatbot(
                label="Chat History",
                height=350,
                show_label=True
            )
            
            # Combined input section - text and voice side by side
            with gr.Row():
                msg = gr.Textbox(
                    label="💬 Type your message",
                    placeholder="Type here or use voice input...",
                    lines=2,
                    scale=3
                )
                voice_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 Voice Input",
                    scale=1
                )
            
            # Action buttons in cleaner layout
            with gr.Row():
                chat_submit_btn = gr.Button("💬 Send Message", variant="primary", scale=2)
                clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", scale=1)
            
            # Audio output
            audio_output = gr.Audio(
                label="🔊 Response Audio",
                visible=True,
                interactive=False
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
        def respond(message, history, voice_enabled, voice_type):
            if not message.strip():
                return history, None, ""
            
            # Update voice type for TTS
            global current_voice_type
            current_voice_type = voice_type
            
            # Get response with voice
            response, audio_path = me.chat_with_voice(message, history, voice_enabled)
            
            # Update history
            history.append((message, response))
            
            return history, audio_path, ""  # Clear message box

        def respond_to_voice(audio_file, history, voice_enabled, voice_type):
            if not audio_file:
                return history, None, ""
            
            # Convert speech to text
            transcribed_text = speech_to_text(audio_file)
            if not transcribed_text:
                return history, None, "Could not transcribe audio. Please try again."
            
            # Update voice type for TTS
            global current_voice_type
            current_voice_type = voice_type
            
            # Get response
            response, audio_path = me.chat_with_voice(transcribed_text, history, voice_enabled)
            
            # Update history
            history.append((transcribed_text, response))
            
            return history, audio_path, ""

        def clear_chat():
            return [], None

        # Connect event handlers
        chat_submit_btn.click(
            fn=respond,
            inputs=[msg, chatbot, voice_toggle, voice_type],
            outputs=[chatbot, audio_output, msg]
        )
        
        # Handle Enter key press in text input
        msg.submit(
            fn=respond,
            inputs=[msg, chatbot, voice_toggle, voice_type],
            outputs=[chatbot, audio_output, msg]
        )
        
        voice_input.change(
            fn=respond_to_voice,
            inputs=[voice_input, chatbot, voice_toggle, voice_type],
            outputs=[chatbot, audio_output, msg]
        )
        
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, audio_output]
        )

    # Launch app
    demo.launch(
        server_name="127.0.0.1",  # Use 127.0.0.1 for local development
        server_port=port,
        share=False,
        show_error=True,
        show_api=False
    )