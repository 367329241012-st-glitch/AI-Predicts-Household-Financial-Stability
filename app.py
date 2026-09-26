import streamlit as st
import pandas as pd
import joblib

# ---------------------------------------------------------
# 1. การตั้งค่าหน้าเว็บและธีม (Page Config)
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI ทำนายความมั่นคงทางการเงินของครัวเรือน",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS เพื่อปรับแต่งปุ่ม ความโค้งมน และเงาของการ์ดให้ดูพรีเมียม
st.markdown("""
    <style>
    /* ปรับแต่งปุ่มกดทำนาย */
    .stButton>button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF2B2B 100%);
        color: white;
        font-weight: bold;
        font-size: 18px;
        border-radius: 12px;
        padding: 12px 24px;
        border: none;
        box-shadow: 0px 4px 12px rgba(255, 75, 75, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 16px rgba(255, 75, 75, 0.4);
    }
    /* ปรับแต่งส่วนหัวข้อ */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 24px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. ส่วนหัวข้อเว็บไซต์ (Header Section)
# ---------------------------------------------------------
st.markdown('<p class="main-header">💰 AI ทำนายความมั่นคงทางการเงินของครัวเรือน</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">กรอกข้อมูลทางการเงินเพื่อประมวลผลวิเคราะห์ความมั่นคงด้วยโมเดล Machine Learning</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. ส่วนรับข้อมูลผู้ใช้ (Input Form with Card Containers)
# ---------------------------------------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    # การ์ดฝั่งข้อมูลส่วนตัวและรายได้
    with st.container(border=True):
        st.subheader("👤 ข้อมูลทั่วไปและรายได้")
        
        # กำหนด value=None เพื่อให้ช่องเป็นค่าว่างเริ่มต้น
        age = st.number_input("อายุ (ปี)", min_value=18, max_value=100, value=None, placeholder="กรอกอายุ เช่น 35")
        monthly_income = st.number_input("รายได้ต่อเดือน (USD)", min_value=0.0, value=None, placeholder="กรอกรายได้ เช่น 3500.00")
        monthly_expenses = st.number_input("รายจ่ายต่อเดือน (USD)", min_value=0.0, value=None, placeholder="กรอกรายจ่าย เช่น 1500.00")
        savings = st.number_input("เงินออมสะสม (USD)", min_value=0.0, value=None, placeholder="กรอกเงินออม เช่น 10000.00")

with col2:
    # การ์ดฝั่งข้อมูลหนี้สิน
    with st.container(border=True):
        st.subheader("💳 ข้อมูลหนี้สินและสินเชื่อ")
        
        has_loan_option = st.radio("มีภาระหนี้สินหรือไม่", ["ไม่มี (No)", "มี (Yes)"], horizontal=True)
        has_loan = "Yes" if has_loan_option == "มี (Yes)" else "No"
        
        if has_loan == "Yes":
            monthly_emi = st.number_input("ค่างวดชำระหนี้ต่อเดือน (USD)", min_value=0.0, value=None, placeholder="เช่น 500.00")
            loan_amount = st.number_input("ยอดหนี้คงเหลือรวม (USD)", min_value=0.0, value=None, placeholder="เช่น 100000.00")
        else:
            monthly_emi = 0.0
            loan_amount = 0.0

        credit_score = st.slider("คะแนนเครดิต (Credit Score)", min_value=300, max_value=850, value=650, help="คะแนนมาตรฐานอยู่ระหว่าง 300 - 850")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. ปุ่มประมวลผลและการแสดงผลลัพธ์ (Prediction & Metrics)
# ---------------------------------------------------------
if st.button("🔍 ทำนายความมั่นคงทางการเงิน", use_container_width=True):
    
    # ตรวจสอบว่าผู้ใช้กรอกข้อมูลสำคัญครบถ้วนหรือไม่
    if age is None or monthly_income is None or monthly_expenses is None or savings is None:
        st.warning("⚠️ กรุณากรอกข้อมูลในช่องตัวเลขให้ครบถ้วนก่อนทำการประมวลผล")
    elif has_loan == "Yes" and (monthly_emi is None or loan_amount is None):
        st.warning("⚠️ กรุณากรอกข้อมูลค่างวดและยอดหนี้คงเหลือให้ครบถ้วน")
    else:
        # คำนวณอัตราส่วนสำคัญ (Feature Engineering)
        debt_to_income = (monthly_emi / monthly_income) if monthly_income > 0 else 0
        savings_to_income = (savings / monthly_income) if monthly_income > 0 else 0
        surplus_ratio = ((monthly_income - monthly_expenses) / monthly_income) if monthly_income > 0 else 0

        # จัดเตรียมข้อมูลส่งเข้าโมเดล
        input_data = pd.DataFrame([{
            'age': age,
            'monthly_income_usd': monthly_income,
            'monthly_expenses_usd': monthly_expenses,
            'savings_usd': savings,
            'loan_amount_usd': loan_amount,
            'monthly_emi_usd': monthly_emi,
            'debt_to_income_ratio': debt_to_income,
            'credit_score': credit_score,
            'savings_to_income_ratio': savings_to_income
        }])

        # พยายามโหลดและทำนายผลจากโมเดล
        try:
            model = joblib.load('model.joblib')
            prediction = model.predict(input_data)[0]
        except Exception:
            # เงื่อนไขสำรอง (Fallback) หากโมเดลยังไม่ถูกโหลด
            if debt_to_income < 0.35 and savings_to_income > 3:
                prediction = "Stable"
            elif debt_to_income < 0.5:
                prediction = "Moderate"
            else:
                prediction = "Unstable"

        # แสดงผลลัพธ์การวิเคราะห์
        with st.container(border=True):
            st.subheader("📊 ผลการวิเคราะห์และดัชนีทางการเงิน")
            
            # สรุปสัดส่วนสำคัญเป็น Metrics
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("สัดส่วนหนี้สินต่อรายได้ (DTI)", f"{debt_to_income*100:.1f}%", delta="ควรน้อยกว่า 35%" if debt_to_income <= 0.35 else "ค่อนข้างสูง", delta_color="inverse")
            m_col2.metric("เงินออมสำรอง (เท่าของรายได้)", f"{savings_to_income:.1f} เท่า", delta="ปลอดภัย (>3 เท่า)" if savings_to_income >= 3 else "ควรเพิ่มเงินออม")
            m_col3.metric("สัดส่วนเงินคงเหลือสุทธิ", f"{surplus_ratio*100:.1f}%")

            st.divider()

            # แสดงการ์ดสถานะผลลัพธ์
            if prediction == "Stable":
                st.success("🟢 **สถานะ: มีความมั่นคงทางการเงินสูง (Stable)**")
                st.write("✨ **คำแนะนำ:** ครัวเรือนมีสภาพคล่องและสัดส่วนหนี้สินอยู่ในระดับปลอดภัย สามารถพิจารณาลงทุนเพิ่มเติมเพื่อสร้างความมั่งคั่งระยะยาวได้")
            elif prediction == "Moderate":
                st.warning("🟡 **สถานะ: มีความมั่นคงทางการเงินปานกลาง (Moderate)**")
                st.write("⚠️ **คำแนะนำ:** ควรระมัดระวังการก่อหนี้สินเพิ่ม ควบคุมรายจ่ายที่ไม่จำเป็น และสะสมเงินออมสำรองฉุกเฉินให้ครอบคลุมอย่างน้อย 3-6 เดือน")
            else:
                st.error("🔴 **สถานะ: มีความเสี่ยงทางการเงิน (Unstable)**")
                st.write("🚨 **คำแนะนำ:** มีสัดส่วนภาระหนี้สินหรือรายจ่ายสูงเกินเกณฑ์ปลอดภัย ควรวางแผนปรับลดรายจ่าย รีไฟแนนซ์ปรับโครงสร้างหนี้ และเพิ่มแหล่งรายได้เสริมโดยด่วน")
