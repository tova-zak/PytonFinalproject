# CodeGuard – Automated Static Code Analysis & Visualization System
CodeGuard is an automated static code analysis system designed to detect quality issues, coding standard violations, and function length metrics. The system consists of a FastAPI backend server that performs the analysis and generates visual charts, alongside a client-side version control simulator (based on `wit` commands) that streams the code for analysis.
---
## 🚀 Key Features
* **Abstract Syntax Tree (AST) Analysis:** Deep structural and logical analysis of source code by parsing it into a node tree, without executing the code.
* **Code Quality Metrics:**
  * **File Length Check:** Detects and alerts on excessively long code files (over 200 lines).
  * **Function Length Check:** Identifies functions exceeding 20 lines to encourage modular coding.
  * **Docstring Verification:** Finds functions missing internal documentation (Missing Docstrings).
  * **Unused Variables:** Detects variables that were assigned but never read or utilized.
  * **Bonus Language Support:** Scans identifiers and alerts if they contain non-English characters (e.g., Hebrew variable names).
* **Visual Analytics Generator:** Automatically generates `matplotlib` charts aggregating statistics from all analyzed files:
  * **Histogram:** Displays the distribution of function lengths across the project.
  * **Pie Chart:** Breaks down the distribution of error and warning types.
  * **Bar Chart:** Compares the total number of issues per file to pinpoint problematic modules.
---
## 📂 System Architecture
The project is decoupled into two primary components:
### 1. Backend Server (`/server`)
* `main.py`: The central FastAPI server exposing async endpoints (`/alerts` and `/analyze`) and serving static graph files.
* `analyzer.py`: Contains the `CodeAnalyzer` class that performs structural analysis using Python's built-in `ast` module.
* `visualizer.py`: The rendering component responsible for aggregating data metrics and outputting PNG charts.
* `utils.py`: Helper functions for line counting, character validation, and clearing outdated graph files from disk.
### 2. Client Side (`/wit-project-in-python`)
A CLI system simulating core version control operations:
* `wit.py add`: Adds code files to the local staging area.
* `wit.py commit`: Creates a permanent snapshot freezing the current project state.
* `wit.py push`: Sends the committed files via an HTTP POST request to the server, retrieving a detailed JSON report and direct graph URLs.
---
## 🛠️ Installation & Setup
### Prerequisites
* Python 3.10 or higher
* Active virtual environment (`.venv`)
### 1. Install Dependencies
Run the following command in your terminal to install the core libraries:
```bash
pip install fastapi uvicorn matplotlib fastapi-staticfiles requests

```

### 2. Run the Server

Open a terminal, navigate to the server directory, and start the application:

```bash
cd server
python main.py

```

## The server will start listening at: `http://127.0.0.1:8000`.

## 💻 Usage Guide

While the server is running in the background, open a **separate new terminal** for the client and navigate to the `wit` project directory:

1. **Add a code file for analysis (e.g., `test_code.py`):**
```bash
python wit.py add test_code.py

```


2. **Commit your changes locally to create a new version:**
```bash
python wit.py commit -m "execute static analysis test"

```


3. **Push the code to the server for evaluation:**
```bash
python wit.py push

```



---

## 📊 System Outputs & Visualizations

Upon executing the `push` command, the FastAPI server will process the files and:

1. Print a clean, structured JSON payload in the client terminal detailing specific warnings for each file.
2. Generate/update 3 analytical charts inside the `server/static_graphs/` directory:
* `histogram.png`
* `pie_chart.png`
* `bar_chart.png`
You can view these graphs at any time directly in your browser using the static links served by the backend:



* `http://localhost:8000/graphs/pie_chart.png`
* `http://localhost:8000/graphs/histogram.png`

```

```
