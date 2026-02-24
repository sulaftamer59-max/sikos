"""
🚀 تطبيق رواد الأعمال | معلومات المشترين للمالك ✅
═══════════════════════════════════════════════
المالك يشوف اسم + جوال + عنوان + إيميل كل مشتري
"""

import streamlit as st
import pandas as pd
import sqlite3
import hashlib

# ========================================================
def init_db():
    conn = sqlite3.connect('business_complete.db', check_same_thread=False)
    c = conn.cursor()
    
    # المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT,
        role TEXT DEFAULT 'customer',
        country TEXT DEFAULT 'SA',
        currency TEXT DEFAULT 'SAR',
        phone TEXT
    )''')
    
    # المنتجات
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_email TEXT,
        name TEXT,
        price REAL,
        stock INTEGER DEFAULT 10,
        image_url TEXT DEFAULT 'https://via.placeholder.com/300x200',
        category TEXT DEFAULT 'عام'
    )''')
    
    # ✅ الطلبات مع معلومات كاملة للمشتري
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_email TEXT,
        customer_email TEXT,
        customer_name TEXT,
        customer_phone TEXT,
        customer_address TEXT,
        products TEXT,
        total_price REAL DEFAULT 0,
        status TEXT DEFAULT 'جديد',
        order_date TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # منتجات تجريبية
    c.execute("INSERT OR IGNORE INTO products (owner_email, name, price, stock, category) VALUES ('demo', 'لابتوب', 3500, 10, 'إلكترونيات')")
    c.execute("INSERT OR IGNORE INTO products (owner_email, name, price, stock, category) VALUES ('demo', 'آيفون', 4500, 5, 'موبايلات')")
    
    conn.commit()
    conn.close()

# ========================================================
COUNTRIES = {'SA': '🇸🇦 السعودية', 'AE': '🇦🇪 الإمارات', 'EG': '🇪🇬 مصر'}
CURRENCIES = {'SAR': '🇸🇦 ر.س', 'AED': '🇦🇪 درهم', 'USD': '🇺🇸 $'}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def safe_query(query, params=()):
    try:
        conn = sqlite3.connect('business_complete.db')
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ========================================================
st.set_page_config(page_title="🚀 متجرك", page_icon="🚀", layout="wide")

if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

st.markdown("""
<style>
.login-card { background: rgba(255,255,255,0.95); padding: 3rem; border-radius: 25px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); max-width: 600px; margin: 2rem auto; }
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
.order-card { background: #e8f5e8; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #11998e; }
</style>
""", unsafe_allow_html=True)

# ========================================================
if 'user' not in st.session_state:
    st.session_state.user = None

