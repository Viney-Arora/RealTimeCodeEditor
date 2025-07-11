# 📝 Real-Time Collaborative Document Editor

A lightweight web application built with **FastAPI** that allows multiple users to collaborate on documents in real time, with basic AI-powered suggestions.

## ✨ Features
✅ Real-time editing using WebSockets  
✅ User authentication (email & password)  
✅ AI suggestions for grammar/tips (using a dummy or simple API)  
✅ Version history (save & view older versions)  
✅ Simple and responsive frontend with Quill.js and Bootstrap

---

## 📦 Stack
- Backend: **Python**, **FastAPI**, **SQLAlchemy**
- Frontend: **HTML**, **Bootstrap**, **Quill.js**
- Database: Postgres 
- AI: Simple API route returning dummy suggestions

---

## 🚀 Live demo
*To Check, follow the this link below (Railway)*
https://realtimecodeeditor-production.up.railway.app/
---

## 🛠️ Local setup

### 1️⃣ Clone & install
```bash
git clone https://github.com/Viney-Arora/RealTimeCodeEditor.git
cd documentEditorBackend
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux

pip install -r requirements.txt
