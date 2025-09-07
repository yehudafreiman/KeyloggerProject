סקירת מערכת – Keylogger Management System

מבוא
המערכת מספקת פתרון מלא לניטור, איסוף וניהול לוגים של הקלדות (Keylogs) ממספר מחשבים מרוחקים. המערכת מורכבת משלושה חלקים עיקריים:
	1.	סוכן מקומי (Keylogger Agent – keylogger.py) רץ על מחשב הקצה, אוסף את ההקלדות ושולח אותן בצורה מאובטחת לשרת.
	2.	שרת מרכזי (Flask Backend – app.py) מנהל את התקשורת עם הסוכנים, שומר את הלוגים ומספק ממשק API לניהול משתמשים ולניהול מכונות.
	3.	ממשק משתמש (Frontend – HTML) מספק ממשק גרפי נוח הכולל התחברות, בחירת מכונה, הצגת נתוני לוגים, חיפוש מתקדם וביצוע פעולות כמו מחיקה או רענון.

רכיבי המערכת

הסוכן (keylogger.py)
	•	מנטר לחיצות מקשים בזמן אמת באמצעות הספרייה pynput.
	•	שומר את המידע בפורמט JSON מקומי.
	•	שולח את הלוגים לשרת בפרקי זמן קבועים כשהם מוצפנים בעזרת cryptography.

שורות רדומות עבור Windows
בקובץ קיימות שורות המוגדרות כהערות (comments):

בייבוא ספריות:

# import win32gui

במחלקת KeyLoggerService, מתודת get_active_application():

if platform.system() == "Windows":
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd) or "Unknown"

שורות אלו מיועדות להרצה בסביבת Windows בלבד.
ברירת מחדל (לינוקס / מק): השורות נשארות כבויות.
ב־Windows: יש להסיר את סימן ה־# כדי להפעילן, להרדים את השורות המסומנות עבור מק ולהתקין את החבילה pywin32.

דרישות התקנה לסוכן:
	•	לינוקס / מק: pip install pynput cryptography requests
	•	Windows: בנוסף, נדרש pip install pywin32

השרת (app.py)
נבנה באמצעות Flask ומספק ממשק REST API לניהול:
	•	ניהול משתמשים:
	•	/api/addUser – הוספת משתמש
	•	/api/deleteUser – מחיקת משתמש
	•	/api/validateUser – אימות כניסה
	•	ניהול מכונות:
	•	/api/getTargetMachinesList – קבלת רשימת מכונות
	•	/api/getData/ – הצגת נתוני לוגים למכונה מסוימת
	•	/api/deleteLogs/ – מחיקת לוגים
	•	/api/toggle – הפעלה/כיבוי של איסוף לוגים

דרישות התקנה לשרת:
pip install flask pynput cryptography

ממשק המשתמש (Frontend)
	•	log_in.html – מאפשר התחברות, הוספת משתמש ומחיקת משתמש. הכפתורים מעוצבים באופן אחיד לפי צבעי פעולה.
	•	WebsiteView.html – מציג את רשימת המכונות כלחצנים, כולל כפתור התנתקות.
	•	individualUinit.html – מציג לוגים של מכונה, כולל אפשרות חיפוש לפי זמן, אפליקציה או מילה, מחיקת לוגים ורענון, וכן מתג להפעלה או עצירה של איסוף הלוגים.

הפעלה

שרת:

pip install flask pynput cryptography
python app.py

ברירת המחדל: http://127.0.0.1:5000

סוכן:

pip install pynput cryptography requests
python keylogger.py

	•	במק / לינוקס: אין לשנות את הקוד.
	•	ב־Windows: יש להסיר את סימן ה־# מהשורות הרדומות, להרדים את השורות עבור מק ולהתקין בנוסף את pywin32.
