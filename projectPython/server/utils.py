# server/utils.py

import re

def count_lines(text: str) -> int:
    """
    פונקציית עזר לספירת שורות במחרוזת טקסט.
    תשמש את ה-Analyzer לבדיקת אורך הקובץ הכולל.
    """
    if not text.strip():
        return 0
    return text.count('\n') + 1


def is_non_english(text: str) -> bool:
    """
    בודקת האם מחרוזת מכילה תווים שאינם אותיות באנגלית, מספרים או קו תחתון.
    מחזירה True אם נמצאו אותיות בשפות אחרות (עברית, רוסית וכו') או תווים מיוחדים (אימוג'י).
    """
    # [^...] אומר: חפש תו שאינו אנגלית, מספר או קו תחתון
    invalid_chars_regex = re.compile(r'[^a-zA-Z0-9_]')

    # אם נמצא תו כזה, search יחזיר אובייקט והפונקציה תחזיר True
    return bool(invalid_chars_regex.search(text))

def clean_old_graphs(directory: str):
    import os
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith(".png"):
                try:
                    os.remove(os.path.join(directory, filename))
                except Exception:
                    # אם הקובץ תפוס כרגע ע"י מערכת ההפעלה, נדלג עליו במקום שהשרת יתרסק
                    pass