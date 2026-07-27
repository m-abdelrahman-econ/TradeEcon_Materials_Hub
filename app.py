import streamlit as st
import pandas as pd
import os
import urllib.parse
from database import load_materials, add_material, search_materials, increment_downloads, add_rating, get_average_rating, CATEGORIES, UPLOADS_DIR
st.set_page_config(page_title="منصة مواد اقتصاديات التجارة الخارجية", page_icon="logo.png", layout="wide")

st.markdown("<style>.stContainer{border-radius:10px;} div[data-testid='stMetric']{background-color:#EFF3F6; border-radius:10px; padding:15px;} </style>", unsafe_allow_html=True)

header_col1, header_col2 = st.columns([1, 5])
with header_col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
with header_col2:
    st.markdown("<h1 style='color:#0F3B5F; margin-bottom:0;'>منصة مواد اقتصاديات التجارة الخارجية</h1><p style='color:#B5A642; font-size:18px; margin-top:0;'>جامعة العاصمة | كلية التجارة وإدارة الأعمال</p>", unsafe_allow_html=True)
    st.caption("إعداد: د. محمد عبد الرحمن")

st.markdown("<hr style='border:1px solid #EFF3F6;'>", unsafe_allow_html=True)

if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=80)
st.sidebar.title("قائمة التنقل")
user_name = st.sidebar.text_input("اسمك", value="زائر")
user_role = st.sidebar.selectbox("صفتك", ["طالب", "معيد", "دكتور"])
page = st.sidebar.radio("التنقل", ["الرئيسية", "بحث", "رفع مادة", "الإحصائيات", "مصادر خارجية", "عن المنصة"])

if page == "الرئيسية":
    materials = load_materials()
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد المواد", len(materials))
    col2.metric("عدد التصنيفات", len(CATEGORIES))
    col3.metric("إجمالي التحميلات", sum(m["downloads"] for m in materials))
    st.subheader("آخر المواد المضافة")
    if not materials:
        st.info("لا توجد مواد مرفوعة بعد. كن أول من يرفع مادة!")
    else:
        recent = sorted(materials, key=lambda m: m["id"], reverse=True)[:6]
        cols = st.columns(3)
        for i, m in enumerate(recent):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{m['title']}**")
                    st.caption(f"{m['category']} | {m['author']}")
                    st.write(m["description"][:80] + "...")
                    st.write(f"تقييم: {get_average_rating(m)} | تحميلات: {m['downloads']}")

elif page == "بحث":
    st.subheader("البحث عن المواد")
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("ابحث بالعنوان، المؤلف، أو الكلمات المفتاحية")
    with col2:
        category_filter = st.selectbox("التصنيف", ["الكل"] + CATEGORIES)
    results = search_materials(query, category_filter)
    st.write(f"عدد النتائج: {len(results)}")
    for m in results:
        with st.container(border=True):
            st.markdown(f"### {m['title']}")
            st.caption(f"{m['category']} | {m['author']} | {m['upload_date']}")
            st.write(m["description"])
            if m["tags"]:
                st.write("الكلمات المفتاحية: " + " | ".join(m["tags"]))
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"التقييم: {get_average_rating(m)} ({m['rating_count']} تقييم)")
            with col2:
                st.write(f"التحميلات: {m['downloads']}")
            with col3:
                if os.path.exists(m["file_path"]):
                    with open(m["file_path"], "rb") as f:
                        if st.download_button("تحميل", data=f.read(), file_name=os.path.basename(m["file_path"]), key=f"dl_{m['id']}"):
                            increment_downloads(m["id"])
            rating = st.slider("قيّم المادة", 1, 5, 3, key=f"rate_{m['id']}")
            if st.button("إرسال التقييم", key=f"rate_btn_{m['id']}"):
                add_rating(m["id"], rating)
                st.success("شكراً لتقييمك!")
                st.rerun()