# تسجيل/دخول (نفس الكود السابق)
if st.session_state.user is None:
    st.markdown("""
    <div class='login-card'>
        <h1 style='text-align: center; color: #667eea;'>🚀 متجرك الخاص</h1>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 حساب جديد", "🔑 دخول"])
    
    with tab1:
        with st.form("register"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("📧 الإيميل *")
                phone = st.text_input("📱 الجوال")
            with col2:
                password = st.text_input("🔐 كلمة المرور *", type="password")
                confirm_pass = st.text_input("🔐 تأكيد *", type="password")
            
            country = st.selectbox("🌍 البلد", list(COUNTRIES.keys()))
            currency = st.selectbox("💰 العملة", list(CURRENCIES.keys()))
            role = st.radio("نوع الحساب", ["customer", "owner"])
            
            if st.form_submit_button("إنشاء حساب"):
                if password == confirm_pass and email:
                    if safe_query("SELECT id FROM users WHERE email=?", (email,)).empty:
                        conn = sqlite3.connect('business_complete.db')
                        c = conn.cursor()
                        c.execute("INSERT INTO users (email, password_hash, role, country, currency, phone) VALUES (?, ?, ?, ?, ?, ?)",
                                (email, hash_password(password), role, country, currency, phone))
                        conn.commit()
                        conn.close()
                        st.session_state.user = {'email': email, 'role': role, 'country': country, 'currency': currency}
                        st.success("✅ حسابك جاهز!")
                        st.rerun()
                    else:
                        st.error("❌ الإيميل موجود")
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            login_email = st.text_input("📧 الإيميل")
        with col2:
            login_pass = st.text_input("🔐 كلمة المرور", type="password")
        
        if st.button("دخول"):
            users = safe_query("SELECT * FROM users")
            for _, user in users.iterrows():
                if user['email'] == login_email and hash_password(login_pass) == user['password_hash']:
                    st.session_state.user = {'email': user['email'], 'role': user['role'], 'country': user['country'], 'currency': user['currency']}
                    st.rerun()
                    break
            else:
                st.error("❌ بيانات خاطئة")

else:
    # شريط التحكم
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.markdown(f"**👋 {st.session_state.user['email']}**")
    with col2:
        st.metric("🏠", COUNTRIES[st.session_state.user['country']])
        st.metric("💰", CURRENCIES[st.session_state.user['currency']])
    with col3:
        if st.button("خروج"):
            st.session_state.user = None
            st.rerun()
    
    # ✅ لوحة المالك مع معلومات المشترين الكاملة
    if st.session_state.user['role'] == 'owner':
        st.markdown("""
        <div style='background: linear-gradient(135deg, #11998e, #38ef7d); color: white; padding: 3rem; border-radius: 25px; text-align: center;'>
            <h1>👑 متجرك الخاص</h1>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📦 المنتجات", "🛒 الطلبات", "👥 المشترون"])
        
        with tab1:
            with st.form("add_product"):
                name = st.text_input("اسم المنتج")
                price = st.number_input("السعر", min_value=1.0)
                stock = st.number_input("المخزون", min_value=1)
                if st.form_submit_button("➕ إضافة"):
                    conn = sqlite3.connect('business_complete.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO products (owner_email, name, price, stock) VALUES (?, ?, ?, ?)",
                            (st.session_state.user['email'], name, price, stock))
                    conn.commit()
                    conn.close()
                    st.success("✅ تمت الإضافة!")
            
            products = safe_query("SELECT * FROM products WHERE owner_email=?", (st.session_state.user['email'],))
            st.dataframe(products)
        
        with tab2:
            st.subheader("📋 الطلبات الجديدة")
            orders = safe_query("SELECT * FROM orders WHERE owner_email=? ORDER BY id DESC", (st.session_state.user['email'],))
            
            if not orders.empty:
                for _, order in orders.iterrows():
                    with st.expander(f"🆔 طلب #{order['id']} - {order['status']}"):
                        st.markdown(f"""
                        <div class='order-card'>
                            <h4>👤 {order['customer_name']}</h4>
                            <p><strong>📧 الإيميل:</strong> {order['customer_email']}</p>
                            <p><strong>📱 الجوال:</strong> {order['customer_phone']}</p>
                            <p><strong>📍 العنوان:</strong> {order['customer_address']}</p>
                            <p><strong>🛒 المنتجات:</strong> {order['products']}</p>
                            <p><strong>💰 المجموع:</strong> {order['total_price']} ر.س</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button(f"✅ تم الشحن {order['id']}", key=f"ship_{order['id']}"):
                                conn = sqlite3.connect('business_complete.db')
                                c = conn.cursor()
                                c.execute("UPDATE orders SET status='مُشحن' WHERE id=?", (order['id'],))
                                conn.commit()
                                conn.close()
                                st.rerun()
                        with col2:
                            if st.button(f"✨ مُستلم {order['id']}", key=f"done_{order['id']}"):
                                conn = sqlite3.connect('business_complete.db')
                                c = conn.cursor()
                                c.execute("UPDATE orders SET status='مُستلم' WHERE id=?", (order['id'],))
                                conn.commit()
                                conn.close()
                                st.rerun()
            else:
                st.info("📭 لا توجد طلبات")
        
        # ✅ تبويب جديد: قائمة المشترين
        with tab3:
            st.subheader("👥 جميع المشترين")
            customers = safe_query("""
                SELECT DISTINCT customer_email, customer_name, customer_phone, customer_address 
                FROM orders 
                WHERE owner_email=? 
                ORDER BY customer_name
            """, (st.session_state.user['email'],))
            
            if not customers.empty:
                st.dataframe(customers)
                
                st.markdown("---")
                st.subheader("📊 إحصائيات المشترين")
                st.metric("👥 عدد المشترين الفريدين", len(customers))
                st.metric("📦 إجمالي الطلبات", len(safe_query("SELECT * FROM orders WHERE owner_email=?", (st.session_state.user['email'],))))
            else:
                st.info("👥 لا يوجد مشترين بعد")
    
    # المشتري
    else:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 3rem; border-radius: 25px; text-align: center;'>
            <h1>🛒 تسوق الآن</h1>
        </div>
        """, unsafe_allow_html=True)
        
        products = safe_query("SELECT * FROM products WHERE stock > 0")
        if not products.empty:
            cols = st.columns(3)
            for i, row in products.iterrows():
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style='background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center;'>
                        <h4>{row['name']}</h4>
                        <h5 style='color: #11998e;'>{row['price']:.0f} ر.س</h5>
                        <p>المخزون: {row['stock']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with st.form("order"):
                st.subheader("📋 اطلب الآن")
                customer_name = st.text_input("👤 الاسم الكامل *")
                customer_phone = st.text_input("📱 رقم الجوال *")
                customer_address = st.text_area("📍 العنوان التفصيلي *")
                items = st.multiselect("🛒 المنتجات", products['name'].tolist())
                
                if st.form_submit_button("✅ إتمام الطلب"):
                    if customer_name and customer_phone and customer_address and items:
                        conn = sqlite3.connect('business_complete.db')
                        total = 0
                        for item in items:
                            product = products[products['name'] == item].iloc[0]
                            owner = product['owner_email']
                            total += product['price']
                            c = conn.cursor()
                            c.execute("""INSERT INTO orders 
                                       (owner_email, customer_email, customer_name, customer_phone, customer_address, products, total_price) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                    (owner, st.session_state.user['email'], customer_name, customer_phone, 
                                     customer_address, item, product['price']))
                        
                        conn.commit()
                        conn.close()
                        st.success("✅ تم إرسال الطلب لصاحب المتجر!")
                        st.balloons()
                    else:
                        st.error("❌ املأ جميع الحقول المطلوبة")

st.markdown("""
<div style='text-align: center; padding: 2rem; color: #666;'>
    <h4>✅ تطبيق متجر كامل مع معلومات المشترين</h4>
</div>
""", unsafe_allow_html=True)
