# 🔍 Agentic Docs RAG Explorer

יישום RAG (Retrieval-Augmented Generation) מתקדם לניהול ותשאול תיעוד של כלי Agentic Coding, הכולל תמיכה מובנית בסביבות רשת מסוננות (NetFree).

## 📌 תיאור הפרויקט

המערכת מנהלת ומאפשרת לתשאל את קבצי ה-Markdown של כלי קידוד אוטונומיים (Agentic Coding Tools) כמו:
- **Cursor** - כלי AI לעריכת קוד
- **Claude Code** - עוזר קידוד מבוסס Claude
- **Windsurf** - סביבת פיתוח חכמה
- **Kiro** - AI agent לתכנות

הפרויקט מורכב מ-3 שלבים עם 3 קבצים מרכזיים:

### 🎯 שלב א' - MVP ([main.py](main.py))
חיפוש סמנטי בסיסי עם Embeddings וקטוריים - מאפשר לשאול שאלות כלליות ולקבל תשובות המבוססות על הקשר סמנטי.

### 🎯 שלב ב' - Event-Driven Workflow ([workflow.py](workflow.py))
ארכיטקטורה מבוססת אירועים עם ולידציות, ניתובים חכמים, וניהול state - מערכת מתקדמת שמטפלת בזרימה מדורגת.

### 🎯 שלב ג' - Data Extraction + Router ([extractor.py](extractor.py))
חילוץ נתונים מובנה מקבצי ה-md + Router אוטומטי שמחליט בין חיפוש סמנטי לשליפה מובנית.

---

## 🛠️ טכנולוגיות

| טכנולוגיה | תפקיד | גרסה |
|-----------|-------|------|
| **LlamaIndex** | Framework ל-RAG | Latest |
| **Cohere** | Embeddings + LLM (multilingual) | embed-v3.0 |
| **Pinecone** | Vector Database | Serverless |
| **Gradio** | ממשק משתמש אינטראקטיבי | Latest |
| **pip-system-certs** | תמיכה בתעודות SSL (NetFree) | Latest |
| **Pydantic** | Validation & Structured Output | v2 |
| **Python** | שפת הפיתוח | 3.10+ |

---

## 🌐 תמיכה בסביבת נטפרי (NetFree Support)
הפרויקט כולל פתרונות ייחודיים לעבודה בסביבה מסוננת:
- **SSL Verification**: שימוש ב-`pip-system-certs` המאפשר לפייתון להכיר בתעודות האבטחה של נטפרי.
- **Hybrid Storage Fallback**: המערכת מזהה אוטומטית חסימות רשת (כמו שגיאה 418) ועוברת לשימוש ב-`SimpleVectorStore` מקומי לשמירה על רציפות העבודה.

---

## 📦 התקנה

### דרישות מקדימות
- Python 3.10 ומעלה
- חשבון Cohere וחשבון Pinecone (Free Tiers)

### שלבי ההתקנה

