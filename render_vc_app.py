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

    def chat_with_voice(self, message, history):
        """Chat with automatic text-to-speech for responses"""
        response = self.chat(message, history)
        
        if response:
            # Generate speech for the response using current voice type
            if current_voice_type == "custom":
                audio_path = custom_voice_tts(response)
            else:
                audio_path = text_to_speech(response, current_voice_type)
            
            return response, audio_path
        else:
            return response, None


if __name__ == "__main__":
    me = Me()
    port = int(os.environ.get("PORT", 10000))  # Use port 10000 as default for Render
    
    # Custom CSS for simple, clean UI
    custom_css = """
    <style>
        /* Hide Gradio branding */
        footer, 
        .prose a[href*="gradio.app"], 
        .gradio-container .footer {
            display: none !important;
        }
        
        /* Simple, clean styling */
        .gradio-container {
            max-width: 800px !important;
            margin: 0 auto !important;
        }
        
        /* Chat history styling */
        .chat-history {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            min-height: 300px;
            max-height: 500px;
            overflow-y: auto;
        }
        
        /* Input container styling */
        .input-container {
            display: flex;
            align-items: center;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 25px;
            padding: 8px 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* Text input styling */
        .text-input {
            flex: 1;
            border: none;
            outline: none;
            padding: 8px 12px;
            font-size: 16px;
            background: transparent;
        }
        
        /* Icon button styling */
        .icon-btn {
            background: none;
            border: none;
            padding: 8px;
            margin-left: 8px;
            cursor: pointer;
            border-radius: 50%;
            transition: background-color 0.2s;
        }
        
        .icon-btn:hover {
            background-color: #f0f0f0;
        }
        
        /* Voice type selector */
        .voice-selector {
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
    """

    with gr.Blocks(css=custom_css) as demo:
        gr.HTML(custom_css)
        
        # Header
        gr.Markdown("# Chat with Ibe Nwandu")
        gr.Markdown(f"*Today is {get_current_date()}*")
        
        # Voice type selector
        with gr.Row():
            voice_type = gr.Dropdown(
                choices=["alloy", "custom"],
                value="alloy",
                label="Voice Type",
                container=False,
                scale=1
            )
        
        # Chat history
        chatbot = gr.Chatbot(
            label="",
            height=400,
            show_label=False,
            container=False,
            elem_classes=["chat-history"]
        )
        
        # Simple input interface
        with gr.Row():
            with gr.Column(scale=4):
                msg = gr.Textbox(
                    label="",
                    placeholder="Type your message here...",
                    lines=1,
                    show_label=False,
                    container=False,
                    elem_classes=["text-input"]
                )
            with gr.Column(scale=1):
                voice_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="",
                    show_label=False,
                    container=False
                )
            with gr.Column(scale=1):
                send_btn = gr.Button("Send", variant="primary", size="sm")
        
        # Audio output (hidden but functional)
        audio_output = gr.Audio(
            label="",
            visible=False,
            interactive=False
        )

        # Event handlers
        def respond(message, history, voice_type):
            if not message.strip():
                return history, None, ""
            
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
            
            return history, audio_path, ""  # Clear message box

        def respond_to_voice(audio_file, history, voice_type):
            if not audio_file:
                return history, None, ""
            
            # Convert speech to text
            transcribed_text = speech_to_text(audio_file)
            if not transcribed_text:
                return history, None, "Could not transcribe audio. Please try again."
            
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
            
            return history, audio_path, ""

        # Connect event handlers
        send_btn.click(
            fn=respond,
            inputs=[msg, chatbot, voice_type],
            outputs=[chatbot, audio_output, msg]
        )
        
        # Handle Enter key press in text input
        msg.submit(
            fn=respond,
            inputs=[msg, chatbot, voice_type],
            outputs=[chatbot, audio_output, msg]
        )
        
        voice_input.change(
            fn=respond_to_voice,
            inputs=[voice_input, chatbot, voice_type],
            outputs=[chatbot, audio_output, msg]
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