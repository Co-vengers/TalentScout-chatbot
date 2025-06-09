import google.generativeai as genai
import streamlit as st
import re
from typing import Optional, Tuple, List, Dict

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

MODEL_NAME = "models/gemini-1.5-flash-latest"
EXIT_KEYWORDS = ["exit", "quit", "bye", "goodbye", "end", "stop"]

CANDIDATE_FIELDS = [
    ("Full Name", r"^[A-Za-z\s\-\.']{2,50}$", "Please enter a valid name (2-50 characters)"),
    ("Email Address", r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", "Please enter a valid email address"),
    ("Phone Number", r"^[\d\-\+\s\(\)]{7,20}$", "Please enter a valid phone number (7-20 digits)"),
    ("Years of Experience", r"^\d{1,2}$", "Please enter a valid number (0-99)"),
    ("Desired Position(s)", r".{3,100}", "Please enter position(s) (3-100 characters)"),
    ("Current Location", r".{3,100}", "Please enter location (3-100 characters)"),
    ("Tech Stack", r".{5,200}", "Please describe your tech stack (5-200 characters)")
]

SYSTEM_PROMPT = (
    "You are TalentScout, a professional and friendly hiring assistant for a tech recruitment agency. "
    "Your goal is to collect candidate information and assess their technical skills. "
    "Be concise, professional, and guide the candidate through the process efficiently."
)

@st.cache_resource
def get_gemini_model():
    return genai.GenerativeModel(MODEL_NAME)

class ChatState:
    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.candidate_info = {}
        self.current_stage = "info_collection"
        self.current_field_index = 0
        self.tech_questions = []
        self.tech_answers = []
        self.current_tech_q = 0
        self.waiting_for_response = False

def initialize_session_state():
    if "chat_state" not in st.session_state:
        st.session_state.chat_state = ChatState()

def check_exit(text: str) -> bool:
    return any(word in text.lower() for word in EXIT_KEYWORDS)

def validate_field(field: str, value: str, pattern: str) -> Tuple[bool, str]:
    value = value.strip()
    if not value:
        return False, "This field cannot be empty"
    if not re.match(pattern, value):
        field_def = next((f for f in CANDIDATE_FIELDS if f[0] == field), None)
        return False, field_def[2] if field_def else "Invalid input format"
    return True, ""

def get_current_field() -> Optional[Tuple[str, str, str]]:
    if st.session_state.chat_state.current_field_index < len(CANDIDATE_FIELDS):
        return CANDIDATE_FIELDS[st.session_state.chat_state.current_field_index]
    return None

def generate_tech_questions(tech_stack: str) -> List[str]:
    prompt = (
        f"Generate exactly 5 technical interview questions about: {tech_stack}. "
        "Each question should test specific knowledge in these technologies. "
        "Return ONLY the questions as a numbered list (1-5), nothing else."
    )
    try:
        response = get_gemini_model().generate_content(prompt)
        questions = []
        for line in response.text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                q = re.sub(r'^\d+[\.\)]\s*', '', line)
                questions.append(q)
        return questions[:5] or ["Could you explain your experience with " + tech_stack + "?"]
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return [
            f"Tell me about your experience with {tech_stack}",
            f"What's the most challenging {tech_stack} project you've worked on?",
            f"How would you solve [problem] using {tech_stack}?",
            f"What are the key features of {tech_stack}?",
            f"What's your approach to debugging in {tech_stack}?"
        ]

def render_chat_history():
    for msg in st.session_state.chat_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

def handle_user_input(user_input: str):
    chat_state = st.session_state.chat_state
    if check_exit(user_input):
        chat_state.messages.append({
            "role": "assistant",
            "content": "Thank you for your time! We'll review your information and be in touch."
        })
        chat_state.current_stage = "completed"
        chat_state.waiting_for_response = False
        return
    chat_state.messages.append({"role": "user", "content": user_input})
    if chat_state.current_stage == "info_collection":
        field_info = get_current_field()
        if field_info:
            field, pattern, _ = field_info
            is_valid, error_msg = validate_field(field, user_input, pattern)
            if is_valid:
                chat_state.candidate_info[field] = user_input.strip()
                chat_state.current_field_index += 1
                if chat_state.current_field_index >= len(CANDIDATE_FIELDS):
                    chat_state.current_stage = "tech_questions"
                    chat_state.tech_questions = generate_tech_questions(
                        chat_state.candidate_info.get("Tech Stack", "")
                    )
                    if chat_state.tech_questions:
                        chat_state.waiting_for_response = True
                        chat_state.messages.append({
                            "role": "assistant",
                            "content": chat_state.tech_questions[0]
                        })
            else:
                chat_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                chat_state.waiting_for_response = True
    elif chat_state.current_stage == "tech_questions":
        if chat_state.current_tech_q < len(chat_state.tech_questions):
            chat_state.tech_answers.append(user_input.strip())
            chat_state.current_tech_q += 1
            if chat_state.current_tech_q < len(chat_state.tech_questions):
                chat_state.waiting_for_response = True
                chat_state.messages.append({
                    "role": "assistant",
                    "content": chat_state.tech_questions[chat_state.current_tech_q]
                })
            else:
                chat_state.messages.append({
                    "role": "assistant",
                    "content": "Thank you for completing the interview! We'll review your responses and be in touch."
                })
                chat_state.current_stage = "completed"
                chat_state.waiting_for_response = False

def prompt_next_question():
    chat_state = st.session_state.chat_state
    if chat_state.current_stage == "info_collection":
        field_info = get_current_field()
        if field_info and not chat_state.waiting_for_response:
            chat_state.messages.append({
                "role": "assistant",
                "content": f"What is your {field_info[0]}?"
            })
            chat_state.waiting_for_response = True
    elif (chat_state.current_stage == "tech_questions" and 
          chat_state.current_tech_q < len(chat_state.tech_questions) and
          not chat_state.waiting_for_response):
        chat_state.messages.append({
            "role": "assistant",
            "content": chat_state.tech_questions[chat_state.current_tech_q]
        })
        chat_state.waiting_for_response = True

def main():
    st.title("🤖 TalentScout Hiring Assistant")
    st.markdown("Welcome to TalentScout! I'll guide you through our initial screening process.")
    initialize_session_state()
    render_chat_history()
    chat_state = st.session_state.chat_state
    if not chat_state.waiting_for_response and chat_state.current_stage != "completed":
        prompt_next_question()
        st.rerun()
    if chat_state.waiting_for_response and chat_state.current_stage != "completed":
        user_input = st.chat_input("Type your response here...")
        if user_input:
            chat_state.waiting_for_response = False
            handle_user_input(user_input)
            st.rerun()

if __name__ == "__main__":
    main()