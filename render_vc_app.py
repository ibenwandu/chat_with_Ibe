import os
import json
import datetime
import gdown
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Placeholder for custom voice function
def custom_voice_tts(text):
    # TODO: Implement your custom voice TTS logic here
    # For now, this just returns None
    return None

# Default OpenAI TTS
def text_to_speech(text, voice="alloy"):
    try:
        client = OpenAI()
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        audio_path = "temp_speech.mp3"
        response.stream_to_file(audio_path)
        return audio_path
    except Exception as e:
        print(f"TTS error: {e}")
        return None

# Whisper STT
def speech_to_text(audio_file):
    try:
        client = OpenAI()
        with open(audio_file, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio
            )
        return transcript.text
    except Exception as e:
        print(f"STT error: {e}")
        return None

# Tools
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
    "description": "Record that a user is interested in being in touch",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string"},
            "name": {"type": "string"},
            "notes": {"type": "string"},
        },
        "required": ["email"],
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Record any question that couldn't be answered",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
        },
        "required": ["question"],
    },
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]

# Me class
class Me:
    def __init__(self):
        self.openai = OpenAI()
        self.name = "Ibe Nwandu"
        self.linkedin = ""
        self.summary = ""

        linkedin_pdf_url = os.getenv("LINKEDIN_PDF_URL")
        if linkedin_pdf_url:
            try:
                gdown.download(linkedin_pdf_url, "linkedin.pdf", quiet=False)
                reader = PdfReader("linkedin.pdf")
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        self.linkedin += text
            except Exception as e:
                print(f"LinkedIn PDF error: {e}")

        summary_txt_url = os.getenv("SUMMARY_TXT_URL")
        if summary_txt_url:
            try:
                gdown.download(summary_txt_url, "summary.txt", quiet=False)
                with open("summary.txt", "r", encoding="utf-8") as f:
                    self.summary = f.read()
            except Exception as e:
                print(f"Summary text error: {e}")

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
        return results

    def system_prompt(self):
        today_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return (
            f"You are acting as {self.name} on {today_str}. "
            f"Answer questions about your career, background, skills, and experience professionally. "
            f"If unsure, record the question. Encourage the user to provide their email for follow-up.

"
            f"## Summary:
{self.summary}

## LinkedIn Profile:
{self.linkedin}
"
        )

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

# Instantiate Me
me = Me()

# Gradio UI
port = int(os.environ.get("PORT", 10000))

dark_theme = gr.themes.Base().set(body_background_fill="#2778c4", body_text_color="#000000")

with gr.Blocks(theme=dark_theme) as demo:
    # Password screen
    with gr.Column(visible=True) as password_section:
        gr.Markdown("# Welcome")
        error_message = gr.Textbox(value="", visible=False, interactive=False, show_label=False)
        password_box = gr.Textbox(label="🔑 Enter Access Code", type="password", placeholder="Enter password")
        submit_btn = gr.Button("Submit", variant="primary")

    # Chatbot section
    with gr.Column(visible=False) as chatbot_section:
        gr.Markdown("## 🎤 Voice Chat with Ibe Nwandu")
        chatbot = gr.Chatbot(label="Chat History", height=400)
        msg = gr.Textbox(label="Type your message (optional)", placeholder="Type here...", lines=2)
        voice_input = gr.Audio(sources=["microphone"], type="filepath", label="🎤 Voice Input")
        voice_type = gr.Dropdown(choices=["default", "custom"], value="default", label="🎭 Voice Type")
        chat_submit_btn = gr.Button("💬 Send Message", variant="primary")
        clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
        audio_output = gr.Audio(label="🔊 Response Audio", interactive=False, autoplay=True)

    def handle_password_submit(pw):
        PASSWORD = os.getenv("CHATBOT_PASSCODE")
        if pw == PASSWORD:
            return gr.update(visible=False), gr.update(visible=True), gr.update(value="", visible=False)
        else:
            return gr.update(visible=True), gr.update(visible=False), gr.update(value="❌ Wrong password", visible=True)

    def respond_text(message, history, voice_type):
        if not message.strip():
            return history, None
        response = me.chat(message, history)
        history.append((message, response))
        if voice_type == "custom":
            audio_path = custom_voice_tts(response)
        else:
            audio_path = text_to_speech(response, "alloy")
        return history, audio_path

    def respond_voice(audio_file, history, voice_type):
        if not audio_file:
            return history, None
        transcribed_text = speech_to_text(audio_file)
        if not transcribed_text:
            return history, None
        response = me.chat(transcribed_text, history)
        history.append((transcribed_text, response))
        if voice_type == "custom":
            audio_path = custom_voice_tts(response)
        else:
            audio_path = text_to_speech(response, "alloy")
        return history, audio_path

    def clear_chat():
        return [], None

    submit_btn.click(handle_password_submit, inputs=password_box, outputs=[password_section, chatbot_section, error_message])
    chat_submit_btn.click(respond_text, inputs=[msg, chatbot, voice_type], outputs=[chatbot, audio_output])
    voice_input.change(respond_voice, inputs=[voice_input, chatbot, voice_type], outputs=[chatbot, audio_output])
    clear_btn.click(clear_chat, outputs=[chatbot, audio_output])

demo.launch(server_name="0.0.0.0", server_port=port, share=False, show_error=True, show_api=False)
