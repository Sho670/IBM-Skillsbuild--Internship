import os
import streamlit as st
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

# ── Load environment variables ──────────────────────────────────────────────
load_dotenv()

IBM_API_KEY   = os.getenv("IBM_API_KEY")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID")
IBM_URL        = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")
IBM_MODEL_ID   = os.getenv("IBM_MODEL_ID", "ibm/granite-4-h-small")
APP_TITLE      = os.getenv("APP_TITLE", "Fitness Buddy")
APP_ICON       = os.getenv("APP_ICON", "💪")

# ── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Global */
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(160deg, #0f2027, #203a43, #2c5364);
        color: #ffffff;
    }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label { color: #d1fae5 !important; }

    /* Header banner */
    .hero-banner {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        color: #fff;
    }
    .hero-banner h1 { font-size: 2.4rem; margin: 0 0 6px; }
    .hero-banner p  { font-size: 1.05rem; margin: 0; opacity: .9; }

    /* Chat messages */
    .chat-user {
        background: #e0f7fa;
        border-left: 4px solid #00acc1;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 10px 0;
    }
    .chat-bot {
        background: #f1f8e9;
        border-left: 4px solid #43a047;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 10px 0;
    }
    .chat-label { font-size: .75rem; font-weight: 700; color: #555; margin-bottom: 4px; }

    /* Quick-action pills */
    .pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }
    .pill {
        background: #e8f5e9; border: 1px solid #a5d6a7;
        border-radius: 20px; padding: 6px 16px;
        font-size: .85rem; color: #2e7d32; cursor: pointer;
    }

    /* Metric cards */
    .metric-card {
        background: #ffffff; border: 1px solid #e0e0e0;
        border-radius: 12px; padding: 18px; text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,.06);
    }
    .metric-card .number { font-size: 2rem; font-weight: 700; color: #11998e; }
    .metric-card .label  { font-size: .85rem; color: #757575; margin-top: 4px; }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── IBM Granite client (cached) ──────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_model():
    """Initialise and return the IBM Granite model inference client."""
    if not IBM_API_KEY or IBM_API_KEY == "your_ibm_api_key_here":
        return None
    if not IBM_PROJECT_ID or IBM_PROJECT_ID == "your_ibm_project_id_here":
        return None
    try:
        creds = Credentials(url=IBM_URL, api_key=IBM_API_KEY)
        model = ModelInference(
            model_id=IBM_MODEL_ID,
            credentials=creds,
            project_id=IBM_PROJECT_ID,
        )
        return model
    except Exception as exc:
        st.error(f"IBM Granite connection error: {exc}")
        return None


# ── System prompt builder ────────────────────────────────────────────────────
def build_system_prompt(profile: dict) -> str:
    return f"""You are Fitness Buddy, a friendly, motivating, and knowledgeable AI-powered health and fitness coach.

User Profile:
- Fitness Goal: {profile.get('goal', 'General Fitness')}
- Fitness Level: {profile.get('level', 'Beginner')}
- Available Equipment: {profile.get('equipment', 'No equipment (bodyweight only)')}
- Days per Week: {profile.get('days', 3)}
- Age Group: {profile.get('age_group', '18-30')}
- Dietary Preference: {profile.get('diet', 'No preference')}

Your responsibilities:
1. Recommend personalized home workouts and exercise routines tailored to the user's profile.
2. Provide daily motivational tips and fitness inspiration.
3. Suggest simple, nutritious meal ideas aligned with their dietary preference.
4. Encourage habit-building and consistency with practical advice.
5. Answer general fitness, nutrition, and wellness questions.

Guidelines:
- Be warm, encouraging, and non-judgmental.
- Keep responses clear, concise, and actionable.
- Use bullet points or numbered lists for workouts and meal plans.
- Always remind users to consult a doctor before starting a new exercise program if they have health conditions.
- Never diagnose medical conditions or replace professional medical advice.
"""


# ── Generate response ────────────────────────────────────────────────────────
def generate_response(model, conversation_history: list, user_message: str, profile: dict) -> str:
    """Send the conversation to IBM Granite using the chat API and return the reply."""
    system_prompt = build_system_prompt(profile)

    # Build messages list for the chat API
    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-8:]:   # keep last 8 turns for context
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        response = model.chat(
            messages=messages,
            params={"max_tokens": 800, "temperature": 0.7},
        )
        reply = response["choices"][0]["message"]["content"]
        return reply.strip() if reply else "I couldn't generate a response. Please try again."
    except Exception as exc:
        return f"Error communicating with IBM Granite: {exc}"


# ── Demo fallback (no API key) ───────────────────────────────────────────────
DEMO_RESPONSES = {
    "workout": """Here's a quick **30-minute home workout** for you:

**Warm-Up (5 min)**
- 2 min light jogging in place
- 1 min arm circles
- 2 min leg swings

**Main Circuit (20 min) — 3 rounds**
1. 15 × Push-ups
2. 20 × Bodyweight squats
3. 10 × Lunges (each leg)
4. 30-sec Plank hold
5. 15 × Glute bridges
*Rest 60 seconds between rounds.*

**Cool-Down (5 min)**
- Hamstring stretch — 30 sec each side
- Child's pose — 1 min
- Deep breathing — 2 min

💡 *Consistency beats intensity. 3× per week builds lasting strength!*""",

    "meal": """Here are **3 simple, nutritious meal ideas** for today:

🥣 **Breakfast — Overnight Oats**
- ½ cup rolled oats + 1 cup milk of choice
- 1 tbsp chia seeds, banana slices, a drizzle of honey
*High in fibre, keeps you full for hours.*

🥗 **Lunch — Grilled Chicken Salad**
- 150 g grilled chicken breast
- Mixed greens, cherry tomatoes, cucumber, olive oil & lemon dressing
*Lean protein + healthy fats = sustained energy.*

🍲 **Dinner — Lentil Soup**
- Red lentils, diced tomatoes, spinach, cumin, garlic
- Serve with a slice of whole-grain bread
*Plant-based protein and iron-rich.*

💧 *Tip: Drink 8–10 glasses of water throughout the day!*""",

    "motivation": """🔥 **Your Daily Fitness Inspiration**

*"The only bad workout is the one that didn't happen."*

Remember why you started. Every squat, every step, every healthy meal is a vote for the person you're becoming.

**3 Habits to Build This Week:**
1. ✅ Move for at least 20 minutes every day
2. ✅ Prep one healthy meal in advance
3. ✅ Sleep 7–8 hours — recovery IS training

You've got this! 💪""",

    "default": """Hi! I'm **Fitness Buddy** 💪 — your AI-powered health and fitness coach.

I can help you with:
- 🏋️ **Personalized home workouts** tailored to your level & goals
- 🥦 **Nutritious meal suggestions** for your dietary needs
- 🔥 **Daily motivation** to keep you consistent
- 📅 **Habit-building tips** for a healthier lifestyle

Try asking me:
- *"Give me a 20-minute workout for beginners"*
- *"What should I eat for more energy?"*
- *"Motivate me to stay consistent"*
- *"How do I build a morning routine?"*"""
}

def demo_response(user_message: str) -> str:
    msg = user_message.lower()
    if any(k in msg for k in ["workout", "exercise", "train", "routine", "gym"]):
        return DEMO_RESPONSES["workout"]
    if any(k in msg for k in ["meal", "eat", "food", "nutrition", "diet", "recipe"]):
        return DEMO_RESPONSES["meal"]
    if any(k in msg for k in ["motivat", "inspire", "habit", "consistent", "tips"]):
        return DEMO_RESPONSES["motivation"]
    return DEMO_RESPONSES["default"]


# ── Session state initialisation ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0


# ── Sidebar — User Profile ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏃 Your Fitness Profile")
    st.markdown("---")

    goal = st.selectbox(
        "🎯 Fitness Goal",
        ["Weight Loss", "Muscle Gain", "General Fitness", "Improve Endurance",
         "Stress Relief / Flexibility", "Maintain Current Fitness"],
        index=2,
    )
    level = st.selectbox(
        "📊 Fitness Level",
        ["Beginner", "Intermediate", "Advanced"],
        index=0,
    )
    equipment = st.selectbox(
        "🏠 Available Equipment",
        ["No equipment (bodyweight only)", "Resistance bands", "Dumbbells",
         "Full home gym", "Gym access"],
        index=0,
    )
    days = st.slider("📅 Workout Days per Week", min_value=1, max_value=7, value=3)
    age_group = st.selectbox(
        "🎂 Age Group",
        ["Under 18", "18–30", "31–45", "46–60", "60+"],
        index=1,
    )
    diet = st.selectbox(
        "🥗 Dietary Preference",
        ["No preference", "Vegetarian", "Vegan", "Keto", "High-protein",
         "Gluten-free", "Dairy-free"],
        index=0,
    )

    st.session_state.profile = {
        "goal": goal, "level": level, "equipment": equipment,
        "days": days, "age_group": age_group, "diet": diet,
    }

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_count = 0
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", st.session_state.chat_count)
    with col2:
        st.metric("Days/Week", days)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:.75rem; opacity:.7; text-align:center;'>"
        "Powered by IBM Granite 🤖<br>IBM watsonx.ai</div>",
        unsafe_allow_html=True,
    )


