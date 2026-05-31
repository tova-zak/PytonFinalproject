from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from typing import List
from analyzer import CodeAnalyzer
from visualizer import generate_all_plots

app = FastAPI(title="CodeGuard Backend")

# שיתוף תיקיית הגרפים כסטטית כדי שיהיה אפשר לגשת אליהם דרך לינק בדפדפן
app.mount("/graphs", StaticFiles(directory="static_graphs"), name="graphs")


@app.post("/alerts")
async def get_alerts(files: List[UploadFile] = File(...)):
    """
    נקודת קצה המקבלת קבצי קוד, מנתחת אותם ומחזירה אך ורק רשימת אזהרות מהירה בפורמט JSON.
    """
    all_alerts = {}

    # מעבר בלולאה על כל הקבצים שנשלחו בבקשה
    for file in files:
        try:
            # קריאת תוכן הקובץ בצורה אסינכרונית מהזיכרון/דיסק הזמני
            file_bytes = await file.read()

            # המרת מערך הבייטים למחרוזת טקסט רגילה (UTF-8)
            content = file_bytes.decode("utf-8")

            # יצירת מופע חדש של האנלייזר עבור הקובץ הנוכחי
            analyzer = CodeAnalyzer(content, file.filename)

            # הרצת כל ארבעת הבדיקות הסטטיסטיות (אורך, דוקסטרינג, משתנים, עברית)
            result = analyzer.run_all_checks()

            # אם נמצאו אזהרות בקובץ הנוכחי, נשמור אותן תחת שם הקובץ במילון המרכזי
            if result["alerts"]:
                all_alerts[file.filename] = result["alerts"]

        except Exception as e:
            # טיפול במקרה של קובץ פגום או שגיאת קידוד (למשל אם הועלה קובץ תמונה בטעות)
            all_alerts[file.filename] = [f"Failed to analyze file due to error: {str(e)}"]

    # החזרת תשובת JSON מובנית למשתמש
    return {
        "status": "success",
        "alerts": all_alerts
    }

@app.post("/analyze")
async def analyze_code(files: List[UploadFile] = File(...)):
    """
    Endpoint 2: /analyze (POST)
    - עושה בדיוק את אותו הדבר כמו /alerts, אבל בנוסף:
    - אוסף את ה-stats מכל הקבצים ומעביר אותם לפונקציה generate_all_plots מה-visualizer.
    - מחזיר בתשובה גם את האזהרות וגם קישורים (URLs) ישירים לצפייה בגרפים שנוצרו, למשל:
      "http://localhost:8000/graphs/pie_chart.png"
    """
    all_results = []
    all_alerts = {}

    for file in files:
        content = (await file.read()).decode("utf-8")
        analyzer = CodeAnalyzer(content, file.filename)
        result = analyzer.run_all_checks()
        all_results.append(result)
        if result["alerts"]:
            all_alerts[file.filename] = result["alerts"]

    # יצירת הגרפים על בסיס הנתונים שנאספו
    graph_paths = generate_all_plots(all_results)

    # בניית קישורים דינמיים עבור המשתמש
    graph_links = [f"http://localhost:8000/graphs/{path.split('/')[-1]}" for path in graph_paths]

    return {
        "status": "success",
        "alerts": all_alerts,
        "graphs": graph_links
    }

# פקודה להרצת השרת מהטרמינל: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
