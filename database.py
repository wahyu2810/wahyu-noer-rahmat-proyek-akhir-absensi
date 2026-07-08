import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Check if application is running as a bundled executable (via PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

def get_connection():
    """Get database connection for PostgreSQL"""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "absensi_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password,
        cursor_factory=RealDictCursor
    )
    return conn

def init_database():
    """Initialize PostgreSQL database with tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            nama VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Absensi table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS absensi (
            id SERIAL PRIMARY KEY,
            nama VARCHAR(100) NOT NULL,
            kelas VARCHAR(50),
            tanggal VARCHAR(20) NOT NULL,
            jam_masuk VARCHAR(20),
            jam_keluar VARCHAR(20),
            status VARCHAR(50) DEFAULT 'Hadir',
            keterangan TEXT,
            latitude VARCHAR(50),
            longitude VARCHAR(50)
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_default_data():
    """Insert default users"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        row = cursor.fetchone()
        if row and row['count'] == 0:
            cursor.execute('''
                INSERT INTO users (username, password, role, nama)
                VALUES (%s, %s, %s, %s)
            ''', ('dosen1', '123456', 'dosen', 'Dr. Saeful'))
            
            cursor.execute('''
                INSERT INTO users (username, password, role, nama)
                VALUES (%s, %s, %s, %s)
            ''', ('mahasiswa1', '123456', 'mahasiswa', 'Wahyu Noer Rahmat'))
            
            cursor.execute('''
                INSERT INTO users (username, password, role, nama)
                VALUES (%s, %s, %s, %s)
            ''', ('mahasiswa2', '123456', 'mahasiswa', 'Siti Nurhaliza'))
            
            conn.commit()
    except Exception as e:
        print(f"Error inserting default data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
    insert_default_data()
    print("Database initialized successfully!")