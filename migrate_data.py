import json
import os
from database import _get_connection, _ensure_setup

OLD_FILE = "materials.json"

def migrate():
    _ensure_setup()
    if not os.path.exists(OLD_FILE):
        print("لا يوجد ملف materials.json قديم - لا حاجة للنقل.")
        return

    with open(OLD_FILE, "r", encoding="utf-8") as f:
        old_materials = json.load(f)

    if not old_materials:
        print("ملف materials.json فارغ - لا حاجة للنقل.")
        return

    conn = _get_connection()
    count = 0
    for m in old_materials:
        tags_str = ",".join(m.get("tags", []))
        conn.execute(
            """INSERT INTO materials
               (title, category, author, description, file_path, tags, uploaded_by, upload_date, downloads, rating_sum, rating_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                m.get("title", ""), m.get("category", ""), m.get("author", ""),
                m.get("description", ""), m.get("file_path", ""), tags_str,
                m.get("uploaded_by", ""), m.get("upload_date", ""),
                m.get("downloads", 0), m.get("rating_sum", 0), m.get("rating_count", 0)
            )
        )
        count += 1
    conn.commit()
    conn.close()
    print(f"تم نقل {count} مادة بنجاح إلى قاعدة البيانات materials.db")

if __name__ == "__main__":
    migrate()
