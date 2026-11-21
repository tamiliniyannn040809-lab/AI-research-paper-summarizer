# PaperLens — AI Research Paper Summarizer

A professional, beginner-friendly Generative AI project built with Python, Streamlit, Groq, and PyPDF.

## Main features

1. **PDF summarization** — upload a research-paper PDF and generate a structured summary.
2. **Research comparison** — compare 2–4 papers by objectives, methodology, findings, similarities, and differences.
3. **Chat with research paper** — ask questions about one or more uploaded papers. The app retrieves relevant text passages using simple keyword matching and sends those passages plus the paper summary to the AI model.
4. **Download** — export a summary or comparison as a Markdown (`.md`) file.

## Project structure

```text
AI_Research_Paper_Summarizer_Final/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── utils/
│   ├── __init__.py
│   ├── pdf_processor.py
│   └── ai_engine.py
│
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

---

# PART A — Run the project in VS Code (Windows 11)

## Step 1: Install the requirements

Install Python 3.10 or newer and VS Code if they are not already installed.

1. Download the ZIP from ChatGPT.
2. Right-click the ZIP and choose **Extract All**.
3. Open VS Code.
4. Select **File → Open Folder**.
5. Select the extracted `AI_Research_Paper_Summarizer_Final` folder.
6. Select **Terminal → New Terminal**.

Make sure the terminal path ends with the project folder name. If it does not, use `cd` to move into the extracted folder.

## Step 2: Create a virtual environment

Run these commands one at a time in the VS Code PowerShell terminal:

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this command for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

## Step 3: Install Python packages

```powershell
python -m pip install --upgrade pip
```

```powershell
pip install -r requirements.txt
```

Wait until installation completes.

## Step 4: Get a Groq API key

1. Open https://console.groq.com/
2. Sign in or create an account.
3. Create an API key in the API keys section.
4. Copy the key and keep it private.

Do not paste the key into Python source code, GitHub, screenshots, or assignment documents.

## Step 5: Add your API key locally (recommended)

Create a new file named `.streamlit/secrets.toml` inside the `.streamlit` folder.

The full path should be:

```text
AI_Research_Paper_Summarizer_Final/.streamlit/secrets.toml
```

Put this inside it, replacing the example with your own key:

```toml
GROQ_API_KEY = "your_real_groq_api_key"
```

The `.gitignore` file excludes this secrets file from Git.

Alternatively, enter the key into the password field in the app's sidebar while testing locally.

## Step 6: Start the website

In the VS Code terminal, run:

```powershell
streamlit run app.py
```

Streamlit should open the app in your browser. If it does not, copy the Local URL shown in the terminal (usually `http://localhost:8501`) into your browser.

## Step 7: Test all four features

### Test 1 — PDF summarization
- Upload a text-based research-paper PDF.
- Open the **Summarize paper** tab.
- Select the paper.
- Click **Generate summary**.
- Check the methodology, findings, limitations, and quick summary.
- Download the Markdown file.

### Test 2 — Research comparison
- Upload at least two different research-paper PDFs.
- Open **Compare research**.
- Select two papers.
- Click **Compare selected papers**.
- Review the comparison and download it.

### Test 3 — Chat with research paper
- Open **Chat with paper**.
- Select a paper.
- Ask a question such as: `What research problem does this paper address?`
- Click **Ask PaperLens**.
- Check whether the answer is supported by the displayed paper context.

### Test 4 — Multiple papers
- Select more than one paper in the chat tab.
- Ask: `What are the main differences between these studies?`

---

# PART B — Deploy for assignment checking (Streamlit Community Cloud)

## Step 1: Create a GitHub account

Open https://github.com/ and sign in or create an account.

## Step 2: Create a repository

1. Click **New repository**.
2. Repository name: `ai-research-paper-summarizer`
3. Select **Public** if your assignment evaluator needs to inspect the source code.
4. Click **Create repository**.

Before uploading, verify that `.env` and `.streamlit/secrets.toml` are NOT included.

## Step 3: Upload the project files

Upload the contents of the extracted project folder to the repository. Keep the same folder structure. The root of the repository must contain `app.py` and `requirements.txt`.

Do not upload the ZIP as the only repository file; upload the extracted files and folders.

## Step 4: Open Streamlit Community Cloud

1. Go to https://share.streamlit.io/
2. Sign in using GitHub.
3. Click **Create app**.
4. Select your repository: `ai-research-paper-summarizer`.
5. Select branch: `main`.
6. Main file path: `app.py`.
7. Click **Deploy**.

## Step 5: Configure the API key on Streamlit

After the app is created:

1. Open the app menu / **Manage app**.
2. Open **Settings** and find **Secrets**.
3. Paste:

```toml
GROQ_API_KEY = "your_real_groq_api_key"
```

4. Save the secrets.
5. Wait for the app to restart.

Do not add your API key to GitHub repository files.

## Step 6: Test the deployed app

1. Open the public Streamlit app URL.
2. Upload a small text-based PDF.
3. Generate a summary.
4. Test comparison with two PDFs.
5. Ask a question in the chat tab.
6. Test the Markdown download.

Submit the deployed URL to your assignment evaluator.

---

# Troubleshooting

## `streamlit is not recognized`
Activate the virtual environment and run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## `ModuleNotFoundError`
Check that the virtual environment is activated, then run:

```powershell
pip install -r requirements.txt
```

## API authentication error
- Check that the API key is correct.
- Check that there are no extra spaces around the key.
- Confirm that the key is active in the Groq console.
- For Streamlit Cloud, check the app's Secrets settings.

## Model unavailable or rate limit
The model list and API limits can change. Try the other model in the sidebar if it is available to your Groq account. Check the provider dashboard for current access and limits.

## PDF has no extracted text
Some PDFs are scanned images rather than text-based documents. This version does not include OCR. Test with a PDF where you can select and copy the text.

---

# How the application works

1. The user uploads a PDF.
2. PyPDF extracts text page-by-page.
3. The text is split into overlapping chunks to handle longer papers.
4. The Groq-hosted language model summarizes each chunk and combines the notes into a structured summary.
5. For comparisons, the model analyzes the summaries of selected papers.
6. For chat, the app selects relevant text chunks using keyword matching and sends those passages with the paper summary to the model.
7. Streamlit displays the response and provides a Markdown download.

## Limitations and responsible use

- This is an educational prototype, not a peer-review system.
- Scanned image-only PDFs are not supported without OCR.
- Chat retrieval uses simple keyword matching, not a vector database.
- API access, model names, rate limits, and pricing are controlled by the AI provider and may change.
- AI can misunderstand technical content or omit details. Verify all important claims, numbers, and page references against the original paper.
- Do not upload confidential, private, or restricted research documents unless you have permission.
