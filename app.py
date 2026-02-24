"""
🚀 تطبيق رواد الأعمال | تسجيل فردي بدون OTP ✅
═══════════════════════════════════════════════════════════════
كل شخص ينشئ حسابه الخاص - مالك/مشتري منفصل - بدون حساب جاهز
"""

import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, date

# ========================================================
@st.cache_data(ttl=300)
def init_db():
    conn = sqlite3.connect('business_personal.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT CHECK(role IN ('owner', 'customer')) DEFAULT 'customer',
        country TEXT DEFAULT 'SA',
        currency TEXT DEFAULT 'SAR',
        phone TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_email TEXT,
        name TEXT, price REAL, stock INTEGER DEFAULT 10,
        image_url TEXT, category TEXT, currency TEXT DEFAULT 'SAR'
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_email TEXT,
        customer_email TEXT, customer_name TEXT, phone TEXT, 
        address TEXT, products TEXT, total REAL, status TEXT DEFAULT 'جديد'
    )''')
    
    # منتجات تجريبية عامة
    c.executemany("INSERT OR IGNORE INTO products (owner_email, name, price, stock, image_url, category) VALUES (?, ?, ?, ?, ?, ?)", [
        ('demo', 'لابتوب گيمنگ', 3500, 10, 'https://via.placeholder.com/300x200/667eea/fff?text=لابتوب', 'إلكترونيات'),
        ('demo', 'آيفون 15', 4500, 5, 'https://via.placeholder.com/300x200/764ba2/fff?text=آيفون', 'موبايلات'),
        ('demo', 'سماعات وايرلس', 250, 25, 'https://via.placeholder.com/300x200/11998e/fff?text=سماعات', 'إكسسوارات')
    ])
    
    conn.commit()
    return conn

# ========================================================
COUNTRIES = {
    'SA': '🇸🇦 السعودية', 'AE': '🇦🇪 الإمارات', 'EG': '🇪🇬 مصر', 
    'JO': '🇯🇴 الأردن', 'KW': '🇰🇼 الكويت', 'US': '🇺🇸 أمريكا'
}

CURRENCIES = {
    'SAR': '🇸🇦 ر.س', 'AED': '🇦🇪 درهم', 'EGP': '🇪🇬 ج.م', 'USD': '🇺🇸 $'
}

# ========================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def safe_query(query, params=()):
    try:
        conn = sqlite3.connect('business_personal.db')
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ========================================================
st.set_page_config(page_title="🚀 متجرك الخاص", page_icon="🚀", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
.login-card { 
    background: rgba(255,255,255,0.95); padding: 3rem; border-radius: 25px; 
    box-shadow: 0 20px 40px rgba(0,0,0,0.15); max-width: 600px; margin: 2rem auto; 
}
</style>
""", unsafe_allow_html=True)

# ========================================================
if 'user' not in st.session_state:
    st.session_state.user = None

# ========================================================
# تسجيل/دخول - كل واحد حسابه الخاص ✅
if st.session_state.user is None:
    st.markdown("""
    <div class='login-card'>
        <h1 style='text-align: center;'>🚀 أنشئ متجرك الخاص الآن</h1>
        <h3 style='text-align: center; color: #11998e;'>كل شخص حسابه الخاص!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 حساب جديد", "🔑 حساب موجود"])
    
    with tab1:
        st.subheader("📝 أنشئ حسابك الخاص فوراً")
        
        with st.form("new_account"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("📧 بريدك الإلكتروني *")
                phone = st.text_input("📱 رقم الجوال")
            with col2:
                password = st.text_input("🔐 كلمة المرور *", type="password")
                confirm_password = st.text_input("🔐 تأكيد كلمة المرور *", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                country = st.selectbox("🌍 بلدك", list(COUNTRIES.keys()), index=0,
                                     format_func=lambda x: COUNTRIES[x])
            with col2:
                currency = st.selectbox("💰 عملتك", list(CURRENCIES.keys()), index=0,
                                      format_func=lambda x: CURRENCIES[x])
            
            **role = st.radio("🎭 نوع حسابك", ["customer", "owner"], index=1,  # افتراضي مالك
                            format_func=lambda x: "🛒 مشتري" if x=="customer" else "👑 مالك متجر")**
            
            submitted = st.form_submit_button("🚀 أنشئ حسابي الآن", use_container_width=True)
            
            if submitted and email and password and password == confirm_password:
                if safe_query("SELECT * FROM users WHERE email=?", (email,)).empty:
                    # ✅ تسجيل فوري بدون أي تأخير
                    conn = sqlite3.connect('business_personal.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO users (email, password_hash, role, country, currency, phone) VALUES (?, ?, ?, ?, ?, ?)",
                             (email, hash_password(password), role, country, currency, phone))
                    conn.commit()
                    conn.close()
                    
                    st.session_state.user = {
                        'email': email, 'role': role, 
                        'country': country, 'currency': currency, 'phone': phone
                    }
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #11998e, #38ef7d); color: white; padding: 3rem; border-radius: 25px; text-align: center;'>
                        <h2>🎉 حسابك جاهز فوراً!</h2>
                        <h1>مرحباً {email}</h1>
                        <p>ابدأ متجرك أو تسوق الآن ✨</p>
                    </div>
                    """.format(email=email), unsafe_allow_html=True)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ هذا الإيميل مستخدم بالفعل")
            elif submitted:
                st.error("❌ تأكد من البيانات")
    
    with tab2:
        st.subheader("🔑 لديك حساب بالفعل؟")
        
        col1, col2 = st.columns(2)
        with col1:
            login_email = st.text_input("📧 بريدك الإلكتروني")
        with col2:
            login_password = st.text_input("🔐 كلمة المرور", type="password")
        
        if st.button("🚪 دخول إلى حسابي", use_container_width=True):
            users_df = safe_query("SELECT * FROM users")
            for _, user_row in users_df.iterrows():
                if (user_row['email'] == login_email and 
                    hash_password(login_password) == user_row['password_hash']):
                    st.session_state.user = {
                        'email': user_row['email'],
                        'role': user_row['role'],
                        'country': user_row['country'],
                        'currency': user_row['currency']
                    }
                    st.success(f"✅ مرحباً مرة أخرى {login_email}!")
                    st.rerun()
                    break
            else:
                st.error("❌ لا يوجد حساب بهذه البيانات")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ========================================================
# حساب مُسجل دخوله
else:
    # شريط التحكم الشخصي
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown(f"**👋 {st.session_state.user['email']}**")
    with col2:
        st.metric("🏠", COUNTRIES[st.session_state.user['country']])
        st.metric("💰", CURRENCIES[st.session_state.user['currency']])
    with col3:
        if st.button("🔓 خروج", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    
    # ✅ لوحة المالك الخاصة
    if st.session_state.user['role'] == 'owner':
        st.markdown("""
        <div style='background: linear-gradient(135deg, #11998e, #38ef7d); color: white; padding: 3rem; border-radius: 25px; text-align: center;'>
            <h1>👑 متجرك الخاص {email}</h1>
            <p>إدارة كاملة لمتجرك الشخصي</p>
        </div>
        """.format(email=st.session_state.user['email']), unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📦 منتجاتك", "🛒 طلباتك", "📊 إحصائياتك"])
        
        with tab1:
            st.header("➕ أضف منتجات لمتجرك")
            with st.form("owner_products"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("اسم المنتج")
                    price = st.number_input("السعر", min_value=1.0)
                with col2:
                    stock = st.number_input("المخزون", min_value=1)
                    category = st.selectbox("الفئة", ["إلكترونيات", "ملابس", "أغذية"])
                
                if st.form_submit_button("➕ إضافة لمتجري"):
                    conn = sqlite3.connect('business_personal.db')
                    conn.execute("""INSERT INTO products (owner_email, name, price, stock, category, currency) 
                                  VALUES (?, ?, ?, ?, ?, ?)""",
                               (st.session_state.user['email'], name, price, stock, category, 
                                st.session_state.user['currency']))
                    conn.commit()
                    st.success("✅ تمت الإضافة لمتجرك!")
            
            # منتجات هذا المالك
            my_products = safe_query("SELECT * FROM products WHERE owner_email=?", 
                                   (st.session_state.user['email'],))
            if my_products.empty:
                st.info("📦 لا توجد منتجات بعد - أضف الأول!")
            else:
                st.subheader("منتجات متجرك")
                st.dataframe(my_products)
        
        with tab2:
            my_orders = safe_query("""SELECT * FROM orders WHERE owner_email=? ORDER BY id DESC""", 
                                 (st.session_state.user['email'],))
            if my_orders.empty:
                st.info("📭 لا توجد طلبات بعد")
            else:
                st.dataframe(my_orders)
        
        with tab3:
            st.metric("💰 مبيعات متجرك", "0 ر.س")
            st.metric("📦 طلبات متجرك", "0 طلب")
    
    # ✅ متجر المشتري الخاص
    else:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 3rem; border-radius: 25px; text-align: center;'>
            <h1>🛒 تسوق من المتاجر</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # جميع المنتجات المتاحة من كل المالكين
        all_products = safe_query("SELECT * FROM products WHERE stock > 0")
        
        if not all_products.empty:
            st.subheader("🛍️ المنتجات المتاحة")
            cols = st.columns(3)
            for i, (_, product) in enumerate(all_products.iterrows()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style='background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center;'>
                        <img src='{product['image_url']}' style='width: 100%; height: 150px; object-fit: cover; border-radius: 10px;'>
                        <h4>{product['name']}</h4>
                        <h5 style='color: #11998e;'>{product['price']:.0f} {CURRENCIES.get(product['currency'], 'ر.س')}</h5>
                        <p>المخزون: {product['stock']}</p>
                        <small>👑 مالك: {product['owner_email']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # طلب من أي متجر
            with st.form("buy_form"):
                st.markdown("<div style='background: white; padding: 2rem; border-radius: 20px;'>", unsafe_allow_html=True)
                st.subheader("📋 اطلب الآن")
                
                customer_name = st.text_input("الاسم الكامل *")
                phone = st.text_input("رقم الجوال *")
                address = st.text_area("العنوان *")
                
                selected_products = st.multiselect("المنتجات المطلوبة", all_products['name'].tolist())
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ اطلب الآن", use_container_width=True):
                        if customer_name and phone and address and selected_products:
                            # البحث عن مالك المنتجات
                            owners = set()
                            for prod_name in selected_products:
                                owner = all_products[all_products['name'] == prod_name]['owner_email'].iloc[0]
                                owners.add(owner)
                            
                            # حفظ الطلب لكل مالك
                            conn = sqlite3.connect('business_personal.db')
                            for owner_email in owners:
                                conn.execute("""INSERT INTO orders (owner_email, customer_email, customer_name, phone, address, products) 
                                              VALUES (?, ?, ?, ?, ?, ?)""",
                                           (owner_email, st.session_state.user['email'], customer_name, 
                                            phone, address, ";".join(selected_products)))
                            conn.commit()
                            conn.close()
                            
                            st.success("✅ تم إرسال طلبك لأصحاب المتاجر!")
                            st.balloons()
                        else:
                            st.error("❌ املأ جميع الحقول")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("📦 لا توجد منتجات متاحة حالياً")

# Footer
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #666; margin-top: 3rem;'>
    <h4>✅ كل شخص متجره الخاص - تسجيل فردي بدون OTP</h4>
    <p>أنشئ حسابك الآن وابدأ متجرك أو تسوق من المتاجر ✨</p>
</div>
""", unsafe_allow_html=True)
