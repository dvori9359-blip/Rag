# 🔍 Agentic Docs RAG Explorer

יישום RAG (Retrieval-Augmented Generation) מתקדם לניהול ותשאול תיעוד של כלי Agentic Coding.

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
| **Pydantic** | Validation & Structured Output | v2 |
| **Python** | שפת הפיתוח | 3.10+ |

---

## 📦 התקנה

### דרישות מקדימות
- Python 3.10 ומעלה
- חשבון Cohere (חינם)
- חשבון Pinecone (free tier)

### שלבי ההתקנה

```bash
# 1. שכפול/הורדת הפרויקט
cd my_target_project

# 2. יצירת סביבה וירטואלית (מומלץ)
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. התקנת כל החבילות הנדרשות
pip install llama-index-core
pip install llama-index-embeddings-cohere
pip install llama-index-llms-cohere
pip install llama-index-llms-openai
pip install llama-index-vector-stores-pinecone
pip install pinecone-client
pip install gradio
pip install python-dotenv
pip install pydantic

# 4. הגדרת קובץ .env (ראה סעיף הבא)
cp .env.example .env
# ערוך את .env והוסף את המפתחות שלך
```

---

## 🔑 הגדרת מפתחות API

### 1. Cohere
1. היכנס ל-[Cohere Dashboard](https://dashboard.cohere.ai)
2. צור API Key חדש
3. התוכנית החינמית כוללת 100 calls לדקה

### 2. Pinecone
1. היכנס ל-[Pinecone Console](https://app.pinecone.io)
2. צור API Key
3. Free tier: 100,000 operations לחודש

### 3. OpenAI (אופציונלי)
1. היכנס ל-[OpenAI Platform](https://platform.openai.com)
2. צור API Key
3. נדרש רק אם רוצים להשתמש ב-GPT במקום Cohere LLM

### הוספת המפתחות ל-.env

ערוך את הקובץ `.env` והוסף:

```env
COHERE_API_KEY=your_cohere_api_key_here
COHERE_EMBED_API_KEY=your_cohere_embed_key_here  # אופציונלי - אותו מפתח
PINECONE_API_KEY=your_pinecone_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # אופציונלי
```

**⚠️ חשוב:** אל תשתף את קובץ ה-.env! הוא כבר מוגדר ב-.gitignore

---

## 🚀 שימוש

### הכנה ראשונית - הוספת מסמכים

לפני שתריץ את המערכת, ודא שיש לך קבצי `.md` באחת מהתיקיות הבאות:

```
my_target_project/
├── .cursor/          # מסמכי Cursor
├── .claude/          # מסמכי Claude Code
├── .windsurf/        # מסמכי Windsurf
├── .kiro/            # מסמכי Kiro
└── docs_ai/          # מסמכים כלליים
```

המערכת תסרוק את כל התיקיות הקיימות ותטעון את כל קבצי ה-md באופן רקורסיבי.

---

### 🎯 שלב א' - MVP (חיפוש סמנטי בסיסי)

```bash
python main.py
```

**מה זה עושה:**
- טוען את כל קבצי ה-md מהתיקיות
- יוצר Embeddings וקטוריים עם Cohere
- מאחסן ב-Pinecone
- מאפשר חיפוש סמנטי חכם
- מציג את המקורות (tool + file + score)

**מתאים לשאלות:**
- "מה הצבע העיקרי שנבחר לדיזיין?"
- "איך מתקינים את המערכת?"
- "מהי הגישה לטיפול בשגיאות?"
- שאלות כלליות שדורשות הבנת הקשר

**ממשק Gradio יפתח ב:** `http://127.0.0.1:7860`

---

### 🎯 שלב ב' - Event-Driven Workflow

```bash
python workflow.py
```

**מה זה עושה:**
- זרימה מבוססת אירועים (Events)
- ולידציה של קלט (ריק/קצר/ארוך)
- חיפוש וקטורי עם Retriever
- סינון לפי Confidence (>0.5)
- טיפול ב-Low Confidence
- ניהול State (Context)

**זרימת העבודה:**
```
StartEvent (query)
    ↓
[validate_input] ✅ בדיקת תקינות
    ↓ QueryEvent
[retrieve] 🔍 חיפוש וקטורי
    ↓ ResultsEvent / NoResultsEvent  
[postprocess] 🔬 סינון confidence
    ↓ SynthesizeEvent / LowConfidenceEvent
[synthesize] 🤖 ניסוח תשובה
    ↓ StopEvent (תשובה סופית)
```

**יתרונות על פני שלב א':**
- ולידציות מובנות
- ניהול שגיאות מתקדם
- logging מפורט
- הפרדה ברורה בין שלבים

**ממשק Gradio יפתח ב:** `http://127.0.0.1:7861`

---

### 🎯 שלב ג' - Data Extraction + Router

**שלב 1: בניית מאגר הנתונים המובנה (פעם ראשונה)**

```bash
python extractor.py --rebuild
```

זה יוצר את `knowledge_db.json` עם:
- **decisions** - החלטות טכניות וארכיטקטוניות
- **rules** - כללים והנחיות לפיתוח
- **warnings** - אזהרות ואזורים רגישים
- **dependencies** - תלויות וספריות חיצוניות

⏱️ זמן בניה: ~2-3 דקות עבור 100 מסמכים

**שלב 2: הרצה רגילה**

```bash
python extractor.py
```

**מה זה עושה:**
- **Router חכם** - מחליט אוטומטית בין חיפוש סמנטי לשליפה מובנית
- **חיפוש סמנטי** - לשאלות כלליות (כמו שלב א')
- **שליפה מובנית** - לשאלות שדורשות רשימות, סינון, עדכניות

**דוגמאות לשאלות - שליפה מובנית:**
- "תן לי רשימה של כל ההחלטות הטכניות"
- "אילו כללי UI הוגדרו?"
- "אילו אזהרות קיימות במערכת?"
- "מה התלויות החיצוניות?"
- "תראה לי החלטות שקשורות ל-DB"

**דוגמאות לשאלות - חיפוש סמנטי:**
- "למה בחרנו ב-Postgres?"
- "מה הגישה לניהול State?"
- "איך מטפלים באימות?"

**ממשק Gradio יפתח ב:** `http://127.0.0.1:7862`

---

## 💬 דוגמאות שאלות לפי סוג

### 🔵 שאלות סמנטיות (Semantic Search)

```
✅ "מה הצבע העיקרי שנבחר לדיזיין של המערכת?"
✅ "איך מתבצעת ההתקנה הראשונית?"
✅ "מהי הגישה המומלצת לטיפול בשגיאות?"
✅ "למה בחרנו ב-Cohere במקום OpenAI?"
✅ "איך עובד מנגנון ה-Caching?"
✅ "מה היתרונות של ארכיטקטורת Event-Driven?"
```

### 🟢 שאלות מובנות (Structured Query)

```
✅ "תן לי רשימה מלאה של כל ההחלטות הטכניות"
✅ "אילו כללי UI חייבים להישמר?"
✅ "אילו אזהרות רגישות קיימות בקוד?"
✅ "מה כל התלויות החיצוניות של הפרויקט?"
✅ "תראה לי החלטות שקשורות ל-database"
✅ "אילו כללים נוגעים ל-authentication?"
```

### 🟡 שאלות מעורבות

```
✅ "מהם השינויים העיקריים שנעשו בארכיטקטורה?"
   → Router ישלח לסמנטי אם רוצים הסבר, למובנה אם רוצים רשימה

✅ "ספר לי על כללי ה-RTL בממשק"
   → Router יחליט לפי ניסוח השאלה
```

---

## 📊 ארכיטקטורה

### 📊 System Architecture

**Workflow Flowchart (Phase B)**
כדי ליצור תרשים זרימה אוטומטי של ה־Workflow, הרץ:

```bash
python workflow.py --map
```

הקובץ `workflow_map.html` ייווצר בתיקיית השורש.

**Header Metadata (Phase A)**
כותרות סעיפים מקבצי Markdown נשמרות כעת בשדה מטא־דאטה חדש בשם `section_header`,
ומאונדקסות ב־Pinecone לשיפור הדיוק בשליפה.

### שלב א' - MVP ([main.py](main.py))

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         ↓
┌────────────────────────────┐
│  Vector Search (Pinecone)  │
│  - Cohere Embeddings       │
│  - Similarity Top 5        │
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│  Postprocessor             │
│  - Similarity > 0.5        │
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│  Response Synthesizer      │
│  - Cohere LLM              │
│  - Mode: compact           │
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│  Answer + Sources          │
│  - tool, file, score       │
└────────────────────────────┘
```

### שלב ב' - Workflow ([workflow.py](workflow.py))

```
StartEvent
    ↓
┌──────────────────────────────┐
│  [validate_input]            │
│  ✅ ריק / קצר / ארוך         │
│  📝 שמירת state              │
└─────────┬────────────────────┘
          ↓ QueryEvent
┌──────────────────────────────┐
│  [retrieve]                  │
│  🔍 VectorIndexRetriever     │
│  📊 Top 5 results            │
└─────────┬────────────────────┘
          ↓ ResultsEvent / NoResultsEvent
┌──────────────────────────────┐
│  [postprocess]               │
│  🔬 Similarity > 0.5         │
│  📉 חישוב best_score         │
└─────────┬────────────────────┘
          ↓ SynthesizeEvent / LowConfidenceEvent
┌──────────────────────────────┐
│  [handle_low_confidence]     │
│  ⚠️  תשובה: נסה אחרת        │
└─────────┬────────────────────┘
          ↓ StopEvent
┌──────────────────────────────┐
│  [synthesize]                │
│  🤖 Response Synthesizer     │
│  📚 הוספת מקורות             │
└─────────┬────────────────────┘
          ↓ StopEvent
┌──────────────────────────────┐
│  Final Answer                │
└──────────────────────────────┘
```

### שלב ג' - Extraction + Router ([extractor.py](extractor.py))

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         ↓
┌────────────────────────────┐
│  [Router Decision]         │
│  - LLM מנתח את השאלה       │
│  - semantic / structured   │
└────────┬───────────────────┘
         ↓
    ┌────┴─────┐
    ↓          ↓
┌─────────┐  ┌──────────────┐
│Semantic │  │  Structured  │
│ Search  │  │    Query     │
│         │  │              │
│Vector DB│  │knowledge_db  │
│Pinecone │  │   .json      │
└────┬────┘  └──────┬───────┘
     │              │
     └──────┬───────┘
            ↓
    ┌───────────────┐
    │ Final Answer  │
    │ + Sources     │
    └───────────────┘
```

### מבנה knowledge_db.json

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-01T10:30:00+02:00",
  "sources": [
    {
      "tool": "cursor",
      "root_path": "./.cursor",
      "files": [...]
    }
  ],
  "items": {
    "decisions": [
      {
        "id": "dec-001",
        "title": "בחירת PostgreSQL",
        "summary": "החלטנו להשתמש ב-Postgres עבור נתונים יחסיים",
        "tags": ["db", "architecture"],
        "source": {
          "tool": "cursor",
          "file": "spec.md",
          "observed_at": "2026-02-15T..."
        }
      }
    ],
    "rules": [...],
    "warnings": [...],
    "dependencies": [...]
  }
}
```

---

## 📁 מבנה הפרויקט

```
my_target_project/
│
├── 📄 main.py                    # שלב א' - MVP
│   ├── load_documents()          # טעינה מכל הכלים
│   ├── initialize_index()        # בניית אינדקס וקטורי
│   └── chat_function()           # ממשק Gradio
│
├── 📄 workflow.py                # שלב ב' - Event-Driven
│   ├── RAGWorkflow               # מחלקת Workflow
│   ├── Events (5 types)          # אירועים
│   ├── Steps (5 handlers)        # שלבי עיבוד
│   └── chat_function()           # ממשק Gradio
│
├── 📄 extractor.py               # שלב ג' - Extraction + Router
│   ├── Pydantic Models (4)       # סכמת נתונים
│   ├── extract_from_document()   # חילוץ עם LLM
│   ├── build_knowledge_db()      # בניית JSON
│   ├── decide_route()            # Router
│   ├── query_structured()        # שליפה מ-JSON
│   ├── query_semantic()          # חיפוש וקטורי
│   └── chat_with_router()        # ממשק Gradio
│
├── 📄 .env                       # מפתחות API (לא ב-Git!)
├── 📄 .env.example               # דוגמה למפתחות
├── 📄 .gitignore                 # הגנת סודות
├── 📄 knowledge_db.json          # DB מובנה (נוצר אוטומטית)
├── 📄 README.md                  # התיעוד הזה
│
└── 📁 [תיקיות מקור]
    ├── .cursor/                  # מסמכי Cursor
    ├── .claude/                  # מסמכי Claude Code
    ├── .windsurf/                # מסמכי Windsurf
    ├── .kiro/                    # מסמכי Kiro
    └── docs_ai/                  # מסמכים כלליים
```

---

## 🔧 פתרון בעיות נפוצות

### ❌ "לא נמצאו מסמכים לאינדקס"

**בעיה:** אין קבצי .md בתיקיות המקור

**פתרון:**
```bash
# ודא שיש לפחות תיקייה אחת עם קבצי .md
ls .cursor/*.md
ls .claude/*.md
ls docs_ai/*.md

# אם אין, צור תיקייה ודוגמה:
mkdir docs_ai
echo "# Test Document" > docs_ai/test.md
```

---

### ❌ "SSL Certificate Error"

**בעיה:** בעיות SSL במערכות ארגוניות

**פתרון:** הקוד כבר מטפל בזה:
```python
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = "0"
```

אם עדיין יש בעיה:
```bash
# Windows
set PYTHONHTTPSVERIFY=0
set REQUESTS_CA_BUNDLE=""

# Mac/Linux
export PYTHONHTTPSVERIFY=0
export REQUESTS_CA_BUNDLE=""
```

---

### ❌ "API Rate Limit Exceeded"

**בעיה:** חרגת מהמגבלות של התוכנית החינמית

**מגבלות:**
- **Cohere Free**: 100 calls/דקה, 1000 calls/חודש
- **Pinecone Free**: 100,000 operations/חודש

**פתרון:**
- המתן דקה ונסה שוב
- שקול שדרוג לתוכנית בתשלום
- צמצם את `similarity_top_k` ל-3 במקום 5

---

### ❌ "Pinecone index dimension mismatch"

**בעיה:** האינדקס הקיים עם ממד שגוי

**פתרון:** הקוד מטפל בזה אוטומטית:
```python
if desc.dimension != EMBEDDING_DIM:
    pc.delete_index(INDEX_NAME)
    pc.create_index(...)  # יוצר מחדש
```

אם זה לא עובד, מחק ידנית ב-[Pinecone Console](https://app.pinecone.io)

---

### ❌ "ModuleNotFoundError: No module named 'X'"

**בעיה:** חבילה לא מותקנת

**פתרון:**
```bash
pip install llama-index-core
pip install llama-index-embeddings-cohere
pip install llama-index-llms-cohere
pip install llama-index-vector-stores-pinecone
pip install pinecone-client
pip install gradio
pip install python-dotenv
```

---

### ❌ "knowledge_db.json לא נמצא"

**בעיה:** לא רצת את extractor.py עם --rebuild

**פתרון:**
```bash
python extractor.py --rebuild
```

זה יוצר את הקובץ. יכול לקחת 2-3 דקות.

---

### ❌ Gradio לא נפתח בדפדפן

**בעיה:** הדפדפן לא נפתח אוטומטית

**פתרון:**
1. חפש בטרמינל את השורה:
   ```
   Running on local URL:  http://127.0.0.1:7860
   ```
2. פתח את ה-URL הזה ידנית בדפדפן

---

## 📈 ביצועים

| פעולה | זמן | הערות |
|-------|-----|-------|
| **טעינה ראשונית** | ~30 שניות | 100 מסמכים |
| **שאילתה סמנטית** | ~2-3 שניות | תלוי ב-API response time |
| **שאילתה מובנית** | ~1-2 שניות | מהיר יותר - רק JSON |
| **בניית knowledge_db** | ~2-3 דקות | 100 מסמכים, חד-פעמי |
| **אינדוקס ל-Pinecone** | ~1 דקה | 100 documents, חד-פעמי |

**טיפים לשיפור ביצועים:**
- צמצם את `similarity_top_k` ל-3
- הגדל את `similarity_cutoff` ל-0.6
- השתמש ב-cache עבור שאלות חוזרות

---

## 🎯 תכונות מתקדמות

### ✅ תמיכה מלאה בעברית
- Cohere embed-multilingual-v3.0
- Cohere command-r LLM
- תשובות בעברית

### ✅ Metadata עשיר
כל chunk כולל:
- `tool` - מקור (cursor/claude/windsurf/kiro)
- `source_file` - שם קובץ
- `file_path` - נתיב מלא
- `title` - כותרת (חילוץ אוטומטי)
- `loaded_at` - timestamp

### ✅ סינון חכם
- **Postprocessor**: רק תוצאות מעל similarity 0.5
- **Deduplication**: ניקוי כפילויות במקורות
- **Best Score**: הצגת score הכי טוב

### ✅ Event-Driven Architecture
- State Management עם Context
- 5 Events שונים
- 5 Steps מוגדרים
- Async support

### ✅ Structured Data Extraction
- 4 סוגי פריטים: decisions, rules, warnings, dependencies
- Pydantic validation
- JSON schema versioning

### ✅ Smart Router
- החלטה אוטומטית: semantic/structured
- LLM-based decision
- Fallback logic

---

## 🧪 בדיקות והרצה

### בדיקה מהירה - שלב א'

```bash
python main.py
```

נסה שאלה:
```
"מה הצבע שנבחר לממשק?"
```

אם התשובה הגיונית → עובד! ✅

### בדיקה מהירה - שלב ב'

```bash
python workflow.py
```

נסה שאלה ריקה:
```
""
```

אמור להחזיר: "❌ שאלה ריקה — נא להזין שאלה."

### בדיקה מהירה - שלב ג'

```bash
python extractor.py --rebuild
python extractor.py
```

נסה שאלה מובנית:
```
"תן לי רשימה של כל ההחלטות"
```

אמור להחזיר רשימה מ-knowledge_db.json

---

## 🤝 תרומה ופידבק

הפרויקט פותח כחלק ממטלה לימודית בקורס "RAG & Agentic Coding".

**לשאלות, הצעות, או דיווח על באגים:**
- פנה למנחה הקורס
- פתח Issue ב-GitHub (אם הפרויקט ציבורי)

---

## 📚 משאבים נוספים

### תיעוד רשמי
- [LlamaIndex Docs](https://docs.llamaindex.ai)
- [Cohere Docs](https://docs.cohere.ai)
- [Pinecone Docs](https://docs.pinecone.io)
- [Gradio Docs](https://gradio.app/docs)

### מאמרים רלוונטיים
- [What is RAG?](https://docs.llamaindex.ai/en/stable/getting_started/concepts.html)
- [Vector Databases Explained](https://www.pinecone.io/learn/vector-database/)
- [Cohere Multilingual Embeddings](https://docs.cohere.ai/docs/multilingual-language-models)

---

## 📄 רישיון

פרויקט לימודי - שימוש חופשי למטרות לימוד ומחקר.

**⚠️ שים לב:**
- מפתחות API הם אישיים - אל תשתף אותם
- קובץ .env אסור להעלות ל-Git
- הפרויקט לא מיועד לשימוש בייצור (production)

---

## 👥 קרדיטים

**פותח:** [שמך]  
**קורס:** RAG & Agentic Coding  
**תאריך:** מרץ 2026  
**טכנולוגיות:** LlamaIndex, Cohere, Pinecone, Gradio

---

## 🎓 מטרות למידה שהושגו

✅ **שלב א':**
- הבנת RAG Pipeline מלא
- עבודה עם Vector Databases
- Embeddings וחיפוש סמנטי
- Integration עם Gradio

✅ **שלב ב':**
- ארכיטקטורת Event-Driven
- State Management
- Workflow Design
- Error Handling מתקדם

✅ **שלב ג':**
- Structured Data Extraction
- LLM-based Routing
- Schema Design
- Hybrid Search

---

## 🚀 שיפורים עתידיים (אופציונלי)

רעיונות להרחבת הפרויקט:

- [ ] Caching עבור שאלות חוזרות
- [ ] מעקב אחר היסטוריית שיחה
- [ ] Multi-turn conversations
- [ ] Fine-tuning של ה-Router
- [ ] Dashboard לניתוח שימוש
- [ ] Export לפורמטים שונים (PDF, Markdown)
- [ ] Integration עם Slack/Discord
- [ ] Monitoring וMetrics
- [ ] A/B testing של strategies
- [ ] Auto-refresh של knowledge_db

---

**🎉 בהצלחה בשימוש במערכת!**

אם נתקלת בבעיות או יש לך שאלות - פנה למנחה הקורס או עיין בסעיף "פתרון בעיות" למעלה.
