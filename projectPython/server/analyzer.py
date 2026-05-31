import ast
from utils import count_lines, is_non_english


class CodeAnalyzer:
    def __init__(self, file_content: str, file_name: str):
        self.code = file_content
        self.file_name = file_name
        self.tree = ast.parse(file_content)
        self.alerts = []

        self.stats = {
            "function_lengths": [],
            "issue_counts": {
                "function_length": 0,
                "file_length": 0,
                "unused_variable": 0,
                "missing_docstring": 0,
                "non_english_name": 0
            }
        }

    def check_file_length(self):
        """בדיקת אורך הקובץ הכולל"""
        # שימוש בפונקציית העזר מ-utils:
        total_lines = count_lines(self.code)

        if total_lines > 200:
            self.alerts.append(f"File {self.file_name} is too long ({total_lines} lines).")
            self.stats["issue_counts"]["file_length"] += 1

    def check_functions_and_docstrings(self):
        """
        סורקת את כל הפונקציות בקוד, בודקת את אורכן (מקסימום 20 שורות)
        ומוודא שקיים להן docstring (תיעוד).
        """
        # מעבר על כל הצמתים בעץ ה-AST
        for node in ast.walk(self.tree):
            # סינון: רק צמתים המייצגים הגדרת פונקציה (def)
            if isinstance(node, ast.FunctionDef):
                func_name = node.name

                # 1. בדיקת אורך הפונקציה
                # חישוב שורת סיום פחות שורת התחלה + 1 (כדי לכלול את שורת ה-def עצמה)
                func_length = node.end_lineno - node.lineno + 1

                # שמירת האורך בסטטיסטיקה עבור ההיסטוגרמה (גם אם הפונקציה תקינה)
                self.stats["function_lengths"].append(func_length)

                # בדיקה אם חרג מ-20 שורות
                if func_length > 20:
                    self.alerts.append(
                        f"Function '{func_name}' in {self.file_name} is too long ({func_length} lines)."
                    )
                    self.stats["issue_counts"]["function_length"] += 1

                # 2. בדיקת קיום Docstring
                # ast.get_docstring מחזיר את מחרוזת התיעוד או None אם היא לא קיימת
                docstring = ast.get_docstring(node)

                if not docstring:
                    self.alerts.append(
                        f"Function '{func_name}' in {self.file_name} is missing a docstring."
                    )
                    self.stats["issue_counts"]["missing_docstring"] += 1

    def check_unused_variables(self):
        """
        מזהה משתנים שהוגדרו בקוד (השמה) אך לא נעשה בהם שימוש (קריאה).
        """
        defined_variables = set()  # סט לשמירת משתנים שהוגדרו (Store)
        used_variables = set()  # סט לשמירת משתנים שנקראו (Load)

        # מעבר על כל הצמתים בעץ ה-AST
        for node in ast.walk(self.tree):
            # אנחנו מחפשים צמתים מסוג Name (שמות של משתנים)
            if isinstance(node, ast.Name):

                # אם הקונטקסט הוא Store - המשתנה מוגדר/מקבל ערך
                if isinstance(node.ctx, ast.Store):
                    defined_variables.add(node.id)

                # אם הקונטקסט הוא Load - המשתנה נמצא בשימוש
                elif isinstance(node.ctx, ast.Load):
                    used_variables.add(node.id)

        # משתנים שלא בשימוש הם כאלו שהוגדרו (defined) אבל לא נעזרנו בהם (used)
        unused_variables = defined_variables - used_variables

        # סינון משתני מערכת מובנים או משתנים מיוחדים של פייתון (כמו __name__)
        # וכן משתנים שמתחילים בקו תחתון פנימי שמקובל לפעמים לא להשתמש בהם
        unused_variables = {var for var in unused_variables if not var.startswith('_')}

        # רישום האזהרות ועדכון הסטטיסטיקה
        for var_name in unused_variables:
            self.alerts.append(
                f"Variable '{var_name}' in {self.file_name} is assigned but never used."
            )
            self.stats["issue_counts"]["unused_variable"] += 1

    def check_non_english_variables(self):
        """
        בונוס: סורקת את כל שמות המשתנים והפונקציות בקוד,
        ומתריעה אם הם מכילים תווים שאינם באנגלית (כמו עברית).
        """
        # סט לשמירת שמות שכבר בדקנו, כדי למנוע התראות כפולות על אותו משתנה
        reported_names = set()

        # מעבר על כל הצמתים בעץ ה-AST
        for node in ast.walk(self.tree):
            name_to_check = None

            # מקרה א': הצומת הוא משתנה (ast.Name)
            if isinstance(node, ast.Name):
                name_to_check = node.id

            # מקרה ב': הצומת הוא הגדרת פונקציה (ast.FunctionDef)
            elif isinstance(node, ast.FunctionDef):
                name_to_check = node.name

            # אם מצאנו שם ואסור לפספס אותו
            if name_to_check and name_to_check not in reported_names:
                # שימוש בפונקציית העזר שמימשנו ב-utils
                if is_non_english(name_to_check):
                    # הוספת השם לסט כדי שלא נתריע עליו שוב בקובץ הנוכחי
                    reported_names.add(name_to_check)

                    # רישום ההתראה ועדכון הסטטיסטיקה לגרף
                    self.alerts.append(
                        f"Non-English identifier name found: '{name_to_check}' in {self.file_name}."
                    )
                    self.stats["issue_counts"]["non_english_name"] += 1

    def run_all_checks(self):
        self.check_file_length()
        self.check_functions_and_docstrings()
        self.check_unused_variables()
        self.check_non_english_variables()

        return {
            "file_name": self.file_name,
            "alerts": self.alerts,
            "stats": self.stats
        }