```bash
# 1. שכפול/הורדת הפרויקט
cd Rag

# 2. יצירת סביבה וירטואלית (מומלץ)
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate

# 3. התקנת כל החבילות הנדרשות (כולל תמיכת SSL לנטפרי)
pip install llama-index-core llama-index-embeddings-cohere llama-index-llms-cohere llama-index-vector-stores-pinecone pinecone-client gradio python-dotenv pydantic pip-system-certs

# 4. הגדרת קובץ .env
cp .env.example .env
Gemini נטפרי
‫Gem בהתאמה אישית
Gemini נטפרי אמר
הבנתי בדיוק. את רוצה שהקובץ המאוחד יהיה מבוסס על המבנה המפורט ששלחת, אבל שיכלול בתוכו את התיקונים הטכניים שעשינו (נטפרי, SSL ו-Fallback) כדי שהפרויקט יהיה מושלם להגשה.

הנה הקובץ המלא והסופי. את יכולה להעתיק את כל התוכן מהבלוק למטה ולהדביק אותו ב-README.md:

Markdown
# 🔍 Agentic Docs RAG Explorer

יישום RAG (Retrieval-Augmented Generation) מתקדם לניהול ותשאול תיעוד של כלי Agentic Coding, הכולל תמיכה מובנית בסביבות רשת מסוננות (NetFree).

## 📌 תיאור הפרויקט

המערכת מנהלת ומאפשרת לתשאל את קבצי ה-Markdown של כלי קידוד אוטונומיים (Agentic Coding Tools) כמו:
- **Cursor** - כלי AI לעריכת קוד
- **Claude Code** - עוזר קידוד מבוסס Claude
- **Windsurf** - סביבת פיתוח חכמה
- **Kiro** - AI agent לתכנות

הפרויקט מורכב מ-3 שלבים עם 3 קבצים מרכזיים:

### 🎯 שלב א' - MVP ([main.py](main.py))
חיפוש סמנטי בסיסי עם Embeddings וקטוריים - מאפשר לשאול שאלות כלליות ולקבל תשובות המבוססות על הקשר סמנטי.

### 🎯 שלב ב' - Event-Driven Workflow ([workflow.py](workflow.py))
ארכיטקטורה מבוססת אירועים עם ולידציות, ניתובים חכמים, וניהול state - מערכת מתקדמת שמטפלת בזרימה מדורגת.

### 🎯 שלב ג' - Data Extraction + Router ([extractor.py](extractor.py))
חילוץ נתונים מובנה מקבצי ה-md + Router אוטומטי שמחליט בין חיפוש סמנטי לשליפה מובנית.

---

## 🛠️ טכנולוגיות

| טכנולוגיה | תפקיד | גרסה |
|-----------|-------|------|
| **LlamaIndex** | Framework ל-RAG | Latest |
| **Cohere** | Embeddings + LLM (multilingual) | embed-v3.0 |
| **Pinecone** | Vector Database | Serverless |
| **Gradio** | ממשק משתמש אינטראקטיבי | Latest |
| **pip-system-certs** | תמיכה בתעודות SSL (NetFree) | Latest |
| **Pydantic** | Validation & Structured Output | v2 |
| **Python** | שפת הפיתוח | 3.10+ |

---

## 🌐 תמיכה בסביבת נטפרי (NetFree Support)
הפרויקט כולל פתרונות ייחודיים לעבודה בסביבה מסוננת:
- **SSL Verification**: שימוש ב-`pip-system-certs` המאפשר לפייתון להכיר בתעודות האבטחה של נטפרי.
- **Hybrid Storage Fallback**: המערכת מזהה אוטומטית חסימות רשת (כמו שגיאה 418) ועוברת לשימוש ב-`SimpleVectorStore` מקומי לשמירה על רציפות העבודה.

---

## 📦 התקנה

### דרישות מקדימות
- Python 3.10 ומעלה
- חשבון Cohere וחשבון Pinecone (Free Tiers)

### שלבי ההתקנה

```bash
# 1. שכפול/הורדת הפרויקט
cd Rag

# 2. יצירת סביבה וירטואלית (מומלץ)
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate

# 3. התקנת כל החבילות הנדרשות (כולל תמיכת SSL לנטפרי)
pip install llama-index-core llama-index-embeddings-cohere llama-index-llms-cohere llama-index-vector-stores-pinecone pinecone-client gradio python-dotenv pydantic pip-system-certs

# 4. הגדרת קובץ .env
cp .env.example .env
🔑 הגדרת מפתחות API
ערוך את הקובץ .env והוסף את המפתחות שלך:

קטע קוד
COHERE_API_KEY=your_cohere_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
⚠️ חשוב: אל תשתף את קובץ ה-.env! הוא כבר מוגדר ב-.gitignore.

🚀 שימוש והרצה
🎯 שלב א' - MVP (חיפוש סמנטי בסיסי)
Bash
python main.py
ממשק Gradio יפתח ב: http://127.0.0.1:7860

🎯 שלב ב' - Event-Driven Workflow
Bash
python workflow.py
זרימת העבודה: StartEvent -> [validate_input] -> QueryEvent -> [retrieve] -> ResultsEvent -> [synthesize] -> StopEvent.

🎯 שלב ג' - Data Extraction + Router
בניית המאגר (פעם ראשונה): python extractor.py --rebuild
הרצה רגילה: python extractor.py

📊 ארכיטקטורה ותרשימי זרימה
ניתן לצפות בתרשימי הזרימה האינטראקטיביים בקבצים הבאים:

צפייה בתרשים Workflow מלא (HTML)

צפייה במפת זרימת אירועים (HTML)

🔧 פתרון בעיות נפוצות
❌ "SSL Certificate Error"
פתרון: המערכת משתמשת ב-pip-system-certs. ודא שהרצת את פקודת ההתקנה של החבילה בטרמינל.

❌ "Pinecone Error 418"
בעיה: חסימה של נטפרי על כתובת ה-API של האינדקס.
פתרון: אין צורך בפעולה ידנית - המערכת תבצע Fallback אוטומטי לאחסון מקומי.

👥 קרדיטים
פותח: [שמך]

קורס: RAG & Agentic Coding

תאריך: מרץ 2026

🎉 בהצלחה בשימוש במערכת!