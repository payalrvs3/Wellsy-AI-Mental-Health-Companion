<h1 align="center"> Wellsy – AI Mental Health Companion</h1>

<p align="center">
  <b>Designed for Mental Wellness • Built with Streamlit & AI</b>
</p>

<p align="center">
  <img src="img/logo.png" alt="Wellsy Logo" width="180"/>
</p>

<hr>

<h2>🌱 Overview</h2>
<p>
<b>Wellsy</b> is a secure, AI-powered mental health companion designed to provide users with a
<strong>safe, empathetic, and structured space</strong> to express emotions and thoughts.
</p>

<p>
Unlike generic chatbots, Wellsy includes <b>authentication, multiple AI personas, persistent chat sessions,
safety-aware responses, and crisis support handling</b>.
</p>

<hr>

<h2>🔗 Live Application</h2>
<p>
👉 <b>Live App:</b>
<a href="https://wellsy.streamlit.app/" target="_blank">
https://wellsy.streamlit.app/
</a>
</p>

<hr>

<h2>🎯 Problem Statement</h2>
<ul>
  <li>Rising stress, anxiety, and emotional burnout</li>
  <li>Limited access to immediate mental health support</li>
  <li>Social stigma around expressing mental health concerns</li>
</ul>

<p>
There is a need for an <b>always-available, non-judgmental digital companion</b> that supports emotional wellbeing
and encourages healthy coping strategies.
</p>

<hr>

<h2>💡 Proposed Solution</h2>
<p>
Wellsy provides a <b>web-based AI mental health assistant</b> that allows users to:
</p>

<ul>
  <li>Communicate freely in a private and secure environment</li>
  <li>Select AI personas based on emotional needs</li>
  <li>Maintain conversation history across sessions</li>
  <li>Receive safety-aware and empathetic responses</li>
</ul>

<hr>

<h2>✨ Key Features</h2>

<h3>🔐 Authentication & Security</h3>
<ul>
  <li>User login and registration</li>
  <li>Password-based authentication</li>
  <li>Secure API key handling via environment variables</li>
</ul>

<h3>💬 Persistent Chat Sessions</h3>
<ul>
  <li>Create multiple chat sessions</li>
  <li>Rename or delete conversations</li>
  <li>Automatic chat history loading</li>
</ul>

<h3>🧠 Multiple AI Personas</h3>
<table>
  <tr>
    <th align="left">Persona</th>
    <th align="left">Purpose</th>
  </tr>
  <tr>
    <td>Wellsy Counselor</td>
    <td>Balanced and structured mental health guidance</td>
  </tr>
  <tr>
    <td>Empathetic Listener</td>
    <td>Emotional validation and active listening</td>
  </tr>
  <tr>
    <td>Growth Coach</td>
    <td>Encouragement and positive action focus</td>
  </tr>
  <tr>
    <td>CBT Companion</td>
    <td>Cognitive Behavioral Therapy based support</td>
  </tr>
</table>

<h3>🚨 Safety & Crisis Support</h3>
<ul>
  <li>Global mental health safety layer</li>
  <li>Suicide & self-harm awareness handling</li>
  <li>Country-based crisis resources (India, USA, UK, Canada)</li>
  <li>Encourages professional and human support</li>
</ul>

<h3>🌍 Location-Aware Support</h3>
<ul>
  <li>Optional country selection</li>
  <li>Displays relevant crisis helpline information</li>
</ul>

<h3>🖥️ User Experience</h3>
<ul>
  <li>Clean, minimal, distraction-free UI</li>
  <li>Chat-style interface</li>
  <li>Auto-scroll & loading indicators</li>
  <li>Light/Dark theme compatibility</li>
</ul>

<hr>

<h2>🧩 Application Workflow</h2>
<ol>
  <li>User logs in or registers</li>
  <li>Selects AI persona and country</li>
  <li>Creates or selects a chat session</li>
  <li>Enters thoughts or concerns</li>
  <li>AI generates a context-aware response</li>
  <li>Conversation is securely stored</li>
</ol>

<hr>

<h2>⚙️ System Architecture</h2>
<ul>
  <li><b>Frontend:</b> Streamlit UI components</li>
  <li><b>Backend:</b> Python-based session & database handling</li>
  <li><b>AI Layer:</b> Groq API (LLaMA 3.3 – 70B)</li>
  <li><b>Deployment:</b> GitHub + Streamlit Community Cloud</li>
</ul>

<hr>

<h2>📁 Project Structure</h2>

<pre>
wellsy/
│
├── app.py              # Main Streamlit application
├── auth.py             # Authentication & login UI
├── chatbot.py          # AI personas & safety logic
├── database.py         # SQLite persistence
├── requirements.txt
├── img/
│   ├── logo.png
│   └── icon.png
└── README.md
</pre>

<hr>

<h2>🛠️ Local Installation</h2>

<pre>
git clone https://github.com/your-username/wellsy.git
cd wellsy
pip install -r requirements.txt
streamlit run app.py
</pre>

<hr>

<h2>📊 Results</h2>
<ul>
  <li>Successfully deployed a full-stack AI mental health app</li>
  <li>Implemented safety-first AI design</li>
  <li>Demonstrated cloud deployment & real-world usability</li>
</ul>

<hr>

<h2>🏁 Conclusion</h2>
<p>
Wellsy demonstrates how <b>responsible AI, thoughtful UX, and cloud technologies</b> can be combined to build
meaningful mental health support systems while prioritizing user safety.
</p>

<hr>

<h2>🔮 Future Scope</h2>
<ul>
  <li>Mood tracking & analytics</li>
  <li>Multilingual support</li>
  <li>Mobile application</li>
  <li>Professional therapist integration</li>
</ul>
