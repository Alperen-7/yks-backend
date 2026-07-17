from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import json

app = FastAPI()

# CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase Veritabanı URL'si
DATABASE_URL = "postgresql://postgres.lqwbxtmghdvgalncxzmi:muhtemelyenibolum.@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Tablo: Öğrenci Kayıtları
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                ad_soyad TEXT,
                hedef_bolum TEXT,
                hedef_universite TEXT,
                kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. Tablo: YKS Çalışma, Soru ve Deneme Kayıtları (YENİ)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_records (
                id SERIAL PRIMARY KEY,
                date TEXT,
                category TEXT,
                lesson TEXT,
                topic TEXT,
                study_type TEXT,
                description TEXT,
                stats JSONB,
                exam_type TEXT,
                quiz_questions JSONB,
                user_answers JSONB,
                quiz_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Bulut Veritabanı (Supabase) tabloları başarıyla hazırlandı!")
    except Exception as e:
        print(f"❌ Veritabanına bağlanırken hata: {e}")

# Sunucu başlarken tabloları kontrol et
init_db()


# ==========================================
# 1. ÖĞRENCİ KAYIT API'Sİ (Senin yazdığın)
# ==========================================
@app.post("/register-student/")
async def register_student(request: Request):
    data = await request.json()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO students (ad_soyad, hedef_bolum, hedef_universite)
        VALUES (%s, %s, %s)
    ''', (
        data.get('ad_soyad'),
        data.get('hedef_bolum'),
        data.get('hedef_universite')
    ))
    
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success", "message": "Öğrenci başarıyla kaydedildi!"}


# ==========================================
# 2. YKS TAKİP: YENİ ÇALIŞMA/DENEME KAYDETME API'Sİ
# ==========================================
@app.post("/save-record/")
async def save_record(request: Request):
    data = await request.json()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO study_records (
            date, category, lesson, topic, study_type, description, 
            stats, exam_type, quiz_questions, user_answers, quiz_score
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        data.get('date'),
        data.get('category'),
        data.get('lesson'),
        data.get('topic'),
        data.get('studyType'),
        data.get('description'),
        json.dumps(data.get('stats')) if data.get('stats') else None,
        data.get('examType'),
        json.dumps(data.get('quizQuestions')) if data.get('quizQuestions') else None,
        json.dumps(data.get('userAnswers')) if data.get('userAnswers') else None,
        data.get('quizScore', 0)
    ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"status": "success", "message": "Çalışma Supabase'e kaydedildi!"}


# ==========================================
# 3. YKS TAKİP: YÖNETİCİ PANELİ İÇİN KAYITLARI ÇEKME API'Sİ
# ==========================================
@app.get("/get-records/")
async def get_records():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM study_records ORDER BY date ASC")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {"status": "success", "data": records}


# ==========================================
# 4. YKS TAKİP: ÖSYM SORULARI (Şimdilik boş dönecek)
# ==========================================
@app.get("/get-questions/")
async def get_questions(category: str = None, lesson: str = None, topic: str = None, limit: int = 1):
    # İleride veritabanına soru eklersen buradan çekeceksin. 
    # Şimdilik boş liste döner, frontend hata vermeden kaydı tamamlar.
    return {"status": "success", "data": []}
