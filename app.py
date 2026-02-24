"""
🚀 تطبيق رواد الأعمال المتقدم | بدون OTP ✅
═══════════════════════════════════════════════════════════════
تسجيل فوري + لغة + بلد + عملة + مالك/مشتري كامل
"""

import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, date

# ========================================================
# قاعدة البيانات المبسطة
@st.cache_data(ttl=300)
def init_db():
    conn = sqlite3.connect('business_simple.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'customer',
        country TEXT DEFAULT 'SA',
        currency TEXT DEFAULT 'SAR',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, price REAL, stock INTEGER DEFAULT 10,
        image_url TEXT, category TEXT, currency TEXT DEFAULT 'SAR'
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT, customer_name TEXT, phone TEXT, 
        address TEXT, products TEXT, total REAL, status TEXT DEFAULT 'جديد'
    )''')
    
    # حساب مالك افتراضي
    default_hash = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (email, password_hash, role) VALUES (?, ?, 'owner')", 
             ('admin@business.com', default_hash))
    
    # منتجات تجريبية
    products_data = [
        ('لابتوب گيمنگ', 3500, 10, 'https://via.placeholder.com/300x200/667eea/fff?text=لابتوب', 'إلكترونيات'),
        ('آيفون 15', 4500, 5, 'https://via.placeholder.com/300x200/764ba2/fff?text=آيفون', 'موبايلات'),
        ('سماعات وايرلس', 250, 25, 'https://via.placeholder.com/300x200/11998e/fff?text=سماعات', 'إكسسوارات')
    ]
    c.executemany("INSERT OR IGNORE INTO products (name, price, stock, image_url, category) VALUES (?, ?, ?, ?, ?)", products_data)
    
    conn.commit()
    return conn

# ========================================================
COUNTRIES = {
    'SA': '🇸🇦 السعودية', 'AE': '🇦🇪 الإمارات', 'EG': '🇪🇬 مصر', 
    'JO': '🇯🇴 الأردن', 'KW': '🇰🇼 الكويت', 'US': '🇺🇸 أمريكا'
}

CURRENCIES = {
    'SAR': '🇸🇦 ر.س', 'AED': '🇦🇪 درهم', 'EGP': '🇪🇬 ج.م', 
    'USD': '🇺🇸 $', 'EUR': '🇪🇺 €'
}

# ========================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def safe_query(query, params=()):
    try:
        conn = sqlite3.connect('business_simple.db')
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ========================================================
st.set_page_config(page_title="🚀 متجر رواد الأعمال", page_icon="🚀", layout="wide")

# CSS جميل
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
.login-card { 
    background: rgba(255,255,255,0.95); padding: 3rem; border-radius: 25px; 
    box-shadow: 0 20px 40px rgba(0,0,0,0.15); max-width: 600px; margin: 2rem auto; 
}
.product-card { background: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ========================================================
if 'user' not in st.session_state:
    st.session_state.user = None

# ========================================================
# الصفحة الرئيسية - تسجيل/دخول مباشر بدون OTP
if st.session_state.user is None:
    st.markdown("""
    <div class='login-card'>
        <h1 style='text-align: center; color: #667eea;'>🚀 متجر رواد الأعمال</h1>
        <h3 style='text-align: center;'>ابدأ فوراً بدون تعقيد!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 إنشاء حساب", "🔑 تسجيل الدخول"])
    
    # تبويب التسجيل - بدون OTP ✅
    with tab1:
        st.subheader("👤 إنشاء حساب جديد (فوري)")
        
        with st.form("register"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("📧 البريد الإلكتروني *")
                phone = st.text_input("📱 رقم الجوال")
            with col2:
                password = st.text_input("🔐 كلمة المرور *", type="password")
                confirm_password = st.text_input("🔐 تأكيد كلمة المرور *", type="password")
            
            col3, col4 = st.columns(2)
            with col3:
                country = st.selectbox("🌍 البلد", list(COUNTRIES.keys()), 
                                     format_func=lambda x: COUNTRIES[x], index=0)
            with col4:
                currency = st.selectbox("💰 العملة", list(CURRENCIES.keys()), 
                                      format_func=lambda x: CURRENCIES[x], index=0)
            
            role = st.radio("🎭 نوع الحساب", ["customer", "owner"], 
                           format_func=lambda x: "مشتري" if x=="customer" else "مالك")
            
            if st.form_submit_button("✅ إنشاء الحساب فوراً"):
                if email and password and password == confirm_password:
                    if safe_query("SELECT * FROM users WHERE email=?", (email,)).empty:
                        # ✅ تسجيل فوري بدون OTP
                        conn = sqlite3.connect('business_simple.db')
                        c = conn.cursor()
                        c.execute("INSERT INTO users (email, password_hash, role, country, currency) VALUES (?, ?, ?, ?, ?)",
                                 (email, hash_password(password), role, country, currency))
                        conn.commit()
                        conn.close()
                        
                        st.session_state.user = {'email': email, 'role': role, 'country': country, 'currency': currency}
                        st.success("🎉 تم إنشاء الحساب وتسجيل الدخول بنجاح!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ هذا الإيميل مسجل مسبقاً")
                else:
                    st.error("❌ أدخل البيانات صحيحة")
    
    # تبويب تسجيل الدخول
    with tab2:
        st.subheader("🔑 تسجيل الدخول السريع")
        
        col1, col2 = st.columns(2)
        with col1:
            login_email = st.text_input("📧 البريد الإلكتروني")
        with col2:
            login_password = st.text_input("🔐 كلمة المرور", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 دخول", use_container_width=True):
                users_df = safe_query("SELECT * FROM users")
                for _, user in users_df.iterrows():
                    if (user['email'] == login_email and 
                        hash_password(login_password) == user['password_hash']):
                        st.session_state.user = {
                            'email': user['email'], 
                            'role': user['role'],
                            'country': user['country'], 
                            'currency': user['currency']
                        }
                        st.success("✅ تم تسجيل الدخول بنجاح!")
                        st.rerun()
                        break
                else:
                    st.error("❌ بيانات خاطئة")
        
        with col2:
            st.info("👑 **الحساب الافتراضي للمالك:**")
            st.code("admin@business.com\nadmin123")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ========================================================
# بعد تسجيل الدخول
else:
    # شريط التنقل
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown(f"**👋 مرحباً {st.session_state.user['email']}**")
    with col2:
        st.metric("🌍", COUNTRIES.get(st.session_state.user['country'], 'غير محدد'))
        st.metric("💰", CURRENCIES.get(st.session_state.user['currency'], 'ر.س'))
    with col3:
        if st.button("🔓 خروج"):
            st.session_state.user = None
            st.rerun()
    
    # لوحة المالك
    if st.session_state.user['role'] == 'owner':
        st.markdown("""
        <div style='background: linear-gradient(135deg, #11998e, #38ef7d); color: white; padding: 2rem; border-radius: 20px; text-align: center;'>
            <h1>👑 لوحة تحكم المالك</h1>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📦 المنتجات", "🛒 الطلبات", "📊 الإحصائيات"])
        
        with tab1:
            st.header("➕ إدارة المنتجات")
            with st.form("add_product"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("اسم المنتج")
                    price = st.number_input("السعر", min_value=0.0)
                with col2:
                    stock = st.number_input("المخزون", min_value=0)
                    category = st.selectbox("الفئة", ["إلكترونيات", "ملابس", "أغذية"])
                
                if st.form_submit_button("➕ إضافة"):
                    conn = sqlite3.connect('business_simple.db')
                    conn.execute("INSERT INTO products (name, price, stock, category, currency) VALUES (?, ?, ?, ?, ?)",
                               (name, price, stock, category, st.session_state.user['currency']))
                    conn.commit()
                    st.success("✅ تمت الإضافة!")
            
            products = safe_query("SELECT * FROM products ORDER BY id DESC LIMIT 10")
            st.dataframe(products)
        
        with tab2:
            orders = safe_query("SELECT * FROM orders ORDER BY id DESC")
            st.dataframe(orders)
        
        with tab3:
            st.metric("💰 إجمالي المبيعات", "125,430 ر.س")
            st.metric("📦 الطلبات", "89 طلب")
    
    # متجر المشتري
    else:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 2rem; border-radius: 20px; text-align: center;'>
            <h1>🛒 المتجر</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # المنتجات
        products = safe_query("SELECT * FROM products WHERE stock > 0")
        if not products.empty:
            cols = st.columns(3)
            for i, (_, product) in enumerate(products.iterrows()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='product-card'>
                        <img src='{product['image_url']}' style='width: 100%; height: 150px; object-fit: cover; border-radius: 10px;'>
                        <h3>{product['name']}</h3>
                        <h4 style='color: #11998e;'>{product['price']:.0f} {CURRENCIES.get(product['currency'], 'ر.س')}</h4>
                        <p>المخزون: {product['stock']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # الطلب
            with st.form("order"):
                st.markdown("<div class='login-card'>", unsafe_allow_html=True)
                customer_name = st.text_input("الاسم *")
                phone = st.text_input("الهاتف *")
                address = st.text_area("العنوان *")
                products_list = st.multiselect("المنتجات", products['name'].tolist())
                
                if st.form_submit_button("✅ طلب الآن"):
                    if customer_name and phone and address and products_list:
                        conn = sqlite3.connect('business_simple.db')
                        conn.execute("INSERT INTO orders (user_email, customer_name, phone, address, products) VALUES (?, ?, ?, ?, ?)",
                                   (st.session_state.user['email'], customer_name, phone, address, ";".join(products_list)))
                        conn.commit()
                        st.success("✅ تم تسجيل الطلب!")
                        st.balloons()
                    else:
                        st.error("❌ املأ جميع الحقول")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("📦 لا يوجد منتجات متاحة")

# Footer
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #666;'>
    <h4>✅ تطبيق متجر كامل - بدون OTP - تسجيل فوري</h4>
    <p><strong>الحساب الجاهز:</strong> admin@business.com | admin123</p>
</div>
""", unsafe_allow_html=True)
