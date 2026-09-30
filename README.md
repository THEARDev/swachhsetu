# 🌿 SwachhSetu

> **Smart Waste Management System** — AI + NLP powered, 3-role workflow

## 🚀 LIVE DEMO

👉 **[https://swachhsetu-imgz.onrender.com](https://swachhsetu-imgz.onrender.com)**

### Demo Accounts:
| Role | Email | Password |
|------|-------|----------|
| 🛡️ Admin | `admin@demo.com` | `admin123` |
| 👤 Citizen | `citizen@demo.com` | `citizen123` |
| 👷 Worker | `ramesh@demo.com` | `worker123` |

---

## ✨ Features

- 📸 **Photo + GPS Reporting** — 30 second complaint filing
- 🤖 **AI Waste Classification** — Hugging Face auto-detect
- 🧠 **NLP Detection** — Category + Priority (Hindi + English)
- 🗺️ **Interactive Hotspot Map** — Admin visualization
- 👷 **Worker Module** — Task assignment + proof upload
- 📊 **Real-time Analytics** — Live dashboard
- 🔐 **JWT Auth** — Secure role-based access
- 🎨 **Modern UI** — Dark mode, animations, custom cursor

---

## 🛠️ Tech Stack

### Frontend
HTML5 · CSS3 · Vanilla JavaScript · Leaflet.js · OpenStreetMap

### Backend
Python · Flask · SQLAlchemy · Flask-JWT-Extended · Gunicorn

### Database
SQLite with SQLAlchemy ORM

### AI / NLP
Hugging Face Inference API · Custom Hindi + English NLP

### Deployment
Render · GitHub Auto-Deploy

---

## 🏃 Run Locally

```bash
# Clone
git clone https://github.com/THEARDev/swachhsetu.git
cd swachhsetu

# Setup
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r backend/requirements.txt

# Run
cd backend
python app.py