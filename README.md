# FinPath India

FinPath India is an AI-assisted financial decision support platform built to help users think through financial trade-offs using structured analysis, financial calculations, and explainable recommendations.

This project currently includes:
- A **FastAPI backend** for analysis and API endpoints
- A **React + Vite frontend** for a cleaner user experience
- A base architecture that can later expand into broader life-decision support use cases

---

## Features

- Natural-language financial query input
- FastAPI backend with `/analyze` endpoint
- React frontend for entering scenarios and viewing results
- Interactive API docs with Swagger at `/docs`
- Local development setup for both backend and frontend

---

## Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn

### Frontend
- React
- Vite
- Tailwind CSS

---

## Project Structure

```text
finpath-india/
│
├── app/                  # FastAPI backend
├── finpath-ui/           # React frontend
├── venv/                 # Local Python virtual environment (not pushed to Git)
├── .gitignore
├── README.md
└── requirements.txt
```

---

## How to Clone the Project

```bash
git clone https://github.com/ASRAKSHITH/finpath-india.git
cd finpath-india
```

---

## Backend Setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the virtual environment

#### On Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run this first in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run:

```powershell
.\venv\Scripts\Activate.ps1
```

#### On Windows Command Prompt

```cmd
venv\Scripts\activate.bat
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI backend

```bash
python -m uvicorn app.main:app --reload
```

### 5. Open the backend

Backend base URL:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Open a **new terminal** and make sure you are still in the project root:

```bash
cd finpath-india
```

Then run:

```bash
cd finpath-ui
npm install
npm run dev
```

### Open the frontend

```text
http://localhost:5173
```

---

## Running the Full App

To run the app locally, you need **two terminals**:

### Terminal 1 — Backend

```bash
cd finpath-india
python -m uvicorn app.main:app --reload
```

### Terminal 2 — Frontend

```bash
cd finpath-india\finpath-ui
npm install
npm run dev
```

Then open:

- Frontend: `http://localhost:5173`
- Backend docs: `http://127.0.0.1:8000/docs`

---

## Example Query

You can test the app with a query like:

```text
I have 2 lakh in savings, 1.5 lakh credit card debt at 36 percent interest, and 20000 monthly surplus. Should I repay debt first or invest?
```

---

## Notes

- `venv/` and `node_modules/` are intentionally not pushed to GitHub
- Anyone cloning this repo should recreate the Python environment and run `npm install` locally
- The project is currently in active development and is intended as an MVP / evolving prototype

---

## Future Improvements

- Better structured financial output cards
- Improved recommendation explanations
- User authentication
- Saved analysis history
- Expanded decision types beyond finance

---

## Author

Built by [ASRAKSHITH](https://github.com/ASRAKSHITH)
