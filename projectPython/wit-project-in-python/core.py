import requests  # חובה לייבא בראש הקובץ לשם שליחת בקשות HTTP
import os
import json
import shutil
import uuid
import filecmp
import datetime

WIT_DIR = ".wit"
STAGING_DIR = os.path.join(WIT_DIR, "staging")
COMMITS_DIR = os.path.join(WIT_DIR, "commits")
METADATA_FILE = os.path.join(WIT_DIR, "metadata.json")


# ---------- פונקציות עזר ----------

def load_ignore():
    ignore_list = [WIT_DIR]
    if os.path.exists(".witignore"):
        with open(".witignore", "r") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    ignore_list.append(stripped)
    return ignore_list


def is_ignored(path, ignore_list):
    norm_path = os.path.normpath(path)
    for ignore in ignore_list:
        norm_ignore = os.path.normpath(ignore)
        if norm_path == norm_ignore or norm_path.startswith(norm_ignore + os.sep):
            return True
    return False


def are_directories_different(path1, path2):
    if not os.path.exists(path1) or not os.path.exists(path2):
        return True

    comparison = filecmp.dircmp(path1, path2)
    if comparison.diff_files or comparison.left_only or comparison.right_only:
        return True

    for subdir in comparison.common_dirs:
        if are_directories_different(
            os.path.join(path1, subdir),
            os.path.join(path2, subdir)
        ):
            return True

    return False


def has_uncommitted_changes(head_path):
    for root, _, files in os.walk(head_path):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), head_path)
            work_path = os.path.join(".", rel_path)

            if not os.path.exists(work_path):
                return True

            if not filecmp.cmp(
                os.path.join(head_path, rel_path),
                work_path,
                shallow=False
            ):
                return True
    return False


# ---------- לוגיקה מרכזית ----------

def init_repo():
    if os.path.exists(WIT_DIR):
        return "Repository already initialized"

    os.makedirs(STAGING_DIR, exist_ok=True)
    os.makedirs(COMMITS_DIR, exist_ok=True)

    with open(METADATA_FILE, "w") as f:
        json.dump({"head": None}, f)

    if not os.path.exists(".witignore"):
        with open(".witignore", "w") as f:
            f.write(f"{WIT_DIR}/\n.witignore\n")

    return "Initialized empty wit repository"


def add(path):
    if not os.path.exists(path):
        return "Path does not exist"

    ignore_list = load_ignore()

    def add_single_file(src_path):
        if is_ignored(src_path, ignore_list):
            return
        dest_path = os.path.join(STAGING_DIR, src_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src_path, dest_path)

    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                add_single_file(os.path.join(root, file))
    else:
        add_single_file(path)

    return f"Added {path} to staging area"


def commit(message):
    if not os.listdir(STAGING_DIR):
        return "Nothing to commit (staging is empty)"

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    head_id = metadata.get("head")
    head_path = os.path.join(COMMITS_DIR, head_id) if head_id else None

    if head_path and not are_directories_different(STAGING_DIR, head_path):
        return "No changes detected since last commit. Commit aborted."

    commit_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_path = os.path.join(COMMITS_DIR, commit_id)
    shutil.copytree(STAGING_DIR, commit_path)
    metadata["head"] = commit_id
    metadata[commit_id] = {"message": message, "timestamp": timestamp}
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f)

    return f"Commit {commit_id} created at {timestamp}: {message}"


def status():
    ignore_list = load_ignore()

    staged_files = []
    for root, _, files in os.walk(STAGING_DIR):
        for file in files:
            staged_files.append(
                os.path.relpath(os.path.join(root, file), STAGING_DIR)
            )

    untracked_files = []
    for root, _, files in os.walk("."):
        if is_ignored(root, ignore_list):
            continue
        for file in files:
            full_path = os.path.join(root, file)
            if not is_ignored(full_path, ignore_list):
                rel = os.path.relpath(full_path, ".")
                if rel not in staged_files:
                    untracked_files.append(rel)

    return staged_files, untracked_files


def checkout(commit_id):
    ignore_list = load_ignore()
    commit_path = os.path.join(COMMITS_DIR, commit_id)

    if not os.path.exists(commit_path):
        return "Unknown commit id"

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    head_id = metadata.get("head")
    if head_id:
        head_path = os.path.join(COMMITS_DIR, head_id)
        if has_uncommitted_changes(head_path):
            return "Uncommitted changes exist. Checkout blocked."

    for item in os.listdir("."):
        if item == WIT_DIR or is_ignored(item, ignore_list):
            continue
        if os.path.isdir(item):
            shutil.rmtree(item)
        else:
            os.remove(item)

    for item in os.listdir(commit_path):
        src = os.path.join(commit_path, item)
        if os.path.isdir(src):
            shutil.copytree(src, item)
        else:
            shutil.copy2(src, item)

    if os.path.exists(STAGING_DIR):
        shutil.rmtree(STAGING_DIR)
    shutil.copytree(commit_path, STAGING_DIR)

    metadata["head"] = commit_id
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f)

    return f"Checked out commit {commit_id}"



def push_commit_to_server():
    # 1. קריאת קובץ המטא-דאטה כדי לזהות מהו ה-Commit האחרון (HEAD)
    if not os.path.exists(METADATA_FILE):
        return {"error": "Repository not initialized. Please run init first."}

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    head_id = metadata.get("head")

    # 2. בדיקה האם המשתמש ביצע לפחות Commit אחד ב-WIT
    if not head_id:
        return {"error": "Nothing to push. Please commit your changes first."}

    # 3. הגדרת הנתיב המלא של התיקייה ששומרת את קבצי ה-Commit הזה
    commit_path = os.path.join(COMMITS_DIR, head_id)
    if not os.path.exists(commit_path):
        return {"error": f"Commit folder for ID {head_id} was not found."}

    # 4. איסוף דינמי של כל קבצי הפייתון (.py) שנשמרו בתוך ה-Commit הנוכחי
    python_files = []
    for root, _, files in os.walk(commit_path):
        for file in files:
            if file.endswith('.py'):
                full_file_path = os.path.join(root, file)
                python_files.append(full_file_path)

    if not python_files:
        return {"error": "No Python (.py) files found in the latest commit to analyze."}

    # 5. הכנת מערך הבקשה (Payload) ופתיחת הקבצים לקריאה בינארית (rb)
    files_payload = []
    opened_files = []

    try:
        for file_path in python_files:
            f = open(file_path, "rb")
            opened_files.append(f)
            # os.path.relpath דואג לשלוח את שם הקובץ המקורי (ללא נתיב ה-commit הזמני)
            original_name = os.path.relpath(file_path, commit_path)
            files_payload.append(("files", (original_name, f)))

        # 6. שליחת הקבצים האמיתיים בבקשת POST לשרת ה-FastAPI שרץ ברקע
        url = "http://localhost:8000/alerts"
        response = requests.post(url, files=files_payload, timeout=10)

        if response.status_code == 200:
            return response.json()  # החזרת מילון התוצאות (אזהרות וקישורים לגרפים)
        else:
            return {"error": f"Server returned error code {response.status_code}"}

    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to CodeGuard server. Is uvicorn running on port 8000?"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

    finally:
        # 7. סגירה בטוחה של כל הקבצים מהזיכרון
        for f in opened_files:
            f.close()
