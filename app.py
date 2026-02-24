"""
تطبيق تسعير المنتجات الكامل | Complete Product Pricing App
============================================================
جاهز للرفع على GitHub وتشغيل مباشرة بـ streamlit run app.py

المميزات:
- واجهة عصرية أزرق هادئ مع CSS مخصص
- قاعدة بيانات SQLite كاملة
- رفع/تصدير Excel/CSV/PDF
- داشبورد مع مقاييس ومقارنة منافسين
- دردشة داخلية حية
- اقتراح أسعار ذكي
- دعم عربي/إنجليزي RTL
- حسابات تلقائية (ربح + ضريبة)

التشغيل: pip install -r requirements.txt ثم streamlit run app.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import io
import time
import numpy as np
from datetime import datetime
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ========================================================
# CSS المخصص (عصري هادئ أزرق)
CSS = """
<style>
:root {
  --primary-color: #3b82f6;
  --secondary-color: #60a5fa;
  --bg-color: #f8fafc;
  --card-bg: #ffffff;
  --text-color: #1e293b;
  --border-color: #e2e8f0;
  --success-color: #10b981;
  --warning-color: #f59e0b;
}

.stApp {
  background-color: var(--bg-color);
}

.block-container {
  padding-top: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.stMetric {
  background-color: var(--card-bg);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border: 1px solid var(--border-color);
}

.stDataFrame {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.css-1d391kg {
  color: var(--primary-color) !important;
  font-weight: 700 !important;
}

.stButton > button {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  border-radius: 10px;
  border: none;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.stButton > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input {
  border-radius: 10px;
  border: 2px solid var(--border-color);
  padding: 0.75rem;
}

.chat-message {
  padding: 1rem;
  margin: 0.5rem 0;
  border-radius: 18px;
  max-width: 80%;
}

.user-message {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  margin-left: auto;
}

.assistant-message {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  margin-right: auto;
}

[dir="rtl"] .stApp {
  text-align: right;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ========================================================
# إعدادات الصفحة
st.set_page_config(
    page_title="💰 تطبيق تسعير المنتجات",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================================
# قاعدة البيانات
@st.cache_resource
def init_db():
    conn = sqlite3.connect('products.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit_price REAL NOT NULL,
            profit_margin REAL DEFAULT 0.2,
            tax_rate REAL DEFAULT 0.14,
            competitor_price REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    return conn

# ========================================================
# وظائف قاعدة البيانات
def add_product(name, quantity, unit_price, profit_margin=0.2, tax_rate=0.14, competitor_price=0):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, quantity, unit_price, profit_margin, tax_rate, competitor_price)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, quantity, unit_price, profit_margin, tax_rate, competitor_price))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect('products.db')
    df = pd.read_sql_query("SELECT * FROM products ORDER BY created_at DESC", conn)
    conn.close()
    return df

def add_chat_message(sender, message):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_messages (sender, message) VALUES (?, ?)", (sender, message))
    conn.commit()
    conn.close()

def get_chat_messages(limit=50):
    conn = sqlite3.connect('products.db')
    df = pd.read_sql_query(
        "SELECT * FROM chat_messages ORDER BY timestamp DESC LIMIT ?", 
        conn, params=(limit,)
    )
    conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df[::-1]
    return pd.DataFrame()

# ========================================================
# وظائف الحسابات
def calculate_final_price(row):
    cost = row['unit_price'] * row['quantity']
    profit = cost * row['profit_margin']
    taxable = cost + profit
    tax = taxable * row['tax_rate']
    return cost + profit + tax

def suggest_price(df, product_name):
    similar = df[df['name'].str.contains(product_name, case=False, na=False)]
    if not similar.empty:
        avg_price = similar['unit_price'].mean()
        competitor_avg = similar['competitor_price'].mean()
        return min(avg_price * 1.1, competitor_avg * 0.95) if competitor_avg > 0 else avg_price * 1.15
    return 0

# ========================================================
# وظائف التصدير
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as excel_writer:
        df.to_excel(excel_writer, sheet_name='Products', index=False)
    return output.getvalue()

def export_to_pdf(df):
    if not PDF_AVAILABLE:
        st.warning("مكتبة reportlab غير مثبتة لتصدير PDF")
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    data = [['ID', 'المنتج', 'الكمية', 'سعر الوحدة', 'السعر النهائي']]
    for _, row in df.iterrows():
        final_price = calculate_final_price(row)
        data.append([row['id'], row['name'], row['quantity'], f"{row['unit_price']:.2f}", f"{final_price:.2f}"])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story = [Paragraph("ملخص تسعير المنتجات", styles['Title']), Spacer(1, 20), table]
    doc.build(story)
    return buffer.getvalue()

# ========================================================
# تهيئة الجلسة واللغة
if 'language' not in st.session_state:
    st.session_state.language = 'ar'

TEXTS = {
    'ar': {
        'title': '💰 تطبيق تسعير المنتجات المتقدم',
        'add_product': '➕ إضافة منتج جديد',
        'name': 'اسم المنتج',
        'quantity': 'الكمية',
        'unit_price': 'سعر الوحدة (ر.س)',
        'profit_margin': 'نسبة الربح (%)',
        'tax_rate': 'نسبة الضريبة (%)',
        'competitor_price': 'سعر المنافس (ر.س)',
        'final_price': 'السعر النهائي',
        'total': 'الإجمالي',
        'profit': 'صافي الربح',
        'upload': '📁 رفع ملف Excel/CSV',
        'export': '📤 تصدير البيانات',
        'chat': '💬 دردشة العملاء',
        'send': 'إرسال الرد',
        'admin_reply': 'رد الإدارة...',
        'total_summary': 'ملخص الأسعار',
        'suggest': '💡 اقتراح سعر',
        'products': '📦 المنتجات',
        'dashboard': '📈 الداشبورد',
        'settings': '⚙️ الإعدادات',
        'language': 'اللغة / Language'
    },
    'en': {
        'title': '💰 Advanced Product Pricing App',
        'add_product': '➕ Add New Product',
        'name': 'Product Name',
        'quantity': 'Quantity',
        'unit_price': 'Unit Price (SAR)',
        'profit_margin': 'Profit Margin (%)',
        'tax_rate': 'Tax Rate (%)',
        'competitor_price': 'Competitor Price (SAR)',
        'final_price': 'Final Price',
        'total': 'Total',
        'profit': 'Net Profit',
        'upload': '📁 Upload Excel/CSV',
        'export': '📤 Export Data',
        'chat': '💬 Customer Chat',
        'send': 'Send Reply',
        'admin_reply': 'Admin reply...',
        'total_summary': 'Price Summary',
        'suggest': '💡 Suggest Price',
        'products': '📦 Products',
        'dashboard': '📈 Dashboard',
        'settings': '⚙️ Settings',
        'language': 'Language'
    }
}

# ========================================================
# العنوان الرئيسي
st.title(TEXTS[st.session_state.language]['title'])

# الشريط الجانبي
with st.sidebar:
    st.header(TEXTS[st.session_state.language]['settings'])
    
    # تبديل اللغة
    new_lang = st.selectbox(
        TEXTS[st.session_state.language]['language'], 
        ['ar', 'en'], 
        index=0 if st.session_state.language == 'ar' else 1,
        key='lang_key'
    )
    if new_lang != st.session_state.language:
        st.session_state.language = new_lang
        st.rerun()
    
    texts = TEXTS[st.session_state.language]
    
    # رفع ملف
    uploaded_file = st.file_uploader(texts['upload'], type=['csv', 'xlsx', 'xls'])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)
            
            for _, row in df_upload.iterrows():
                add_product(
                    row.get('name', row.get('اسم المنتج', '')),
                    row.get('quantity', row.get('الكمية', 1)),
                    row.get('unit_price', row.get('سعر الوحدة', 0)),
                    row.get('profit_margin', row.get('نسبة الربح', 0.2)) / 100,
                    row.get('tax_rate', row.get('نسبة الضريبة', 0.14)) / 100,
                    row.get('competitor_price', row.get('سعر المنافس', 0))
                )
            st.success("✅ تم رفع الملف بنجاح!")
            st.rerun()
        except Exception as e:
            st.error(f"خطأ في رفع الملف: {e}")

# ========================================================
# جلب البيانات
df = get_products()
init_db()  # تهيئة قاعدة البيانات

# إضافة عمود السعر النهائي
if not df.empty:
    df['final_price'] = df.apply(calculate_final_price, axis=1)

# ========================================================
# التبويبات الرئيسية
tab1, tab2, tab3 = st.tabs([
    TEXTS[st.session_state.language]['products'],
    TEXTS[st.session_state.language]['dashboard'],
    TEXTS[st.session_state.language]['chat']
])

# تبويب المنتجات
with tab1:
    # نموذج إضافة منتج
    with st.form("add_product"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(texts['name'])
        with col2:
            quantity = st.number_input(texts['quantity'], min_value=0.01, value=1.0, step=0.1)
        with col3:
            unit_price = st.number_input(texts['unit_price'], min_value=0.01, value=10.0)
        
        col4, col5, col6 = st.columns(3)
        with col4:
            profit_margin = st.number_input(texts['profit_margin'], min_value=0.0, max_value=100.0, value=20.0) / 100
        with col5:
            tax_rate = st.number_input(texts['tax_rate'], min_value=0.0, max_value=50.0, value=14.0) / 100
        with col6:
            competitor_price = st.number_input(texts['competitor_price'], min_value=0.0)
        
        col_suggest, col_submit = st.columns([1, 2])
        with col_suggest:
            if st.button(texts['suggest']) and name:
                suggested = suggest_price(df, name)
                if suggested > 0:
                    st.info(f"💡 **السعر المقترح: {suggested:.2f} ر.س**")
        
        with col_submit:
            submitted = st.form_submit_button(texts['add_product'], use_container_width=True)
        
        if submitted and name:
            add_product(name, quantity, unit_price, profit_margin, tax_rate, competitor_price)
            st.success("✅ تم إضافة المنتج بنجاح!")
            st.rerun()
    
    # جدول المنتجات
    if not df.empty:
        st.dataframe(df[['name', 'quantity', 'unit_price', 'final_price', 'competitor_price']], 
                    use_container_width=True,
                    column_config={
                        "final_price": st.column_config.NumberColumn("السعر النهائي", format="%.2f ر.س"),
                        "unit_price": st.column_config.NumberColumn("سعر الوحدة", format="%.2f ر.س"),
                        "competitor_price": st.column_config.NumberColumn("سعر المنافس", format="%.2f ر.س")
                    })
        
        # أزرار التصدير
        col_csv, col_excel, col_pdf = st.columns(3)
        csv = convert_df_to_csv(df)
        excel = convert_df_to_excel(df)
        
        with col_csv:
            st.download_button(
                label="📥 CSV",
                data=csv,
                file_name=f'products_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv'
            )
        with col_excel:
            st.download_button(
                label="📥 Excel", 
                data=excel,
                file_name=f'products_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        with col_pdf:
            if PDF_AVAILABLE:
                pdf_data = export_to_pdf(df)
                st.download_button(
                    label="📥 PDF",
                    data=pdf_data,
                    file_name=f'products_{datetime.now().strftime("%Y%m%d")}.pdf',
                    mime='application/pdf'
                )
            else:
                st.info("📥 قم بتثبيت reportlab لدعم PDF")

# تبويب الداشبورد
with tab2:
    if not df.empty:
        total_final = df['final_price'].sum()
        total_cost = (df['unit_price'] * df['quantity']).sum()
        total_profit = total_final - total_cost
        profit_margin_total = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 " + texts['total'], f"{total_final:.2f} ر.س")
        with col2:
            st.metric("💵 " + texts['profit'], f"{total_profit:.2f} ر.س", f"{profit_margin_total:.1f}%")
        with col3:
            st.metric("📦 عدد المنتجات", len(df))
        with col4:
            st.metric("⭐ متوسط السعر", f"{df['final_price'].mean():.2f} ر.س")
        
        # مقارنة المنافسين
        if df['competitor_price'].sum() > 0:
            st.subheader("⚔️ مقارنة الأسعار مع المنافسين")
            comparison_df = df[df['competitor_price'] > 0].copy()
            if not comparison_df.empty:
                comparison_df['advantage'] = ((comparison_df['competitor_price'] - comparison_df['final_price']) / comparison_df['competitor_price'] * 100).round(1)
                st.dataframe(comparison_df[['name', 'final_price', 'competitor_price', 'advantage']],
                           use_container_width=True,
                           column_config={
                               "advantage": st.column_config.NumberColumn("% ميزة تنافسية", format="%.1f%%")
                           })

# تبويب الدردشة
with tab3:
    st.header("💬 " + texts['chat'])
    
    # عرض الرسائل
    chat_df = get_chat_messages()
    if not chat_df.empty:
        for _, msg in chat_df.iterrows():
            if msg['sender'] == 'customer':
                with st.chat_message("user", avatar="👤"):
                    st.write(msg['message'])
                    st.caption(msg['timestamp'].strftime("%H:%M"))
            else:
                with st.chat_message("assistant", avatar="🧑‍💼"):
                    st.write(msg['message'])
                    st.caption(msg['timestamp'].strftime("%H:%M"))
    
    # إدخال رسائل العميل
    if prompt := st.chat_input("اكتب سؤال العميل هنا..."):
        st.chat_message("user", avatar="👤").write(prompt)
        add_chat_message('customer', prompt)
        st.rerun()
    
    # رد الإدارة
    admin_reply = st.text_area(texts['admin_reply'], height=100, 
                              placeholder="اكتب ردك على العميل هنا...")
    if st.button(texts['send'], use_container_width=True, type="primary") and admin_reply.strip():
        st.chat_message("assistant", avatar="🧑‍💼").write(admin_reply)
        add_chat_message('admin', admin_reply)
        st.success("✅ تم إرسال الرد!")
        st.rerun()

# ========================================================
# requirements.txt (انسخه في ملف منفصل)
st.sidebar.markdown("---")
st.sidebar.code("""
streamlit>=1.38.0
pandas>=2.2.0
openpyxl>=3.1.0
reportlab>=4.0.0  # اختياري لـ PDF
altair>=5.0.0
""", language="txt")

st.sidebar.markdown("---")
st.sidebar.info("🚀 **جاهز للنشر على GitHub & Streamlit Cloud**")
