import sqlite3


def get_connection():
    return sqlite3.connect('kobi_data.db')


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urunler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            stok_miktari INTEGER DEFAULT 0,
            fiyat REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS siparisler (
            id INTEGER PRIMARY KEY,
            musteri_adi TEXT NOT NULL,
            durum TEXT,
            tahmini_teslim TEXT
        )
    ''')

    conn.commit()
    conn.close()

    print("Veritabanı oluşturuldu.")


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    urunler = [
        ('Zeytinyağı 1L', 50, 450.0),
        ('Biber Salçası 500gr', 20, 150.0),
        ('Biber Salçası 1kg', 15, 300.0),
        ('Biber Salçası 5kg', 30, 1400.0),
        ('Domates Salçası 500gr', 20, 160.0),
        ('Domates Salçası 1kg', 15, 300.0),
        ('Domates Salçası 5kg', 20, 1400.0),
        ('Süzme Çiçek Balı', 15, 300.0),
        ('El Yapımı Erişte', 0, 85.0),
        ('Kurutulmuş Patlıcan', 100, 150.0),
        ('Kurutulmuş Domates', 100, 200.0),
        ('Salamur Köy Peyniri', 50, 300.0),
        ('Köy Tereyağı', 70, 800.0),
        ('Asma Yaprak', 100, 1500.0),
        ('Üzüm Sirkesi', 80, 200.0),
        ('Elma Sirkesi', 100, 180.0),
        ('Kara Dut Reçeli', 50, 300.0),
        ('Kayısı Reçeli', 80, 300.0),
        ('Dut Pekmezi', 60, 400.0),
        ('Nar Ekşisi', 70, 270.0),
        ('Süzme Bal', 50, 600.0),
        ('Köz Biber', 100, 200.0),
        ('Köz Patlıcan', 100, 200.0),
        ('Tarhana', 200, 350.0),
        ('Dolmalık Kuru Biber', 100, 260.0),
        ('Dolmalık Kuru Patlıcan', 100, 260.0)
    ]

    siparisler = [
        (1001, 'Beyza', 'Hazırlanıyor', '15 Mayıs 2026'),
        (1002, 'Ali', 'Kargoya Verildi', '12 Mayıs 2026'),
    ]

    cursor.execute("SELECT count(*) FROM urunler")

    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO urunler (isim, stok_miktari, fiyat) VALUES (?, ?, ?)",
            urunler
        )

        cursor.executemany(
            "INSERT INTO siparisler VALUES (?, ?, ?, ?)",
            siparisler
        )

        print("Örnek veriler eklendi.")

    conn.commit()
    conn.close()


def get_order_by_id(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, musteri_adi, durum, tahmini_teslim
        FROM siparisler
        WHERE id=?
    """, (order_id,))

    result = cursor.fetchone()

    conn.close()

    return result


def get_product_by_name(product_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT isim, stok_miktari, fiyat
        FROM urunler
        WHERE isim LIKE ?
    """, (f"%{product_name}%",))

    result = cursor.fetchall()

    conn.close()

    return result


if __name__ == "__main__":
    init_db()
    seed_data()