# ── Main area ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <h1>{APP_ICON} {APP_TITLE}</h1>
    <p>Your AI-powered personal health & fitness coach — available 24/7, completely free.</p>
</div>
""", unsafe_allow_html=True)

# API key status banner
model = get_model()
if model is None:
    st.warning(
        "⚠️ **Demo Mode** — IBM Granite API keys not configured. "
        "Add your `IBM_API_KEY` and `IBM_PROJECT_ID` to the `.env` file for full AI responses. "
        "Pre-written demo responses are shown below.",
        icon="🔔",
    )
else:
    st.success("✅ Connected to **IBM Granite** via watsonx.ai", icon="🤖")

# Quick-action buttons
st.markdown("**✨ Quick Actions — click to ask instantly:**")
qcol1, qcol2, qcol3, qcol4 = st.columns(4)
quick_prompts = {
    "🏋️ Today's Workout": "Give me a workout routine for today based on my profile.",
    "🥦 Meal Plan": "Suggest a healthy meal plan for today based on my dietary preference.",
    "🔥 Motivate Me": "Give me motivational tips and daily fitness inspiration.",
    "📅 Weekly Plan": "Create a weekly workout and nutrition plan tailored to my goals.",
}
for col, (label, prompt) in zip([qcol1, qcol2, qcol3, qcol4], quick_prompts.items()):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state["pending_prompt"] = prompt

st.markdown("---")

# Render chat history
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-bot">
            <div class="chat-label">💪 Fitness Buddy</div>
            👋 Hello! I'm <strong>Fitness Buddy</strong>, your personal AI fitness coach.<br><br>
            Tell me your goals, ask for a workout, request meal ideas, or just say hi!
            I'm here to help you build a healthier, happier lifestyle — one step at a time. 🌟
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-user"><div class="chat-label">🧑 You</div>{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-bot"><div class="chat-label">💪 Fitness Buddy</div>{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

# ── Input area ───────────────────────────────────────────────────────────────
st.markdown("---")
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "💬 Ask Fitness Buddy anything…",
        placeholder=(
            "e.g. 'Give me a 30-minute beginner workout', "
            "'What should I eat after exercise?', "
            "'How do I stay motivated?'"
        ),
        height=90,
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Send 🚀", use_container_width=True)

# Handle quick-action injection
if "pending_prompt" in st.session_state:
    pending = st.session_state.pop("pending_prompt")
    # Append user message
    st.session_state.messages.append({"role": "user", "content": pending})
    with st.spinner("Fitness Buddy is thinking… 🤔"):
        if model:
            reply = generate_response(
                model,
                st.session_state.messages[:-1],
                pending,
                st.session_state.profile,
            )
        else:
            reply = demo_response(pending)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.chat_count += 1
    st.rerun()

# Handle typed input
if submitted and user_input.strip():
    user_text = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.spinner("Fitness Buddy is thinking… 🤔"):
        if model:
            reply = generate_response(
                model,
                st.session_state.messages[:-1],
                user_text,
                st.session_state.profile,
            )
        else:
            reply = demo_response(user_text)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.chat_count += 1
    st.rerun()

# ── Footer info cards ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🌟 What Fitness Buddy Can Do For You")
fc1, fc2, fc3, fc4 = st.columns(4)
features = [
    ("🏋️", "Personalized Workouts", "Home routines tailored to your level, goals & equipment"),
    ("🥦", "Nutrition Guidance",    "Simple, healthy meal ideas matching your dietary needs"),
    ("🔥", "Daily Motivation",      "Inspirational tips to keep you consistent and focused"),
    ("📅", "Habit Building",        "Practical advice to build lasting healthy routines"),
]
for col, (icon, title, desc) in zip([fc1, fc2, fc3, fc4], features):
    with col:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="font-size:2rem">{icon}</div>'
            f'<div class="number" style="font-size:1rem;margin-top:8px">{title}</div>'
            f'<div class="label">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    "<br><div style='text-align:center;color:#9e9e9e;font-size:.8rem;'>"
    "⚕️ Fitness Buddy provides general wellness guidance only. "
    "Always consult a qualified healthcare professional before starting a new fitness program."
    "</div>",
    unsafe_allow_html=True,
)
