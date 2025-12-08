# 🤖 AI Code Translator & Verifier

### 🌍 Translate • Verify • Store • Reuse

The **AI Code Translator & Verifier** is a full-stack application that uses **OpenAI GPT-4o** to translate code across programming languages (Python, Java, C, C++) and verify the correctness of translations by executing both source and translated code on identical test cases.  
All translations and reports are automatically stored in **MongoDB Atlas** and displayed through a modern, responsive **web UI**.

---

## 🚀 Key Features

✅ **AI-Powered Translation**
- Uses OpenAI GPT-4o for precise, syntax-aware code translation.  
- Supports Python ↔ Java ↔ C ↔ C++.

✅ **Automatic Verification**
- Generates random or user-provided test inputs.
- Executes both source and translated code.
- Compares outputs and calculates a pass/fail rate.

✅ **MongoDB Atlas Integration**
- Every translation (verified or not) is stored with metadata, code, and reports.
- Retrieve past jobs instantly via the History sidebar.

✅ **Modern Developer UI**
- Split-view layout for Source (left) and Translated (right).
- Live translation, verification reports, and a collapsible job history panel.

✅ **Persistent Local Backups**
- Each translation creates an `artifacts/<job_id>/` folder for offline reference.

---

## 🧠 System Architecture

User (Web UI)
│
▼
FastAPI Backend (api/main.py)
│
├── Translator (OpenAI GPT-4o via translator/)
├── Verifier (Execution in Python, Java, C, C++)
├── MongoDB Atlas (storage/mongo.py)
▼
Results → History → UI Sidebar


---

## 🧩 Tech Stack

| Layer | Tools / Libraries |
|--------|--------------------|
| **Frontend** | HTML, CSS, Vanilla JS |
| **Backend** | FastAPI (Python) |
| **AI Engine** | OpenAI GPT-4o |
| **Database** | MongoDB Atlas |
| **Verification** | Pytest, subprocess runners (C/Java/C++) |
| **Environment** | Python 3.10+, Node.js, Git |
| **OS** | Windows (tested) |

---

## 📂 Project Structure
```
code-translator/
│
├── api/ 				# FastAPI backend (routes, services, schemas)
├── translator/ 		# AI translation layer (OpenAI integration)
├── verifier/ 			# Functional equivalence testing logic
├── storage/ 			# MongoDB + file persistence
├── ui/ 				# HTML/CSS/JS frontend
├── artifacts/ 			# Auto-generated translation jobs
├── scripts/ 			# PowerShell scripts for running/dev
├── .env 				# Secrets (OpenAI, MongoDB)
├── requirements.txt 	# Python dependencies
├── pyproject.toml	 	# Project config
└── README.md 			# You're here
```
2️⃣ Create a Virtual Environment
python -m venv .venv
.\.venv\Scripts\activate


3️⃣ Install Dependencies
pip install -r requirements.txt


4️⃣ Configure Environment Variables
Create a .env file in the project root:
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
DB_NAME=code_translator
COLLECTION_NAME=job_history


5️⃣ Run the Development Server
powershell -ExecutionPolicy Bypass -File .\scripts\dev_server.ps1

🖥️ Using the App
Enter Source Code in the left pane.
Select Source Language and Target Language.
Enter Function Name (for test generation).
(Optional) Provide custom inputs in JSON format.
Click Translate or Translate & Verify.
See translated code on the right and report below.
All jobs appear in the History sidebar.


💾 MongoDB Atlas Storage Schema
Each document in job_history:
{
  "job_id": "20251110-193855-61dfba8f",
  "timestamp": "2025-11-10T19:38:55Z",
  "source_lang": "python",
  "target_lang": "java",
  "function_name": "gcd",
  "param_count": 2,
  "source_code": "def gcd(a,b): return b if a==0 else gcd(b%a,a)",
  "translated_code": "public static int gcd(int a, int b){ return a==0 ? b : gcd(b%a,a); }",
  "verified": true,
  "pass_rate": 100.0,
  "report": {...}
}


🧪 Testing
Run all tests:
pytest

Or specific modules:
pytest tests/test_e2e.py


Common test files:
File										Purpose
test_e2e.py									Tests full translation → verification pipeline
test_equivalence_local.py					Confirms output equivalence
test_runners.py								Validates code execution for all languages
test_testgen.py								Tests random input generation
conftest.py									Shared pytest setup

🧩 Folder Highlights
Folder					Key Files							Purpose
api/					main.py, services.py				FastAPI endpoints & logic
translator/				openai_model.py, prompts.py			AI translation core
verifier/				compare.py, runners/				Code execution & comparison
storage/				mongo.py, files.py					Database & artifact management
ui/						index.html, app.js, styles.css		Frontend interface
artifacts/				job folders							Stores source, translated, report


🧩 Future Improvements
Add more language support (Go, Rust, JavaScript)
Integrate Monaco/CodeMirror editors for better UX
Add re-translation & diff view
Cloud deployment (Docker + Google Cloud Run)
User authentication and collaboration features
