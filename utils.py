import json
import os
from datetime import datetime

DATA_FILE = "materials.json"
UPLOADS_DIR = "uploads"

CATEGORIES = [
    "أوراق بحثية",
    "تقارير",
    "نماذج Excel",
    "محاضرات",
    "كتب ومراجع",
    "أخرى"
]

def _ensure_setup():
    """التأكد من وجود المجلدات والملفات الأساسية"""
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

def load_materials():
    """تحميل كل المواد من ملف JSON"""
    _ensure_setup()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_materials(materials):
    """حفظ قائمة المواد في ملف JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(materials, f, ensure_ascii=False, indent=2)

def add_material(title, category, author, description, file_path, tags, uploaded_by):
    """إضافة مادة جديدة"""
    materials = load_materials()
    new_id = (max([m["id"] for m in materials]) + 1) if materials else 1
    material = {
        "id": new_id,
        "title": title,
        "category": category,
        "author": author,
        "description": description,
        "file_path": file_path,
        "tags": tags,
        "uploaded_by": uploaded_by,
        "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "downloads": 0,
        "rating_sum": 0,
        "rating_count": 0
    }
    materials.append(material)
    save_materials(materials)
    return material

def increment_downloads(material_id):
    """زيادة عداد التحميلات لمادة معينة"""
    materials = load_materials()
    for m in materials:
        if m["id"] == material_id:
            m["downloads"] += 1
            break
    save_materials(materials)

def add_rating(material_id, rating):
    """إضافة تقييم لمادة (من 1 لـ 5)"""
    materials = load_materials()
    for m in materials:
        if m["id"] == material_id:
            m["rating_sum"] += rating
            m["rating_count"] += 1
            break
    save_materials(materials)

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