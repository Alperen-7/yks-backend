from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Vercel'deki Next.js sitemizin bu sunucuyla sorunsuz konuşabilmesi için CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DİKKAT: Aşağıdaki tırnak içine Supabase'den aldığın ve şifreni yazdığın bağlantı linkini yapıştır!
# ÖRNEK: "postgresql://postgres:SeninSifren123@db.abcde.supabase.co:5432/postgres"
DATABASE_URL = "postgresql://postgres.lqwbxtmghdvgalncxzmi:muhtemelyenibolum.@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

def get_db_connection():
    # Supabase (PostgreSQL) veritabanına bağlanır
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # PostgreSQL'de otomatik artan ID için AUTOINCREMENT yerine SERIAL kullanılır
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                ad_soyad TEXT,
                hedef_bolum TEXT,
                hedef_universite TEXT,
                kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Bulut Veritabanı (Supabase) tabloları başarıyla oluşturuldu/kontrol edildi!")
    except Exception as e:
        print(f"❌ Veritabanına bağlanırken hata: {e}")

# Sunucu başlarken tablonun var olup olmadığını kontrol et
init_db()

# ==========================================
# ENDPOINT'LER (API ÇIKIŞ KAPILARI)
# ==========================================

@app.post("/register-student/")
async def register_student(request: Request):
    data = await request.json()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # PostgreSQL'de dışarıdan gelen veriler için "?" yerine "%s" kullanılır
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
    
    return {"status": "success", "message": "Öğrenci buluta başarıyla kaydedildi!"}