# 🚀 How to Run "Plan AI City" on Any Other Laptop / Computer

If you share this project folder (or a ZIP of this folder) with a friend, colleague, or examiner, follow these simple steps to run it on their Windows PC.

---

## 📋 Prerequisites (Free - Install Once)
Before running the project, the other laptop needs these two free tools:

1. **Python 3.10 or higher**:
   - Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - ⚠️ **CRITICAL**: During installation, check the box that says:
     `☑ Add python.exe to PATH` *(Very Important)*.

2. **Node.js (LTS version)**:
   - Download: [https://nodejs.org/](https://nodejs.org/) (Click the green **LTS** button and install with default settings).

---

## ⚡ Super Easy Setup (Only 2 Clicks!)

### Step 1: Install Dependencies (Only First Time)
1. Open the project folder on the laptop.
2. Double-click **`INSTALL_ALL.bat`**.
3. It will automatically:
   - Verify Python.
   - Install all backend AI & FastAPI libraries.
   - Verify Node.js.
   - Install all frontend React packages.
4. When finished, press any key to close the window.

---

### Step 2: Start the Project (Every Time You Use It)
1. Double-click **`START_APP.bat`**.
2. This 1-click launcher will automatically:
   - Start the **Backend Server** on port 8000.
   - Start the **Frontend Dev Server** on port 3000.
   - Automatically open your default web browser to:
     👉 **[http://localhost:3000](http://localhost:3000)**

---

## 🗄️ Where Is the Database? Do They Need to Install a Database?
**NO! They do NOT need to install MySQL, PostgreSQL, or MongoDB.**

The project uses **SQLite**, and the complete database file is already included inside the folder at:
```text
backend\plan_ai_city.db
```
All Pan-India cities (Jaipur, Varanasi, Kangra, Chitkul, Mawlynnong, Goa, Delhi, Mumbai, etc.), attractions, places, and registered user accounts are already inside this file.

### How to View the Stored Database:
- Simply double-click **`view_database.bat`** to see all tables (`user_profiles`, `users`, `cities`, `places`) right inside a terminal window!
- Or open `backend\plan_ai_city.db` using the free [DB Browser for SQLite](https://sqlitebrowser.org/).

---

## 💻 Manual Terminal Commands (Alternative for Mac/Linux or Advanced Users)

If running manually in two separate terminal windows:

### Terminal 1: Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --reload
```

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000` in the browser.