elif page == "رفع مادة":
    st.subheader("رفع مادة جديدة")
    st.caption("من فضلك تأكد من دقة البيانات قبل الرفع، وأن الملف يخص المقرر أو التخصص بشكل مباشر")
    with st.form("upload_form", clear_on_submit=True):
        title = st.text_input("عنوان المادة *")
        category = st.selectbox("التصنيف *", CATEGORIES)
        author = st.text_input("اسم المؤلف *")
        description = st.text_area("وصف المادة *")
        tags_input = st.text_input("الكلمات المفتاحية (افصل بينها بفاصلة ,)")
        uploaded_file = st.file_uploader("اختر الملف *")
        submitted = st.form_submit_button("رفع المادة")
        if submitted:
            if not title or not author or not description or not uploaded_file:
                st.error("من فضلك املأ كل الحقول المطلوبة (*) واختر ملفاً")
            else:
                if not os.path.exists(UPLOADS_DIR):
                    os.makedirs(UPLOADS_DIR)
                file_path = os.path.join(UPLOADS_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                add_material(title, category, author, description, file_path, tags, f"{user_name} ({user_role})")
                st.success("تم رفع المادة بنجاح!")
                st.balloons()

elif page == "الإحصائيات":
    st.subheader("إحصائيات المنصة")
    materials = load_materials()
    if not materials:
        st.info("لا توجد بيانات كافية")
    else:
        df = pd.DataFrame(materials)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("توزيع المواد حسب التصنيف")
            cat_counts = df["category"].value_counts()
            st.bar_chart(cat_counts)
        with col2:
            st.subheader("أكثر المواد تحميلاً")
            top_downloaded = df.nlargest(10, "downloads")[["title", "downloads"]]
            st.dataframe(top_downloaded, hide_index=True)
        st.subheader("المواد المضافة حسب الشهر")
        df["month"] = pd.to_datetime(df["upload_date"]).dt.to_period("M").astype(str)
        monthly = df.groupby("month").size()
        st.line_chart(monthly)

elif page == "مصادر خارجية":
    st.subheader("ابحث في مصادر مفتوحة الوصول")
    st.caption("بحث وربط فقط بمصادر أكاديمية موثوقة، لا يتم تحميل أو تخزين أي ملفات")
    ext_query = st.text_input("اكتب موضوع البحث (بالعربي أو الإنجليزي)", key="ext_search")
    if ext_query:
        q = urllib.parse.quote(ext_query)
        sources = [("RePEc / IDEAS", f"https://ideas.repec.org/cgi-bin/htsearch?q={q}", "أكبر أرشيف مجاني لأبحاث الاقتصاد في العالم"), ("SSRN", f"https://www.ssrn.com/index.cfm/en/search/?term={q}", "أوراق بحثية أولية في الاقتصاد والتمويل"), ("Google Scholar", f"https://scholar.google.com/scholar?q={q}", "بحث أكاديمي شامل"), ("DOAJ", f"https://doaj.org/search/articles?source=%7B%22query%22%3A%7B%22query_string%22%3A%7B%22query%22%3A%22{q}%22%7D%7D%7D", "مجلات علمية مفتوحة الوصول بالكامل")]
        for name, url, desc in sources:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.caption(desc)
                st.link_button(f"ابحث في {name}", url)
    else:
        st.info("اكتب كلمة أو موضوع فوق عشان تظهرلك روابط البحث في المصادر المختلفة")

elif page == "عن المنصة":
    st.subheader("عن المنصة")
    st.markdown("### الهدف من المنصة")
    st.write("توفير مصدر موحد وسهل الوصول للمواد الأكاديمية الخاصة بقسم اقتصاديات التجارة الخارجية، يجمع بين المحاضرات والأبحاث والنماذج التطبيقية في مكان واحد، لدعم الطلاب وأعضاء هيئة التدريس على حد سواء.")
    st.markdown("### الرؤية")
    st.write("أن تكون المنصة المرجع الرقمي الأساسي لطلاب وباحثي اقتصاديات التجارة الخارجية، من خلال تسهيل الوصول للمعرفة وتشجيع تبادل المحتوى العلمي الأصيل بين الطلاب وأعضاء هيئة التدريس.")
    st.markdown("### القيم الأساسية")
    st.write("- الشفافية في مصادر المعرفة")
    st.write("- تشجيع الإنتاج العلمي الأصيل للطلاب")
    st.write("- سهولة الوصول للمواد لكل المستويات الدراسية")
    st.markdown("### الجهة المسؤولة")
    st.write("قسم اقتصاديات التجارة الخارجية - كلية التجارة وإدارة الأعمال - جامعة العاصمة")

st.markdown("---")
st.markdown("<center style='color:#0F3B5F;'>جامعة العاصمة | كلية التجارة وإدارة الأعمال | قسم اقتصاديات التجارة الخارجية 2026</center>", unsafe_allow_html=True)
