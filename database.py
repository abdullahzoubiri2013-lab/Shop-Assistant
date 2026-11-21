import sqlite3

def init_db():
    conn = sqlite3.connect('shop_database.db')
    cursor = conn.cursor()
    
    # جدول السلع والمخزون مع مسار الصورة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            quantity INTEGER,
            min_stock INTEGER,
            image_path TEXT
        )
    ''')
    
    # جدول المعاملات والأرباح للحرفيين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            service_description TEXT,
            cost REAL,
            profit REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول سجل المحادثات مع المساعد الذكي
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("تم إنشاء قاعدة البيانات والجداول بنجاح!")

if __name__ == '__main__':
    init_db()