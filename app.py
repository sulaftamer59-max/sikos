"""
🚀 تطبيق رواد الأعمال المتقدم | مالك + مشتري | تحليلات كاملة ✅
═══════════════════════════════════════════════════════════════════════════════
صفحة مالك سرية + متجر للمشترين + تحليلات + إشعارات + سرعة البيع
✅ الكود مُصحح بدون تغيير الصفات
"""

import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime, date
import plotly.express as px
import hashlib

# ========================================================
# تصميم فاخر احترافي
st.markdown("""
<style>
:root {
  --primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  --warning: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
.owner-section { background: rgba(255,255,255,0.95); padding: 2rem; border-radius: 25px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); }
.customer-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 3rem; border-radius: 25px; }
.product-card { background: rgba(255,255,255,0.9); border-radius: 20px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
.metric-card { background: rgba(255,255,255,0.95); padding: 2rem; border-radius: 25px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ========================================================
st.set_page_config(page_title="🚀 متجر رواد الأعمال", page_icon="🚀", layout="wide")

# ========================================================
# نظام تسجيل الدخول للمالك
def get_owner_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

OWNER_PASSWORD = "admin123"  # غيّر هذا لكلمة المرور الخاصة بك
OWNER_HASH = get_owner_hash(OWNER_PASSWORD)

# جلسة المستخدم
if 'is_owner' not in st.session_state:
    st.session_state.is_owner = False
if 'customer_order' not in st.session_state:
    st.session_state.customer_order = None

# ========================================================
# قاعدة البيانات المتقدمة - مُصححة
@st.cache_resource
def init_db():
    """إنشاء اتصال آمن بقاعدة البيانات"""
    conn = sqlite3.connect('business_pro.db', check_same_thread=False)
    c = conn.cursor()
    
    # المنتجات مع الصور
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, price REAL DEFAULT 0, cost REAL DEFAULT 0,
        stock INTEGER DEFAULT 0, image_url TEXT, category TEXT, 
        sales_count INTEGER DEFAULT 0, first_sale TEXT, last_sale TEXT, 
        sell_speed REAL DEFAULT 0)''')
    
    # طلبات المشترين
    c.execute('''CREATE TABLE IF NOT EXISTS customer_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, phone TEXT, 
        backup_phone TEXT, address TEXT, products TEXT, total REAL DEFAULT 0, 
        order_date TEXT, status TEXT DEFAULT 'جديد')''')
    
    # المبيعات للتحليلات
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, qty INTEGER,
        total REAL DEFAULT 0, sale_date TEXT)''')
    
    # الإشعارات
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, date TEXT, 
        read_status INTEGER DEFAULT 0)''')
    
    # إضافة منتجات تجريبية
    c.execute("INSERT OR IGNORE INTO products (id, name, price, stock, image_url, category) VALUES " +
             "(1,'لابتوب گيمنگ',3500,10,'https://via.placeholder.com/300x200/667eea/ffffff?text=لابتوب','إلكترونيات')," +
             "(2,'آيفون 15 برو',4500,5,'https://via.placeholder.com/300x200/764ba2/ffffff?text=آيفون','موبايلات')," +
             "(3,'سماعات بلوتوث',250,25,'https://via.placeholder.com/300x200/11998e/ffffff?text=سماعات','إكسسوارات')")
    
    conn.commit()
    return conn

def add_notification(message):
    """إضافة إشعار جديد"""
    try:
        conn = sqlite3.connect('business_pro.db')
        c = conn.cursor()
        c.execute("INSERT INTO notifications (message, date) VALUES (?, ?)", 
                 (message, str(datetime.now())))
        conn.commit()
        conn.close()
    except:
        pass

def safe_query(query, params=None):
    """استعلام آمن من قاعدة البيانات"""
    try:
        conn = sqlite3.connect('business_pro.db')
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df if not df.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

# ========================================================
# الصفحة الرئيسية - اختيار المستخدم
st.title("🚀 متجر رواد الأعمال المتقدم")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="customer-section">
        <h2>👤 أنت مشتري؟</h2>
        <p>تصفح المنتجات واطلب بسهولة!</p>
    """, unsafe_allow_html=True)
    
    if st.button("🛒 متجر المشتري", use_container_width=True):
        st.session_state.is_owner = False
        st.rerun()

