import sqlite3
import os
from datetime import datetime

DB_FILE = "materials.db"
UPLOADS_DIR = "uploads"
CATEGORIES = [
    "أوراق بحثية",
    "تقارير",
    "نماذج Excel",
    "محاضرات",
    "كتب ومراجع",
    "أخرى"
]

def _get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def _ensure_setup():
    """التأكد من وجود المجلدات وقاعدة البيانات والجدول"""
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            author TEXT NOT NULL,
            description TEXT NOT NULL,
            file_path TEXT NOT NULL,
            tags TEXT,
            uploaded_by TEXT,
            upload_date TEXT,
            downloads INTEGER DEFAULT 0,
            rating_sum INTEGER DEFAULT 0,
            rating_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def _row_to_dict(row):
    """تحويل صف من قاعدة البيانات لقاموس متوافق مع باقي الكود"""
    return {
        "id": row["id"],
        "title": row["title"],
        "category": row["category"],
        "author": row["author"],
        "description": row["description"],
        "file_path": row["file_path"],
        "tags": row["tags"].split(",") if row["tags"] else [],
        "uploaded_by": row["uploaded_by"],
        "upload_date": row["upload_date"],
        "downloads": row["downloads"],
        "rating_sum": row["rating_sum"],
        "rating_count": row["rating_count"]
    }

def load_materials():
    """تحميل كل المواد من قاعدة البيانات"""
    _ensure_setup()
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM materials ORDER BY id").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]

def add_material(title, category, author, description, file_path, tags, uploaded_by):
    """إضافة مادة جديدة"""
    _ensure_setup()
    conn = _get_connection()
    tags_str = ",".join(tags) if tags else ""
    upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.execute(
        """INSERT INTO materials
           (title, category, author, description, file_path, tags, uploaded_by, upload_date, downloads, rating_sum, rating_count)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0)""",
        (title, category, author, description, file_path, tags_str, uploaded_by, upload_date)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {
        "id": new_id, "title": title, "category": category, "author": author,
        "description": description, "file_path": file_path, "tags": tags,
        "uploaded_by": uploaded_by, "upload_date": upload_date,
        "downloads": 0, "rating_sum": 0, "rating_count": 0
    }

def increment_downloads(material_id):
    """زيادة عداد التحميلات لمادة معينة"""
    conn = _get_connection()
    conn.execute("UPDATE materials SET downloads = downloads + 1 WHERE id = ?", (material_id,))
    conn.commit()
    conn.close()

def add_rating(material_id, rating):
    """إضافة تقييم لمادة (من 1 لـ 5)"""
    conn = _get_connection()
    conn.execute(
        "UPDATE materials SET rating_sum = rating_sum + ?, rating_count = rating_count + 1 WHERE id = ?",
        (rating, material_id)
    )
    conn.commit()
    conn.close()

def get_average_rating(material):
    """حساب متوسط التقييم لمادة"""
    if material["rating_count"] == 0:
        return 0
    return round(material["rating_sum"] / material["rating_count"], 1)

def search_materials(query="", category=None):
    """البحث عن مواد حسب النص والتصنيف"""
    materials = load_materials()
    results = materials
    if category and category != "الكل":
        results = [m for m in results if m["category"] == category]
    if query:
        query = query.lower()
        results = [
            m for m in results
            if query in m["title"].lower()
            or query in m["description"].lower()
            or query in m["author"].lower()
            or any(query in tag.lower() for tag in m["tags"])
        ]
    return results
