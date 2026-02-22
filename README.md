🧠 Wellsy – AI Mental Health Companion

Designed for Mental Wellness

Wellsy is a secure, AI-powered mental health companion built using Streamlit and Python, designed to provide users with a safe, empathetic, and structured space to express their thoughts and emotions.

Unlike generic chatbots, Wellsy includes user authentication, multiple AI personas, persistent chat sessions, safety-aware responses, and crisis support handling, making it suitable for academic evaluation, real-world demos, and portfolio showcasing.

🔗 Live Application

👉 Live App URL: https://wellsy.streamlit.app/

🎯 Problem Statement

Mental health challenges such as stress, anxiety, emotional overwhelm, and negative thought patterns are increasingly common. However:

Immediate mental health support is not always accessible

Social stigma prevents open expression

Professional help may not be instantly available

There is a need for a safe, non-judgmental, always-available digital companion that supports users emotionally while encouraging healthy coping mechanisms.

💡 Proposed Solution

Wellsy provides a web-based AI mental health companion that:

Allows users to securely log in and manage conversations

Offers multiple AI personas tailored to different emotional needs

Maintains chat history and session continuity

Responds with empathetic, safety-aware, and context-aware messages

Encourages external help during crisis situations

✨ Key Features
🔐 Authentication & User Management

Secure login and registration system

Password-based authentication

User-specific chat sessions and memory

💬 Persistent Chat Sessions

Create multiple chat sessions

Rename or delete past conversations

Chat history stored and reloaded automatically

Session continuity using database + Streamlit session state

🧠 Multiple AI Personas

Users can choose how they want to be supported:

Wellsy Counselor
Balanced, structured, professional mental health guidance

Empathetic Listener
Deep emotional validation and non-judgmental listening

Growth Coach
Encouraging, motivational support focused on positive action

CBT Companion
Cognitive Behavioral Therapy–based thought reframing and reflection

Each persona uses custom system prompts to control tone, behavior, and safety.

🚨 Built-in Safety & Crisis Handling

Global mental health safety layer

Detects severe emotional distress or self-harm expressions

Encourages:

Reaching out to trusted people

Seeking professional help

Contacting emergency services if needed

Country-based crisis resources (India, USA, UK, Canada)

Never presents itself as a replacement for professional care

🌍 Location-Aware Safety Support

Optional country selection

Displays relevant crisis helpline information

Falls back to general emergency guidance if location is unknown

🖥️ User Experience & Interface

Clean, minimal, distraction-free UI

Chat-style message display

Auto-scroll for new messages

Loading spinner while AI responds

Light & dark theme support

Inspirational wellness quotes on login screen

🔐 Secure Configuration

API keys managed via environment variables

Compatible with Streamlit Secrets Manager

No sensitive data exposed in codebase

🧩 Application Workflow

User registers or logs in securely

User selects an AI persona and (optionally) country

User creates or selects a chat session

User enters thoughts or concerns

AI generates a context-aware, persona-based response

Conversation is stored and persisted

Safety layer activates when high-risk language is detected

⚙️ System Architecture
🔹 Frontend

Streamlit UI

Sidebar-based navigation

Chat input and message rendering

🔹 Backend Logic

Python-based session handling

Database-backed user & chat storage

Session state for smooth UX

🔹 AI Layer

Groq API (llama-3.3-70b-versatile)

Persona-based system prompts

Memory-based conversation context

Controlled temperature and token limits

🔹 Deployment

GitHub for version control

Streamlit Community Cloud for hosting

Secrets Manager for secure keys

📁 Project Structure
wellsy/
│
├── app.py              # Main Streamlit application
├── auth.py             # Authentication & login UI
├── chatbot.py          # AI logic, personas & safety layer
├── database.py         # User & chat persistence (SQLite)
├── requirements.txt    # Dependencies
├── img/                # Logos & icons
├── README.md           # Documentation
└── .gitignore
🛠️ Local Setup & Installation
1️⃣ Clone Repository
git clone https://github.com/your-username/wellsy.git
cd wellsy
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Configure Environment Variables

Create a .env file:

GROQ_API_KEY=your_api_key_here
4️⃣ Run the App
streamlit run app.py
📊 Results & Outcomes

Successfully built and deployed a full-stack AI mental health app

Implemented authentication, persistence, safety, and personalization

Demonstrated real-world AI integration and cloud deployment

Suitable for academic projects, internships, and AI portfolios

🏁 Conclusion

Wellsy demonstrates how AI, responsible prompt design, and thoughtful UX can be combined to create meaningful mental health support tools. The project emphasizes user safety, empathy, personalization, and real-world deployment ’best practices’.

🔮 Future Scope

Mood & sentiment analytics

Long-term emotional tracking

Professional therapist integration

Multilingual support

Mobile app version

Crisis escalation workflows
