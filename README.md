# 🎯 Resume ↔ JD Matcher

An intelligent, full-stack application that compares a candidate's resume against a job description using Google's Gemini AI. The app provides a detailed match score, skill gap analysis, and actionable suggestions to improve the resume for the target role.

![Resume Matcher Screenshot](https://via.placeholder.com/800x450.png?text=Resume+Matcher+App+Screenshot)

## 🚀 Tech Stack
* **Frontend:** React, Vite, Tailwind CSS, Framer Motion, React Three Fiber (3D Background)
* **Backend:** FastAPI (Python 3)
* **AI Provider:** Google Gemini API (`gemini-2.5-flash`)
* **PDF Parsing:** `pdfplumber`

## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/resume-jd-matcher.git
cd resume-jd-matcher
```

### 2. Backend Setup
Ensure you have Python 3.10+ installed, then set up the FastAPI backend:
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -e backend/
```

Add your Gemini API Key:
1. Copy the example environment file: `cp .env.example .env`
2. Open `.env` and add your key (get one at [Google AI Studio](https://aistudio.google.com/)):
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

Start the backend server:
```bash
uvicorn backend.main:app --reload --port 8000
```
The API will run at `http://localhost:8000`.

### 3. Frontend Setup
In a new terminal window, set up the React frontend:
```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
```
The application will open in your default browser at `http://localhost:5173`.

## 🔮 Future Improvements
* **PDF Export:** Allow users to export the generated feedback as a styled PDF report.
* **History:** Save past JD comparisons in local storage or a lightweight SQLite database to track applications over time.
* **ATS Strict Mode:** Add a toggle to enforce exact-match keywords only, simulating rigid ATS systems.
* **Cover Letter Generator:** Automatically draft a cover letter based on the matched skills and the job description.
