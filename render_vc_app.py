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


if __name__ == "__main__":
    me = Me()
    port = int(os.environ.get("PORT", 10000))
    
    # Custom CSS for minimal design matching the screenshot
    custom_css = """
    /* Hide Gradio footer and branding */
    footer, 
    .prose a[href*="gradio.app"], 
    .gradio-container .footer {
        display: none !important;
    }
    
    /* Clean, minimal styling */
    .gradio-container {
        max-width: 800px !important;
        margin: 0 auto;
        background: white;
    }
    
    /* Hide labels and make it cleaner */
    .audio-container label,
    .textbox-container label {
        display: none !important;
    }
    
    /* Style the input area to match screenshot */
    .input-container {
        border: 1px solid #e0e0e0;
        border-radius: 25px;
        padding: 8px 16px;
        background: white;
        margin: 20px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Voice mode button styling */
    .voice-mode-btn {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 14px;
        color: #666;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .voice-mode-btn:hover {
        background: #e9ecef;
        border-color: #adb5bd;
    }
    
    .voice-mode-active {
        background: #007bff !important;
        color: white !important;
        border-color: #007bff !important;
    }
    
    /* Hide unnecessary elements */
    .chatbot .message-wrap {
        display: none;
    }
    
    /* Center the interface */
    .main-container {
        text-align: center;
        padding: 40px 20px;
    }
    
    /* Style buttons to be more minimal */
    .gr-button {
        border-radius: 20px;
        border: 1px solid #ddd;
        background: white;
        padding: 8px 16px;
    }
    
    /* Hide audio input when not in voice mode */
    .audio-hidden {
        display: none !important;
    }
    """

    with gr.Blocks(css=custom_css, title="Voice Chat") as demo:
        
        # Password section
        with gr.Column(visible=True, elem_classes=["main-container"]) as password_section:
            gr.Markdown("# Welcome")
            error_message = gr.Textbox(
                value="", 
                visible=False, 
                interactive=False, 
                show_label=False,
                container=False
            )
            password_box = gr.Textbox(
                label="🔒 Enter Access Code", 
                type="password",
                placeholder="Enter password to access chatbot",
                elem_classes=["input-container"]
            )
            with gr.Row():
                submit_btn = gr.Button("Submit", variant="primary")
                show_password_btn = gr.Button("👁️ Show", variant="secondary")

        # Simple chatbot interface matching the screenshot
        with gr.Column(visible=False, elem_classes=["main-container"]) as chatbot_section:
            # Minimal header
            gr.Markdown("## Voice Assistant")
            
            # Chatbot for conversation history using tuples format
            chatbot = gr.Chatbot(
                visible=True,
                show_label=False,
                height=300
            )
            
            # Main input area with conditional display
            with gr.Column():
                # Text mode interface (default)
                with gr.Row(elem_classes=["input-container"], visible=True) as text_mode:
                    # Voice mode toggle button
                    voice_mode_btn = gr.Button(
                        "🎤 Use voice mode", 
                        variant="secondary",
                        elem_classes=["voice-mode-btn"],
                        scale=1
                    )
                    
                    # Text input
                    msg = gr.Textbox(
                        show_label=False,
                        placeholder="Ask me anything...",
                        container=False,
                        lines=1,
                        scale=4
                    )
                    
                    # Send button
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                
                # Voice mode interface (hidden by default)
                with gr.Column(visible=False) as voice_mode_interface:
                    with gr.Row():
                        # Exit voice mode button
                        exit_voice_btn = gr.Button(
                            "🔇 Exit voice mode", 
                            variant="primary",
                            elem_classes=["voice-mode-btn", "voice-mode-active"]
                        )
                    
                    # Audio input with clear styling
                    voice_input = gr.Audio(
                        sources=["microphone"],
                        type="filepath",
                        label="🎤 Record your question",
                        show_label=True,
                        container=True
                    )
                    
                    gr.Markdown("*Speak your question and it will be automatically processed when recording stops*")
            
            # Response text display
            response_text = gr.Textbox(
                label="Response",
                interactive=False,
                lines=4,
                visible=True
            )
            
            # Clear button
            clear_btn = gr.Button("Clear Conversation", variant="secondary")

        # Password handling
        def handle_password_submit(pw):
            PASSWORD = os.getenv("CHATBOT_PASSCODE")
            if pw == PASSWORD:
                return (
                    gr.update(visible=False),
                    gr.update(visible=True),
                    gr.update(value="", visible=False)
                )
            else:
                return (
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(value="❌ Wrong password. Try again.", visible=True)
                )

        submit_btn.click(
            fn=handle_password_submit,
            inputs=password_box,
            outputs=[password_section, chatbot_section, error_message]
        )

        # Show/hide password
        password_visible = gr.State(False)
        
        def toggle_password_visibility(is_visible):
            new_visible = not is_visible
            if new_visible:
                return gr.update(type="text"), "🙈 Hide", new_visible
            else:
                return gr.update(type="password"), "👁️ Show", new_visible

        show_password_btn.click(
            fn=toggle_password_visibility,
            inputs=password_visible,
            outputs=[password_box, show_password_btn, password_visible]
        )

        # Voice mode toggle
        def activate_voice_mode():
            return (
                gr.update(visible=False),  # Hide text mode
                gr.update(visible=True)    # Show voice mode
            )
        
        def exit_voice_mode():
            return (
                gr.update(visible=True),   # Show text mode
                gr.update(visible=False)   # Hide voice mode
            )

        voice_mode_btn.click(
            fn=activate_voice_mode,
            outputs=[text_mode, voice_mode_interface]
        )
        
        exit_voice_btn.click(
            fn=exit_voice_mode,
            outputs=[text_mode, voice_mode_interface]
        )

        # Chat functionality
        def respond(message, history):
            if not message.strip():
                return history, "", ""
            
            # Get response
            response = me.chat(message, history)
            
            # Update history in tuples format for Gradio
            new_history = history + [(message, response)]
            
            return new_history, response, ""

        def respond_to_voice(audio_file, history):
            if not audio_file:
                return history, "Could not process audio. Please try again.", gr.update(visible=True), gr.update(visible=False)
            
            # Convert speech to text
            transcribed_text = speech_to_text(audio_file)
            if not transcribed_text:
                return history, "Could not transcribe audio. Please try again.", gr.update(visible=True), gr.update(visible=False)
            
            # Get response
            response = me.chat(transcribed_text, history)
            
            # Update history in tuples format for Gradio
            new_history = history + [(f"🎤 {transcribed_text}", response)]
            
            # Return to text mode after processing voice input
            return new_history, response, gr.update(visible=True), gr.update(visible=False)

        def clear_chat():
            return [], ""

        # Event handlers
        send_btn.click(
            fn=respond,
            inputs=[msg, chatbot],
            outputs=[chatbot, response_text, msg]
        )
        
        msg.submit(
            fn=respond,
            inputs=[msg, chatbot],
            outputs=[chatbot, response_text, msg]
        )
        
        voice_input.change(
            fn=respond_to_voice,
            inputs=[voice_input, chatbot],
            outputs=[chatbot, response_text, text_mode, voice_mode_interface]
        )
        
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, response_text]
        )

    # Launch app
    server_name = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
    demo.launch(
        server_name=server_name,
        server_port=port,
        share=False,
        show_error=True,
        show_api=False
    )