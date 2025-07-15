import streamlit as st
import easyocr
from PIL import Image, ImageEnhance
import numpy as np
import re

st.set_page_config(page_title="قارئ جواز السفر المحسن", layout="centered")
st.title("🛂 قارئ جواز السفر - نسخة محسّنة")

def preprocess_image(image):
    image = image.convert("L")  # تحويل إلى تدرج رمادي
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # تعزيز التباين
    return image

uploaded_file = st.file_uploader("📤 ارفع صورة الجواز (PNG أو JPG):", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="📷 الصورة الأصلية", use_container_width=True)

    st.subheader("🧪 التحليل والقراءة...")
    with st.spinner("جارٍ تحليل النص..."):
        processed_image = preprocess_image(image)
        reader = easyocr.Reader(['en', 'ar'], gpu=False)
        result = reader.readtext(np.array(processed_image), detail=0)
        text = " ".join(result)

    with st.expander("عرض النص الكامل المستخرج"):
        st.text(text)

    # استخراج المعلومات باستخدام regex
    passport_number = re.search(r'\b[A-Z0-9]{7,}\b', text)
    birth_date = re.search(r'\b\d{2}[A-Z]{3}\d{2}\b', text)
    expiry_date = re.findall(r'\b\d{2}[A-Z]{3}\d{2}\b', text)
    names = re.findall(r'(MR|MRS)\s([A-Z]+)\s*/\s*([A-Z]+)', text)

    passport_number = passport_number.group(0) if passport_number else ""
    birth_date = birth_date.group(0) if birth_date else ""
    expiry_date = expiry_date[1] if len(expiry_date) > 1 else (expiry_date[0] if expiry_date else "")
    if names:
        title, surname, given_name = names[0]
        gender = 'm' if title == 'MR' else 'f'
    else:
        surname, given_name, gender = "", "", "m"

    st.subheader("✏️ تحقق أو عدّل البيانات")
    col1, col2 = st.columns(2)
    with col1:
        surname = st.text_input("اللقب", surname)
        given_name = st.text_input("الاسم", given_name)
        gender = st.selectbox("الجنس", ["m", "f"], index=0 if gender == "m" else 1)
    with col2:
        passport_number = st.text_input("رقم الجواز", passport_number)
        birth_date = st.text_input("تاريخ الميلاد (مثال: 12jun99)", birth_date.lower())
        expiry_date = st.text_input("تاريخ الانتهاء (مثال: 12jun28)", expiry_date.lower())
        nationality = st.text_input("الجنسية (مثال: lby)", "lby")

    st.subheader("📌 التنسيقات الجاهزة")
    format1 = f"sr docs hk1-p-{nationality}-{passport_number}-{nationality}-{birth_date}-{gender}-{expiry_date}-{given_name}/{surname}"
    format2 = f"4-1fdocsp/{nationality[:2]}/{passport_number}/{nationality[:2]}/{birth_date}/{gender}/{expiry_date}/{given_name}/{surname}"
    st.code(format1)
    st.code(format2)

    st.download_button("📥 تحميل النص", data=f"{format1}\n{format2}", file_name="passport_output.txt")
