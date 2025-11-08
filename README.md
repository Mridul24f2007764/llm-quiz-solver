🧠 LLM Quiz Solver — Python Project

📧 Student Email ID
24f2007764@ds.study.iitm.ac.in

🚀 Project Overview

This project implements an API endpoint that automatically solves quizzes involving data sourcing, preparation, analysis, and visualization using Large Language Models (LLMs) and automation tools.

The system:

Receives a POST request with { email, secret, url }

Validates the secret (returns 400/403/200 appropriately)

Visits the given quiz URL using a headless browser (Playwright)

Extracts or downloads data (HTML tables, CSV, JSON, etc.)

Computes the correct answer (e.g., sums, averages, filters)

Submits the answer to the given submit URL

Handles multi-step quizzes automatically within 3 minutes

🧰 Tools & Technologies
Category	Tools Used
Language	Python 3
Framework	Flask (for API endpoint)
Automation	Playwright (headless Chromium browser)
Data Handling	Pandas, BeautifulSoup
Configuration	python-dotenv
Deployment	Render / Railway (HTTPS endpoint)
Version Control	Git & GitHub
License	MIT License
⚙️ System Requirements

Python 3.10 or higher

pip package manager

Internet connection (for Playwright browser install)

Works on Windows, macOS, or Linux

🗂️ Folder Structure
llm-quiz-solver-python/
├── server.py          # Main Flask API server
├── solver.py          # Background solver logic using Playwright
├── requirements.txt   # Python dependencies
├── .env.example       # Example environment variable file
├── README.md          # Project documentation
└── LICENSE            # MIT License file

🔧 Environment Variables

Copy .env.example to .env and update the values:

EMAIL=24f2007764@ds.study.iitm.ac.in
SECRET=S3cr3t-Tk_9x7qB2!
PORT=5000


⚠️ Do NOT commit .env to GitHub.

💻 Installation & Setup
Step 1: Clone the repository
git clone https://github.com/your-username/llm-quiz-solver-python.git
cd llm-quiz-solver-python

Step 2: Create & activate a virtual environment

Windows:

python -m venv venv
venv\Scripts\Activate.ps1


Mac/Linux:

python3 -m venv venv
source venv/bin/activate

Step 3: Install dependencies
pip install -r requirements.txt
python -m playwright install

Step 4: Run the Flask server
python server.py


You should see:

 * Running on http://127.0.0.1:5000

🧪 Testing the Endpoint (Demo)

You can test your API locally using the provided demo quiz simulator.

Run this command in another terminal:

curl -X POST http://127.0.0.1:5000/ \
  -H "Content-Type: application/json" \
  -d '{
    "email":"24f2007764@ds.study.iitm.ac.in",
    "secret":"S3cr3t-Tk_9x7qB2!",
    "url":"https://tds-llm-analysis.s-anand.net/demo"
  }'


Expected:

Immediate HTTP 200 JSON → {"message": "Accepted, solving started"}

Your terminal logs show:

Visiting: https://tds-llm-analysis.s-anand.net/demo
Found submit URL: ...
Computed answer: ...
Submit response: { "correct": true }

☁️ Deployment

Deploy to Render or Railway for HTTPS hosting.

Example Render setup:

Build Command:

pip install -r requirements.txt && python -m playwright install --with-deps


Start Command:

python server.py


Add environment variables: EMAIL, SECRET, PORT

Use the generated HTTPS URL in the Google Form.

🧾 Example API Responses
✅ Valid Secret
{
  "message": "Accepted, solving started"
}

❌ Invalid Secret
{
  "error": "Invalid secret"
}

⚠️ Invalid JSON
{
  "error": "Invalid JSON payload"
}
