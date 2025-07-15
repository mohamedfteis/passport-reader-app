import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import re

st.set_page_config(page_title="قراءة بيانات الجواز", layout="centered")
st.title("🛂 قراءة بيانات جواز السفر وتحويلها لتنسيق مخصص")

uploaded_file = st.file_uploader("📤 ارفع صورة الجواز (JPG أو PNG):", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="📷 صورة الجواز", use_container_width=True)
    with st.spinner("🔍 جاري تحليل الصورة..."):
        reader = easyocr.Reader(['en'], gpu=False)
        result = reader.readtext(np.array(image), detail=0)
        text = " ".join(result)

    with st.expander("عرض النص الكامل المستخرج"):
        st.text(text)

    passport_number = re.search(r'[A-Z0-9]{7,}', text)
    birth_date = re.search(r'\d{2}[A-Z]{3}\d{2}', text)
    expiry_date = re.findall(r'\d{2}[A-Z]{3}\d{2}', text)
    names = re.findall(r'([A-Z]{2,})/([A-Z]{2,})', text)

    passport_number = passport_number.group(0) if passport_number else ""
    birth_date = birth_date.group(0) if birth_date else ""
    expiry_date = expiry_date[1] if len(expiry_date) > 1 else ""
    surname, given_name = names[0] if names else ("", "")

    st.subheader("✏️ تحقق أو عدّل البيانات")
    col1, col2 = st.columns(2)
    with col1:
        surname = st.text_input("اللقب", surname.strip())
        given_name = st.text_input("الاسم", given_name.strip())
        gender = st.selectbox("الجنس", ["m", "f"])
    with col2:
        passport_number = st.text_input("رقم الجواز", passport_number)
        birth_date = st.text_input("تاريخ الميلاد (مثال: 04jun87)", birth_date.lower())
        expiry_date = st.text_input("تاريخ الانتهاء (مثال: 08jan35)", expiry_date.lower())
        nationality = st.text_input("الجنسية (مثال: lby)", "lby")

    st.subheader("📌 النتائج بالتنسيقات الخاصة")
    format1 = f"sr docs hk1-p-{nationality}-{passport_number}-{nationality}-{birth_date}-{gender}-{expiry_date}-{given_name}/{surname}"
    format2 = f"4-1fdocsp/{nationality[:2]}/{passport_number}/{nationality[:2]}/{birth_date}/{gender}/{expiry_date}/{given_name}/{surname}"
    st.code(format1, language="text")
    st.code(format2, language="text")

    colA, colB = st.columns(2)
    with colA:
        st.download_button("📥 تحميل كنص", data=f"{format1}\n{format2}", file_name="passport_output.txt")
    with colB:
        st.button("📋 نسخ للذاكرة", on_click=lambda: st.toast("تم النسخ (انسخه يدويًا من الأعلى)"))
