Key Logger – README

סקירה

סקריפט שמאזין להקשות מקלדת, מרכז אותן לפי דקה, מציג לקונסול וכותב לקובץ בפורמט אחיד. כולל אפשרות להצפין/לפענח את קובץ הלוג.


רכיבים
	•	KeyLoggerService – אחראי על מצב הלוג:
	•	global_log: רשימת בלוקים שנאספו.
	•	log_l: בלוק נוכחי: { "YYYY-MM-DD HH:MM": [keys...] }
	•	long_str: שרשור תווים לצורך בדיקות רצף.
	•	KeyLoggerManager – מתזמר אירועי מקלדת:
	•	key_for_log(event): מעבד כל מקש, סוגר בלוקים על SPACE/ESC, כותב/מדפיס.
	•	starting_listening(): מפעיל את המאזין (pynput.keyboard.Listener) על on_release.
	•	FileWriter – כתיבת לוג לקובץ keyfile.txt בפורמט זהה לקונסול:

<דקה>
[<רשימת מקשים/תווים כפי שנקלטו>]


	•	Encryptor – ניהול מפתח Fernet והצפנה/פענוח של קבצים:
	•	make_key() טוען/יוצר מפתח (key.key).
	•	encrypt_file(src, dst, key) / decrypt_file(src, dst, key).
	•	NetworkWriter – Placeholder (טרם ממומש).



זרימת עבודה
	1.	המאזין קורא ל־key_for_log על כל שחרור מקש.
	2.	האירוע מתווסף לבלוק הנוכחי תחת מפתח הדקה (YYYY-MM-DD HH:MM).
	3.	SPACE:
	•	הבלוק הנוכחי נוסף אל global_log ונאפס (ללא כתיבה לקובץ).
	4.	ESC:
	•	הבלוק הנוכחי נוסף אל global_log.
	•	כל הבלוקים ב־global_log מודפסים לקונסול בפורמט:

<דקה>
[<רשימת מקשים/תווים>]


	•	כל הבלוקים נכתבים לקובץ keyfile.txt באותו פורמט.
	•	המאזין נעצר.

	5.	לאחר העצירה, מתבצעת הדגמת הצפנה/פענוח של keyfile.txt → keyfile.encrypted → keyfile_decrypted.txt.

הערה: מקש רגיל נשמר כתו (key.char), מקש מיוחד נשמר כאובייקט Key.xxx (למשל Key.esc), ולכן יוצג כך גם בקובץ.



דרישות
	•	Python 3.10+
	•	חבילות:
	•	pynput
	•	cryptography

התקנה:

pip install pynput cryptography




הפעלה

הרצה רגילה (ממסוף):

python main.py

עצירת המאזין וכיתוב לוג מתבצעים בלחיצת ESC.



קבצים ותוצרים
	•	keyfile.txt – לוג טקסטואלי, בפורמט:

2025-08-28 14:40
['ע', 'ו', 'ל', 'ם', Key.space]
2025-08-28 14:41
['w', 'o', 'r', 'l', 'd', Key.enter, Key.esc]


	•	keyfile.encrypted – גרסה מוצפנת של הקובץ.
	•	keyfile_decrypted.txt – פענוח של הקובץ המוצפן.
	•	key.key – מפתח Fernet.



API עיקרי (מחלקות/מתודות)

# Service
KeyLoggerService.make_long_str(key)
KeyLoggerService.make_dict(key)

# Manager
KeyLoggerManager.key_for_log(key)        # callback ל-on_release
KeyLoggerManager.starting_listening()    # הפעלת listener

# FileWriter
FileWriter.outing_to_file(character_dict_or_list)

# Encryptor
Encryptor.make_key() -> bytes
Encryptor.encrypt_file(src, dst, key)
Encryptor.decrypt_file(src, dst, key)




התאמות/דגשים
	•	ברירת המחדל: כתיבה לקובץ מתבצעת רק בעת ESC (כל הבלוקים).
אם נדרש לכתוב גם על SPACE, ניתן להוסיף קריאה ל־writer.outing_to_file(...) בענף SPACE (לא מופעל כברירת מחדל).
	•	פורמט הקובץ והקונסול זהים: שורת זמן ולאחריה repr של הרשימה לאותה דקה.

⸻

אבטחה
	•	מפתח ההצפנה נשמר ב־key.key. שמור עליו בנפרד מגיבוי/הפצה של קבצי הלוג.
	•	Encryptor לא מוחק/מחליף את קובץ המקור; קבצי פלט מוגדרים בנפרד.
