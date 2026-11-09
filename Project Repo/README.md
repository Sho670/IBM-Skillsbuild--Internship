# 💪 Fitness Buddy

An AI-powered personal health and fitness coach built with **IBM Granite** (via IBM watsonx.ai) and **Streamlit**.

---

## 🌟 Features

| Feature | Description |
|---|---|
| 🏋️ **Personalized Workouts** | Home routines tailored to your fitness level, goals & available equipment |
| 🥦 **Nutrition Guidance** | Simple, healthy meal ideas matched to your dietary preferences |
| 🔥 **Daily Motivation** | Inspirational tips to keep you consistent and focused |
| 📅 **Habit Building** | Practical advice to build lasting healthy routines |
| 💬 **Conversational Chat** | Natural language interface powered by IBM Granite LLM |

---

## 🛠️ Tech Stack

- **Frontend / UI**: [Streamlit](https://streamlit.io/)
- **AI Model**: IBM Granite (`ibm/granite-3-8b-instruct`) via [IBM watsonx.ai](https://www.ibm.com/watsonx)
- **IBM Cloud Service**: IBM watsonx.ai Lite (free tier)
- **Language**: Python 3.9+

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd fitness-buddy
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure IBM Granite API credentials

Edit the `.env` file and add your IBM Cloud credentials:

```env
IBM_API_KEY=your_ibm_api_key_here
IBM_PROJECT_ID=your_ibm_project_id_here
IBM_URL=https://us-south.ml.cloud.ibm.com
IBM_MODEL_ID=ibm/granite-3-8b-instruct
```

#### How to get IBM credentials (free):
1. Sign up at [IBM Cloud](https://cloud.ibm.com/registration) (Lite tier is free)
2. Navigate to **watsonx.ai** → Create a project
3. Go to **Manage → Access (IAM)** → Create an **API Key**
4. Copy your **Project ID** from the project settings

### 4. Run the application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
fitness-buddy/
├── app.py              # Main Streamlit application
├── .env                # Environment variables (IBM API credentials)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🔒 Demo Mode

If IBM API credentials are not yet configured, the app runs in **Demo Mode** with pre-written, high-quality fitness responses. This lets you explore the full UI without needing an API key immediately.

---

## ⚕️ Disclaimer

Fitness Buddy provides general wellness guidance only. Always consult a qualified healthcare professional before starting a new exercise or nutrition program, especially if you have any pre-existing health conditions.

---

## 📄 License

This project was built for the AICTE Problem Statement #13 — Fitness Buddy.
