import streamlit as st
import pandas as pd
import joblib
import numpy as np

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="AI ทำนายความมั่นคงทางการเงินของครัวเรือน",
    page_icon="💰",
    layout="wide"
)

st.title("💰 AI ทำนายความมั่นคงทางการเงินของครัวเรือน")
st.write("กรอกข้อมูลทางการเงินเพื่อประมวลผลความมั่นคงด้วยโมเดล Machine Learning")

st.divider()

# 2. ฟอร์มรับข้อมูลจากผู้ใช้
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 ข้อมูลทั่วไปและรายได้")
    age = st.number_input("อายุ (ปี)", min_value=18, max_value=100, value=35)
    monthly_income = st.number_input("รายได้ต่อเดือน (USD)", min_value=0.0, value=3500.0, step=100.0)
    monthly_expenses = st.number_input("รายจ่ายต่อเดือน (USD)", min_value=0.0, value=1500.0, step=100.0)
    savings = st.number_input("เงินออมสะสม (USD)", min_value=0.0, value=10000.0, step=500.0)

with col2:
    st.subheader("💳 ข้อมูลหนี้สินและสินเชื่อ")
    has_loan = st.selectbox("มีภาระหนี้สินหรือไม่", ["No", "Yes"])
    
    if has_loan == "Yes":
        monthly_emi = st.number_input("ค่างวดชำระหนี้ต่อเดือน (USD)", min_value=0.0, value=300.0, step=50.0)
        loan_amount = st.number_input("ยอดหนี้คงเหลือรวม (USD)", min_value=0.0, value=15000.0, step=500.0)
    else:
        monthly_emi = 0.0
        loan_amount = 0.0

    credit_score = st.slider("คะแนนเครดิต (Credit Score)", min_value=300, max_value=850, value=650)

# คำนวณ Feature เพิ่มเติม
debt_to_income = (monthly_emi / monthly_income) if monthly_income > 0 else 0
savings_to_income = (savings / monthly_income) if monthly_income > 0 else 0

st.divider()

# 3. ส่วนประมวลผลและแสดงผลลัพธ์
if st.button("🔍 ทำนายความมั่นคงทางการเงิน", type="primary", use_container_width=True):
    
    # จัดรูปข้อมูลให้ตรงกับที่โมเดลใช้เทรน
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

    try:
        # โหลดโมเดล (แนะนำให้ใช้ joblib/pkl)
        model = joblib.load('model.joblib')
        prediction = model.predict(input_data)[0]
    except Exception as e:
        # Fallback กรณีไม่มีไฟล์โมเดลหรือโหลดไม่ผ่าน
        if debt_to_income < 0.35 and savings_to_income > 3:
            prediction = "Stable"
        elif debt_to_income < 0.5:
            prediction = "Moderate"
        else:
            prediction = "Unstable"

    # แสดงผลลัพธ์
    st.subheader("📊 ผลการวิเคราะห์")
    if prediction == "Stable":
        st.success("🟢 **สถานะ: มีความมั่นคงทางการเงินสูง (Stable)**")
        st.write("ครัวเรือนมีสภาพคล่องดี มีสัดส่วนเงินออมและภาระหนี้สินอยู่ในเกณฑ์ปลอดภัย")
    elif prediction == "Moderate":
        st.warning("🟡 **สถานะ: มีความมั่นคงทางการเงินปานกลาง (Moderate)**")
        st.write("ควรระมัดระวังการสร้างหนี้สินเพิ่ม และสะสมเงินออมสำรองฉุกเฉิน")
    else:
        st.error("🔴 **สถานะ: มีความเสี่ยงทางการเงิน (Unstable)**")
        st.write("ควรปรับลดรายจ่าย ชะลอการสร้างหนี้สิน และเพิ่มสัดส่วนเงินออมทันที")