with col2:
    st.markdown("""
    <div class="owner-section">
        <h3>👑 منطقة المالك السرية</h3>
        <p>ادخل كلمة المرور للوصول للتحكم الكامل</p>
    """, unsafe_allow_html=True)
    
    owner_password = st.text_input("🔐 كلمة المرور", type="password")
    if st.button("🚪 دخول المالك", use_container_width=True):
        if get_owner_hash(owner_password) == OWNER_HASH:
            st.session_state.is_owner = True
            st.success("✅ مرحباً بك يا مالك المتجر!")
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة")

# ========================================================
# صفحة المشتري ✅ مُصححة
if not st.session_state.is_owner:
    st.markdown("<h1 style='text-align: center; color: white;'>🛒 متجر المنتجات</h1>", unsafe_allow_html=True)
    
    # عرض المنتجات بصور جميلة
    products_df = safe_query("SELECT * FROM products WHERE stock > 0 ORDER BY sales_count DESC")
    
    if products_df.empty:
        st.info("📦 لا توجد منتجات متاحة حالياً")
        st.markdown("""
        <div class="owner-section">
            <h3>💡 نصيحة للمالك</h3>
            <p>أضف منتجات في لوحة التحكم ليتمكن العملاء من الشراء</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # عرض المنتجات في شبكة
        cols = st.columns(3)
        for idx, (_, product) in enumerate(products_df.iterrows()):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="product-card">
                    <h3>{product['name']}</h3>
                    <img src="https://via.placeholder.com/300x200/667eea/ffffff?text={product['name'][:10]}" 
                         style="width: 100%; border-radius: 15px; height: 150px; object-fit: cover;">
                    <h4 style="color: #11998e;">{product['price']:.0f} ر.س</h4>
                    <p><strong>المخزون:</strong> {int(product['stock'])}</p>
                    <p><em>⭐ مبيعات: {int(product['sales_count'])}</em></p>
                </div>
                """, unsafe_allow_html=True)
        
        # نموذج الطلب ✅ مُصحح
        with st.form("customer_order"):
            st.markdown("<div class='owner-section'>", unsafe_allow_html=True)
            st.subheader("📋 معلومات العميل")
            customer_name = st.text_input("الاسم الكامل *")
            phone = st.text_input("رقم الجوال *", help="مثال: 0501234567")
            backup_phone = st.text_input("رقم احتياطي")
            address = st.text_area("العنوان التفصيلي *", 
                                 placeholder="الحي، الشارع، رقم الشقة، المدينة")
            
            st.subheader("🛒 المنتجات المطلوبة")
            selected_products = st.multiselect("اختر المنتجات", 
                                             products_df['name'].tolist())
            
            quantities = {}
            total_price = 0
            if selected_products:
                for prod in selected_products:
                    quantities[prod] = st.number_input(
                        f"كمية {prod}", 
                        min_value=1, value=1, key=f"qty_{hash(prod)}"
                    )
                
                # حساب المجموع
                total_price = sum([
                    float(products_df[products_df['name']==p]['price'].iloc[0]) * quantities[p]
                    for p in selected_products
                ])
            
            col1, col2 = st.columns([3,1])
            with col1:
                submitted = st.form_submit_button("✅ تأكيد الطلب", use_container_width=True)
            with col2:
                st.metric("💰 المجموع", f"{total_price:.0f} ر.س")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submitted and customer_name and phone and address and selected_products:
                # حفظ الطلب ✅ مُصحح
                products_info = "; ".join([f"{p}: {quantities[p]}" for p in selected_products])
                
                conn = sqlite3.connect('business_pro.db')
                c = conn.cursor()
                c.execute("""INSERT INTO customer_orders 
                           (customer_name, phone, backup_phone, address, products, total, order_date)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                         (customer_name, phone, backup_phone, address, products_info, total_price, str(date.today())))
                order_id = c.lastrowid
                conn.commit()
                conn.close()
                
                # إشعار المالك
                add_notification(f"🛒 طلب جديد #{order_id} من {customer_name} | المبلغ: {total_price:.0f} ر.س")
                
                st.success(f"""
                ✅ تم تسجيل طلبك #{order_id} 
                💰 المجموع: {total_price:.0f} ر.س
                📞 سنتصل بك قريباً على {phone}
                """)
                st.balloons()
                
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📄 ملخص الطلب #{order_id}</h3>
                    <p><strong>الاسم:</strong> {customer_name}</p>
                    <p><strong>الهاتف:</strong> {phone}</p>
                    <p><strong>المنتجات:</strong> {products_info}</p>
                </div>
                """, unsafe_allow_html=True)

