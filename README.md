# TalentScout Hiring Assistant Chatbot

## Overview
TalentScout is an intelligent, privacy-conscious hiring assistant chatbot built with Streamlit and a Gemini (Google) or Hugging Face language model. It streamlines the candidate screening process for tech recruitment by interactively gathering personal and technical information, then generating tailored technical questions based on the candidate's tech stack. The chatbot is designed to run efficiently on a MacBook Air M2 (CPU-only) and can be deployed locally or on the cloud.

## Features
- Conversational screening: Guides candidates through a step-by-step interview, collecting essential information (name, contact, experience, position, location, tech stack).
- Tailored technical questions: Dynamically generates 3-5 technical questions relevant to the candidate’s declared technologies.
- Context awareness: Maintains conversation context and handles fallback responses for unclear inputs.
- Graceful exit: Recognizes exit keywords and ends the conversation politely.
- Privacy-conscious: All data is processed locally and never stored or transmitted externally.
- Robust & compatible: Optimized for CPU inference (float32) and works seamlessly on MacBook Air M2.
- User-friendly UI: Clean, modern Streamlit interface for both candidates and recruiters.

## Project Structure
```
talent_scout_chatbot/
├── interview_assistant_chatbot.py # Main Streamlit chatbot application
├── requirements.txt               # Python dependencies
├── README.md                      # Project documentation
```

## Setup & Installation
1. **Clone the Repository**
   ```sh
   git clone git@github.com:Co-vengers/TalentScout-chatbot.git
   cd talent_scout_chatbot
   ```
2. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure API Key (if using Gemini):**
   - Add your Gemini API key to `.streamlit/secrets.toml` as:
     ```toml
     GEMINI_API_KEY = "your-gemini-api-key"
     ```
4. **Run the Chatbot**
   ```sh
   streamlit run interview_assistant_chatbot.py
   ```
   The chatbot will be available at `http://localhost:8501`.

## Usage
- **Start the Chatbot:** Open the Streamlit app in your browser.
- **Candidate Interaction:** The chatbot will greet the candidate and sequentially request:
  - Full Name
  - Email Address
  - Phone Number
  - Years of Experience
  - Desired Position(s)
  - Current Location
  - Tech Stack
- **Technical Questions:** After collecting the tech stack, the chatbot generates 3-5 relevant technical questions.
- **Exit:** Candidates can end the conversation at any time by typing keywords like "exit", "quit", or "bye".

## Privacy & Security
- All candidate data is processed in-memory and never stored or transmitted externally.
- No third-party analytics or tracking is used.
- The application is suitable for privacy-sensitive environments.

## License

_No license. This project is not licensed for public or commercial use._

## Contact
For support or questions, contact the TalentScout development team.
