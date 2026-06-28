import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- إعدادات واجهة المستخدم ---
st.set_page_config(page_title="نظام حساب الرواتب والحضور", layout="wide", page_icon="💼")
st.title("💼 نظام حساب رواتب الموظفين (بناءً على الحضور والانصراف)")
st.markdown("---")

# --- رفع الملف ---
uploaded_file = st.file_uploader("📂 قم برفع شيت الحضور (CSV)", type=['csv'])

# --- المدخلات ---
col1, col2, col3 = st.columns(3)

with col1:
    employee_salary = st.number_input("💰 الراتب الشهري للموظف", min_value=0.0, value=3000.0, step=100.0)
    expected_check_in = st.time_input("⏰ موعد الحضور الرسمي")
    
with col2:
    date_range = st.date_input("📅 الفترة الزمنية (من - إلى)", [])
    off_days = st.multiselect(
        "🏖️ أيام الإجازة الأسبوعية",
        options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        default=['Friday', 'Saturday'],
        format_func=lambda x: {
            'Monday': 'الاثنين', 'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء', 
            'Thursday': 'الخميس', 'Friday': 'الجمعة', 'Saturday': 'السبت', 'Sunday': 'الأحد'
        }[x]
    )

with col3:
    manual_deductions = st.number_input("➖ خصومات يدوية أخرى", min_value=0.0, value=0.0, step=50.0)
    manual_bonuses = st.number_input("➕ حوافز وإضافات يدوية", min_value=0.0, value=0.0, step=50.0)

# --- معالجة البيانات ---
if st.button("🚀 احسب الراتب النهائي") and uploaded_file is not None:
    if len(date_range) != 2:
        st.error("يرجى تحديد بداية ونهاية الفترة الزمنية بشكل صحيح.")
    else:
        start_date, end_date = date_range
        
        # قراءة الشيت
        df = pd.read_csv(uploaded_file)
        
        # تنظيف عمود التاريخ والوقت (معالجة رموز الصباح والمساء من أجهزة البصمة)
        # Õ غالباً تعني AM (صباحاً) و ã تعني PM (مساءً)
        df['Date/Time'] = df['Date/Time'].astype(str)
        df['Date/Time'] = df['Date/Time'].str.replace('Õ', 'AM').str.replace('ã', 'PM')
        df['Date/Time'] = df['Date/Time'].str.replace('ص', 'AM').str.replace('م', 'PM')
        
        # تحويل العمود إلى صيغة التاريخ والوقت الخاصة ببايثون
        df['Date/Time'] = pd.to_datetime(df['Date/Time'], format='%d/%m/%Y %I:%M:%S %p', errors='coerce')
        df = df.dropna(subset=['Date/Time']) # إزالة أي صفوف لم يتم التعرف على تاريخها
        
        # فصل التاريخ عن الوقت
        df['Date'] = df['Date/Time'].dt.date
        df['Time'] = df['Date/Time'].dt.time
        df['Day_Name'] = df['Date/Time'].dt.day_name()
        
        # تصفية البيانات بناءً على الفترة الزمنية المحددة
        mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
        df_filtered = df.loc[mask]
        
        # إنشاء قائمة بكل الأيام في الفترة المحددة
        delta = end_date - start_date
        all_dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
        
        # متغيرات الحساب
        absent_days = 0
        quarter_day_deductions = 0
        half_day_deductions = 0
        
        # استخراج أوقات الحضور الفعالة (أول بصمة في اليوم لكل موظف)
        # بافتراض أننا نتعامل مع موظف واحد حالياً، أو نأخذ بيانات الموظف الموجود في الشيت
        daily_checkins = df_filtered.groupby('Date')['Date/Time'].min().dt.time.to_dict()
        
        for current_date in all_dates:
            day_name = current_date.strftime('%A')
            
            # تجاهل أيام الإجازة الأسبوعية
            if day_name in off_days:
                continue
                
            # التحقق من الغياب
            if current_date not in daily_checkins:
                absent_days += 1
            else:
                # التحقق من التأخير
                actual_time = daily_checkins[current_date]
                
                # تحويل الأوقات إلى دقائق لتسهيل المقارنة
                expected_mins = expected_check_in.hour * 60 + expected_check_in.minute
                actual_mins = actual_time.hour * 60 + actual_time.minute
                
                delay_mins = actual_mins - expected_mins
                
                if delay_mins > 30:
                    half_day_deductions += 1
                elif delay_mins >= 15:
                    quarter_day_deductions += 1
                    
        # --- الحسابات المالية ---
        daily_rate = employee_salary / 30.0
        
        total_deduction_days = absent_days + (quarter_day_deductions * 0.25) + (half_day_deductions * 0.5)
        attendance_deductions_value = total_deduction_days * daily_rate
        
        net_salary = employee_salary - attendance_deductions_value - manual_deductions + manual_bonuses
        
        # --- عرض النتائج ---
        st.markdown("### 📊 تقرير الحضور والخصومات")
        
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)
        res_col1.metric("أيام الغياب الكاملة", f"{absent_days} يوم")
        res_col2.metric("تأخير (>15 دقيقة) [خصم ربع يوم]", f"{quarter_day_deductions} مرة")
        res_col3.metric("تأخير (>30 دقيقة) [خصم نصف يوم]", f"{half_day_deductions} مرة")
        res_col4.metric("قيمة الخصومات من الحضور", f"{attendance_deductions_value:,.2f} جنيه")
        
        st.markdown("### 💵 الملخص المالي")
        
        fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
        fin_col1.metric("الراتب الأساسي", f"{employee_salary:,.2f}")
        fin_col2.metric("إجمالي الخصومات (حضور + يدوي)", f"{(attendance_deductions_value + manual_deductions):,.2f}")
        fin_col3.metric("إجمالي الإضافات", f"{manual_bonuses:,.2f}")
        fin_col4.metric("صافي الراتب المستحق", f"{net_salary:,.2f}", delta=f"{manual_bonuses - (attendance_deductions_value + manual_deductions):,.2f}")
