import matplotlib.pyplot as plt
import os
# --- השינוי המרכזי: מייבאים את פונקציית הניקוי מ-utils ---
from utils import clean_old_graphs

OUTPUT_DIR = "static_graphs"

def generate_histogram(function_lengths: list):
    """
    מייצרת גרף היסטוגרמה המציג את התפלגות אורכי הפונקציות בקוד ושומרת אותו כ-PNG.
    """
    # אם אין פונקציות בכלל בקוד, אין טעם לייצר גרף ריק
    if not function_lengths:
        return

    # יצירת משטח ציור חדש ונקי
    plt.figure()

    # יצירת ההיסטוגרמה בפועל
    # bins=5 קובע שהנתונים יחולקו ל-5 קבוצות טווחים שונות
    # edgecolor='black' מוסיף מסגרת שחורה לעמודות בשביל יופי וקריאות
    plt.hist(function_lengths, bins=5, color='skyblue', edgecolor='black')

    # הוספת כותרת ושמות לצירים
    plt.title("Distribution of Function Lengths", fontsize=14, fontweight='bold')
    plt.xlabel("Function Length (Lines of Code)", fontsize=12)
    plt.ylabel("Number of Functions", fontsize=12)

    # התאמה אוטומטית של רכיבי הגרף שלא יחתכו בשוליים
    plt.tight_layout()

    # שמירת הגרף כתמונה בתיקייה שהוגדרה בראש הקובץ
    plt.savefig(f"{OUTPUT_DIR}/histogram.png")

    # סגירת הציור הנוכחי כדי לפנות זיכרון ולמנוע ערבוב עם הגרף הבא (העוגה)
    plt.close()
def generate_pie_chart(issue_counts: dict):
    """
    מייצרת דיאגרמת עוגה המציגה את התפלגות סוגי השגיאות בקוד ושומרת אותה כ-PNG.
    מציגה רק קטגוריות שבהן קיימת לפחות שגיאה אחת.
    """
    # סינון המילון: נשמור רק קטגוריות שיש בהן שגיאות (ערך גדול מ-0)
    filtered_issues = {k: v for k, v in issue_counts.items() if v > 0}

    # אם אין שגיאות בכלל בכל הפרויקט - אין טעם לייצר גרף עוגה ריק
    if not filtered_issues:
        return

    # חילוץ הלייבלים (שמות השגיאות) והערכים (הכמויות) לרשימות נפרדות
    labels = list(filtered_issues.keys())
    values = list(filtered_issues.values())

    # יצירת משטח ציור חדש ונקי
    plt.figure()

    # יצירת דיאגרמת העוגה
    # autopct='%1.1f%%' מוסיף אוטומטית כיתוב אחוזים על כל פרוסה
    # startangle=140 מסובב את הגרף להתחלה אסתטית יותר
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140,
            colors=['#ff9999','#6bbf75','#ffcc99','#529ecc','#b284be'])

    # הוספת כותרת לגרף
    plt.title("Issues Distribution by Type", fontsize=14, fontweight='bold')

    # התאמה אוטומטית של רכיבי הגרף שלא יחתכו בשוליים
    plt.tight_layout()

    # שמירת הגרף כתמונה בתיקייה שהוגדרה בראש הקובץ
    plt.savefig(f"{OUTPUT_DIR}/pie_chart.png")

    # סגירת הציור הנוכחי כדי לפנות זיכרון ולמנוע ערבוב עם הגרף הבא
    plt.close()


def generate_bar_chart(files_data: list):
    """
    מייצרת גרף מקלות המציג את כמות הבעיות הכוללת בכל קובץ שנסרק, ושומרת אותו כ-PNG.
    """
    if not files_data:
        return

    file_names = []
    issue_totals = []

    # חילוץ הנתונים מתוך הרשימה שהתקבלה מהשרת
    for file_result in files_data:
        # שמירת שם הקובץ לציר ה-X
        file_names.append(file_result["file_name"])

        # חישוב סך כל הבעיות בקובץ הנוכחי מתוך מילון ה-issue_counts לשם ציר ה-Y
        total_issues = sum(file_result["stats"]["issue_counts"].values())
        issue_totals.append(total_issues)

    # יצירת משטח ציור חדש ונקי
    plt.figure()

    # יצירת גרף המקלות בפועל
    plt.bar(file_names, issue_totals, color='indianred', edgecolor='black', width=0.5)

    # הוספת כותרת ושמות לצירים
    plt.title("Number of Issues per File", fontsize=14, fontweight='bold')
    plt.xlabel("Files", fontsize=12)
    plt.ylabel("Total Issues", fontsize=12)

    # סיבוב שמות הקבצים ב-45 מעלות כדי שלא יחפפו אחד את השני אם השמות ארוכים
    plt.xticks(rotation=45, ha='right')

    # התאמה אוטומטית של השוליים כדי ששמות הקבצים למטה לא ייחתכו
    plt.tight_layout()

    # שמירת הגרף כתמונה
    plt.savefig(f"{OUTPUT_DIR}/bar_chart.png")

    # סגירת הציור הנוכחי כדי לפנות זיכרון
    plt.close()


def generate_all_plots(all_files_results: list):
    """
    פונקציית העל שמקבלת את תוצאות האנליזה של כל הקבצים,
    ממזגת את הנתונים הסטטיסטיים, מייצרת את כל הגרפים ומחזירה את נתיבי התמונות.
    """
    # 1. הכנת הסביבה ומחיקת גרפים ישנים
    clean_old_graphs(OUTPUT_DIR)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 2. מבני נתונים לאיחוד הסטטיסטיקה מכל הקבצים
    aggregated_function_lengths = []

    total_issue_counts = {
        "function_length": 0,
        "file_length": 0,
        "unused_variable": 0,
        "missing_docstring": 0,
        "non_english_name": 0
    }

    # 3. עיבוד ושימוש במשתנה all_files_results שנתקבל בפונקציה
    for file_data in all_files_results:
        # file_data הוא מילון שמגיע מ-CodeAnalyzer.run_all_checks()
        stats = file_data["stats"]

        # א) איחוד כל אורכי הפונקציות לרשימה אחת גדולה
        aggregated_function_lengths.extend(stats["function_lengths"])

        # ב) סכימת כמות הבעיות מכל הקבצים יחד
        for issue_type, count in stats["issue_counts"].items():
            total_issue_counts[issue_type] += count

    # 4. הפעלת פונקציות הציור עם הנתונים המאוחדים
    # א) יצירת היסטוגרמה (מקבלת רשימת אורכים)
    generate_histogram(aggregated_function_lengths)

    # ב) יצירת דיאגרמת עוגה (מקבלת מילון מונים מאוחד)
    generate_pie_chart(total_issue_counts)

    # ג) יצירת גרף מקלות (מקבלת את כל הרשימה הגולמית כדי לדעת כמה בעיות יש *בכל קובץ*)
    generate_bar_chart(all_files_results)

    # 5. החזרת רשימת נתיבי הקבצים שנוצרו
    return [
        f"{OUTPUT_DIR}/histogram.png",
        f"{OUTPUT_DIR}/pie_chart.png",
        f"{OUTPUT_DIR}/bar_chart.png"
    ]