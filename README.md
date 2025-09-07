# **Keylogger Management System**

# **קובץ keylogger.py (צד ה-Agent)**
- תפקיד עיקרי: מאזין ללחיצות מקלדת באמצעות ספריית pynput, מאגד תווים למילים (מתעלם מלחיצות מיוחדות חוץ מ-space ו-backspace), משייך לאפליקציה הפעילה ולזמן, ומאחסן בלוגים.  
- שליחה לשרת: כל שנייה שולח את הלוגים המוצפנים לשרת דרך POST לכתובת /api/upload. משתמש ב-Fernet להצפנה.  
- ניהול מצב: Polling כל 2 שניות לשרת (/api/toggle) כדי לבדוק אם להפעיל/לכבות את ה-keylogger.  
- ריצה: רץ כתהליך רקע, ניתן להפסיק עם Ctrl+C.  

# **קובץ app.py (צד ה-Server)**
- תפקיד עיקרי: שרת Flask שמארח API וממשק web. מקבל נתונים מוצפנים, מפענח ומאחסן אותם כקבצי JSON בתיקיות נפרדות לכל מכונה (data ו-decrypted_data).  
- API endpoints:  
  /api/upload – קליטת לוגים מוצפנים  
  /api/toggle – שליטה במצב (GET/POST) לכל מכונה  
  /api/getData/<machine> – החזרת לוגים למכונה ספציפית  
  /api/getTargetMachinesList – רשימת מכונות זמינות  
  /api/deleteLogs/<machine> – מחיקת לוגים  
  /api/addUser, /api/deleteUser, /api/validateUser – ניהול משתמשים (מאוחסנים כקובצי JSON)  
- אחסון: משתמש בתיקיות מקומיות (data, decrypted_data) לאחסון לוגים מוצפנים ומפוענחים.  

# **קבצי HTML (צד ה-Client)**
- log_in.html – דף כניסה עם אימות משתמש (הוספה/מחיקה/אימות)  
- WebsiteView.html – מציג את רשימת המכונות כלחצנים, כולל כפתור התנתקות  
- individualUinit.html – ממשק למכונה אחת: חיפוש בלוגים (לפי זמן, אפליקציה, מילה), הצגת נתונים, מחיקה ורענון  

# **זרימת העבודה**
1. Agent שולח לוגים  
2. Server מקבל ומפענח  
3. Client מציג ומנהל  
- המערכת משתמשת ב-threading כדי להריץ במקביל שליחה, polling והאזנה למקלדת.  

# **התאמה בין macOS ל-Windows**
ב־keylogger.py, בפונקציה get_active_application():  
- Windows (מושבת כברירת מחדל):  
  if platform.system() == "Windows":  
      import win32gui  
      hwnd = win32gui.GetForegroundWindow()  
      return win32gui.GetWindowText(hwnd) or "Unknown"  
  דורש התקנת pywin32  
- macOS (Darwin) (פעיל כברירת מחדל):  
  if platform.system() == "Darwin":  
      from AppKit import NSWorkspace  
      active_app = NSWorkspace.sharedWorkspace().activeApplication()  
      return active_app.get("NSApplicationName", "Unknown")  
  משתמש ב-AppKit (חלק מ-pyobjc)  
- אחר: מחזיר "Unsupported"  

# **ספריות נדרשות להתקנה**
כללי:  
pip install pynput requests cryptography flask  
macOS:  
pip install pyobjc  
Windows (אם מפעילים את הקוד עבור Win32):  
pip install pywin32  

# **דרישות מערכת**
- Python 3.6 ומעלה (דרוש עבור Fernet)  

# **הוראות הרצה**
צד השרת:  
python app.py  
ברירת מחדל: http://127.0.0.1:5000  
צד הסוכן:  
python keylogger.py  
- macOS: אין לשנות את הקוד  
- Windows: יש להסיר # מהשורות המיועדות ל-Windows, להרדים את שורות macOS, ולהתקין בנוסף את pywin32  