# ========================================================
# صفحة المالك السرية ✅ مُصححة
else:
    st.markdown("<h1 style='text-align: center; color: #11998e;'>👑 لوحة تحكم المالك</h1>", unsafe_allow_html=True)
    
    # شريط جانبي للمالك
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #11998e, #38ef7d); color: white; padding: 1rem; border-radius: 15px; text-align: center;'>
            <h3>👑 لوحة المالك</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # إحصائيات سريعة ✅ مُصححة
        products_count = len(safe_query("SELECT * FROM products"))
        new_orders = len(safe_query("SELECT * FROM customer_orders WHERE status='جديد'"))
        notifications_count = len(safe_query("SELECT * FROM notifications WHERE read_status=0"))
        
        st.metric("🛒 طلبات جديدة", new_orders)
        st.metric("📦 المنتجات", products_count)
        st.metric("🔔 الإشعارات", notifications_count)
        
        if st.button("🔓 خروج", use_container_width=True):
            st.session_state.is_owner = False
            st.rerun()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛒 الطلبات الجديدة", "📦 المخزون", "📊 التحليلات", "🔔 الإشعارات", "⚙️ الإعدادات"
    ])
    
    # تبويب الطلبات الجديدة ✅ مُصحح
    with tab1:
        st.header("🛒 الطلبات الجديدة")
        orders_df = safe_query("SELECT * FROM customer_orders ORDER BY id DESC LIMIT 20")
        
        if orders_df.empty:
            st.info("🎉 لا توجد طلبات جديدة!")
        else:
            for idx, (_, order) in enumerate(orders_df.iterrows()):
                with st.expander(f"طلب #{order['id']} | {order['customer_name']} | {order['total']:.0f} ر.س"):
                    st.markdown(f"""
                    <div class="metric-card">
                        <p><strong>📞 الهاتف:</strong> {order['phone']}</p>
                        <p><strong>📱 احتياطي:</strong> {order['backup_phone'] or 'غير محدد'}</p>
                        <p><strong>📍 العنوان:</strong> {order['address']}</p>
                        <p><strong>🛒 المنتجات:</strong> {order['products']}</p>
                        <p><strong>📅 التاريخ:</strong> {order['order_date']}</p>
                        <p><strong>📊 الحالة:</strong> <span style="color: {'green' if order['status']=='مُشحن' else 'orange'}">{order['status']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"✅ تم الشحن", key=f"ship_{order['id']}_{idx}", use_container_width=True):
                            conn = sqlite3.connect('business_pro.db')
                            c = conn.cursor()
                            c.execute("UPDATE customer_orders SET status='مُشحن' WHERE id=?", (order['id'],))
                            conn.commit()
                            conn.close()
                            st.success(f"✅ تم شحن الطلب #{order['id']}")
                            st.rerun()
                    with col2:
                        if st.button(f"❌ ملغي", key=f"cancel_{order['id']}_{idx}", use_container_width=True):
                            conn = sqlite3.connect('business_pro.db')
                            c = conn.cursor()
                            c.execute("UPDATE customer_orders SET status='ملغي' WHERE id=?", (order['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()
                    with col3:
                        if st.button(f"📞 اتصال", key=f"call_{order['id']}_{idx}", use_container_width=True):
                            st.info(f"📞 اتصل على: {order['phone']}")
    
    # تبويب المخزون ✅ مُصحح
    with tab2:
        st.header("📦 إدارة المخزون")
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("add_product_owner"):
                st.subheader("➕ إضافة منتج جديد")
                name = st.text_input("اسم المنتج")
                price = st.number_input("سعر البيع", min_value=0.0, value=100.0)
                cost = st.number_input("تكلفة الشراء", min_value=0.0, value=80.0)
                stock = st.number_input("المخزون", min_value=0, value=10)
                image_url = st.text_input("رابط الصورة", 
                                        value="https://via.placeholder.com/300x200/667eea/ffffff?text=منتج")
                category = st.selectbox("الفئة", ["إلكترونيات", "ملابس", "أغذية", "عام"])
                
                submitted = st.form_submit_button("➕ إضافة المنتج")
                if submitted and name:
                    conn = sqlite3.connect('business_pro.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO products (name,price,cost,stock,image_url,category) VALUES (?,?,?,?,?,?)",
                             (name, price, cost, stock, image_url, category))
                    conn.commit()
                    conn.close()
                    st.success("✅ تمت إضافة المنتج بنجاح!")
                    st.rerun()
        
        with col2:
            st.subheader("📋 قائمة المنتجات")
            products_df = safe_query("SELECT * FROM products ORDER BY sales_count DESC LIMIT 10")
            if not products_df.empty:
                st.dataframe(products_df[['name', 'price', 'stock', 'sales_count', 'category']])
    
    # تبويب التحليلات ✅ مُبسط
    with tab3:
        st.header("📊 تحليلات المبيعات")
        orders_df = safe_query("SELECT * FROM customer_orders")
        
        if not orders_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 إجمالي المبيعات", f"{orders_df['total'].sum():.0f} ر.س")
                st.metric("📦 عدد الطلبات", len(orders_df))
                st.metric("⭐ متوسط الطلب", f"{orders_df['total'].mean():.0f} ر.س")
            
            with col2:
                # أفضل منتج
                all_products = "; ".join(orders_df['products'].tolist())
                top_product = max(set(all_products.split(";")), key=all_products.split(";").count)
                st.metric("🥇 أفضل منتج", top_product[:20] + "...")
        else:
            st.info("📊 أضف بعض الطلبات لرؤية التحليلات")
    
    # الإشعارات ✅ مُصحح
    with tab4:
        st.header("🔔 الإشعارات")
        notifications_df = safe_query("SELECT * FROM notifications ORDER BY date DESC LIMIT 20")
        if notifications_df.empty:
            st.info("🔔 لا توجد إشعارات جديدة")
        else:
            for _, notif in notifications_df.iterrows():
                st.info(notif['message'])
    
    # الإعدادات
    with tab5:
        st.header("⚙️ إعدادات النظام")
        st.success(f"**كلمة مرور المالك: `{OWNER_PASSWORD}`**")
        st.info("""
        🔧 **تعليمات الأمان:**
        1. غيّر `OWNER_PASSWORD` في السطر 26
        2. احفظ الملف وأعد تشغيل التطبيق
        3. شارك رابط التطبيق مع العملاء
        """)

# Footer
st.markdown("""
<div style='text-align: center; padding: 3rem; color: #666; background: rgba(255,255,255,0.1); border-radius: 20px; margin-top: 3rem;'>
    <h3>✅ تطبيق رواد الأعمال المتقدم - مالك + مشتري</h3>
    <p>جاهز للنشر العام | أي شخص يدخل يقدر يشتري! ✨</p>
</div>
""", unsafe_allow_html=True)
