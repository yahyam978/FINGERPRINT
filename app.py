import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta, date
import io

st.set_page_config(
    page_title="نظام الحضور والانصراف",
    page_icon="🕐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    * { font-family: 'Cairo', sans-serif !important; }
    
    .main { direction: rtl; }
    
    .stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); }
    
    .main-header {
        background: linear-gradient(90deg, #1a1a2e, #16213e, #0f3460);
        border: 1px solid #e94560;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(233,69,96,0.3);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 0 20px rgba(233,69,96,0.5);
    }
    
    .main-header p {
        color: #a0aec0;
        margin: 8px 0 0 0;
        font-size: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    
    .metric-card:hover { transform: translateY(-2px); }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 5px 0;
    }
    
    .metric-label {
        color: #a0aec0;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .red-val { color: #fc5c7d; }
    .yellow-val { color: #f7971e; }
    .orange-val { color: #fd7238; }
    .green-val { color: #11998e; }
    .blue-val { color: #4facfe; }
    .purple-val { color: #c471ed; }
    
    .salary-box {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(17,153,142,0.4);
    }
    
    .salary-box .amount {
        font-size: 3rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .salary-box .label {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .detail-table {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        margin: 15px 0;
    }
    
    .detail-table table {
        width: 100%;
        border-collapse: collapse;
        direction: rtl;
    }
    
    .detail-table th {
        background: #0f3460;
        color: #4facfe;
        padding: 12px 15px;
        text-align: right;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .detail-table td {
        padding: 10px 15px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        color: #e2e8f0;
        text-align: right;
        font-size: 0.85rem;
    }
    
    .detail-table tr:hover td { background: rgba(79,172,254,0.05); }
    
    .section-header {
        background: linear-gradient(90deg, #0f3460, #1a1a2e);
        border-right: 4px solid #e94560;
        border-radius: 8px;
        padding: 12px 18px;
        margin: 20px 0 12px 0;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        direction: rtl;
    }
    
    .info-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }
    
    .badge-red { background: rgba(252,92,125,0.2); color: #fc5c7d; border: 1px solid #fc5c7d; }
    .badge-yellow { background: rgba(247,151,30,0.2); color: #f7971e; border: 1px solid #f7971e; }
    .badge-orange { background: rgba(253,114,56,0.2); color: #fd7238; border: 1px solid #fd7238; }
    
    div[data-testid="stSidebar"] { background: #0f2027 !important; }
    
    .stButton > button {
        background: linear-gradient(90deg, #e94560, #0f3460) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Cairo', sans-serif !important;
        font-weight: 600 !important;
        padding: 12px 30px !important;
        width: 100% !important;
        font-size: 1.1rem !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(233,69,96,0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(233,69,96,0.5) !important;
    }
    
    label { color: #a0aec0 !important; font-weight: 600 !important; direction: rtl !important; }
    
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background: #1a1a2e !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
        direction: rtl !important;
    }
    
    .stDateInput input {
        background: #1a1a2e !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        direction: rtl !important;
    }
    
    .stTimeInput input {
        background: #1a1a2e !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        direction: rtl !important;
    }
    
    .stMultiSelect > div { direction: rtl !important; }
    
    .stSuccess { direction: rtl; }
    .stError { direction: rtl; }
    .stWarning { direction: rtl; }
    
    .deduction-row {
        background: #16213e;
        border-radius: 8px;
        padding: 12px 15px;
        margin: 5px 0;
        border-right: 3px solid;
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

DAYS_AR = {0: "الاثنين", 1: "الثلاثاء", 2: "الأربعاء", 3: "الخميس", 4: "الجمعة", 5: "السبت", 6: "الأحد"}
DAYS_EN = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]


def parse_attendance(df):
    df = df.copy()
    df.columns = ["Department", "Name", "No", "DateTime", "LocationID", "IDNumber", "VerifyCode", "CardNo"]
    df = df[df["DateTime"].notna()]
    df = df[df["DateTime"].astype(str).str.contains(r'\d{2}/\d{2}/\d{4}', regex=True, na=False)]

    def clean_dt(val):
        s = str(val).strip()
        # Remove trailing non-ascii chars
        clean = ''.join(c for c in s if c.isdigit() or c in '/:- ')
        clean = clean.strip()
        try:
            return datetime.strptime(clean, "%d/%m/%Y %H:%M:%S")
        except:
            try:
                return datetime.strptime(clean[:19], "%d/%m/%Y %H:%M:%S")
            except:
                return None

    df["ParsedDT"] = df["DateTime"].apply(clean_dt)
    df = df[df["ParsedDT"].notna()]
    df["Date"] = df["ParsedDT"].dt.date
    df["Time"] = df["ParsedDT"].dt.time
    return df


def get_first_punch(group):
    return group["ParsedDT"].min()


def analyze_attendance(df_parsed, start_date, end_date, required_time, off_days, salary):
    results = {
        "absent_days": [],
        "quarter_deductions": [],
        "half_deductions": [],
        "work_days": [],
        "on_time_days": []
    }

    required_dt = datetime.combine(date.today(), required_time)
    quarter_limit = (required_dt + timedelta(minutes=15)).time()
    half_limit = (required_dt + timedelta(minutes=30)).time()

    current = start_date
    while current <= end_date:
        weekday = current.weekday()  # 0=Mon,...,6=Sun
        day_name = DAYS_AR[weekday]

        if day_name in off_days:
            current += timedelta(days=1)
            continue

        day_records = df_parsed[df_parsed["Date"] == current]

        if day_records.empty:
            results["absent_days"].append({
                "date": current,
                "day": day_name,
                "reason": "غياب كامل - لا توجد بصمة"
            })
        else:
            first_punch = day_records["ParsedDT"].min().time()
            if first_punch >= half_limit:
                results["half_deductions"].append({
                    "date": current,
                    "day": day_name,
                    "punch_time": first_punch,
                    "delay": f"تأخر {_diff_minutes(required_time, first_punch)} دقيقة"
                })
            elif first_punch >= quarter_limit:
                results["quarter_deductions"].append({
                    "date": current,
                    "day": day_name,
                    "punch_time": first_punch,
                    "delay": f"تأخر {_diff_minutes(required_time, first_punch)} دقيقة"
                })
            else:
                results["on_time_days"].append({"date": current, "day": day_name, "punch_time": first_punch})

            results["work_days"].append(current)

        current += timedelta(days=1)

    day_rate = salary / 30
    absent_deduction = len(results["absent_days"]) * day_rate
    quarter_deduction = len(results["quarter_deductions"]) * (day_rate / 4)
    half_deduction = len(results["half_deductions"]) * (day_rate / 2)
    total_auto_deduction = absent_deduction + quarter_deduction + half_deduction

    return results, day_rate, absent_deduction, quarter_deduction, half_deduction, total_auto_deduction


def _diff_minutes(t1, t2):
    dt1 = datetime.combine(date.today(), t1)
    dt2 = datetime.combine(date.today(), t2)
    diff = (dt2 - dt1).seconds // 60
    return diff


# ─── UI ────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🕐 نظام تحليل الحضور والانصراف</h1>
    <p>تحليل شامل للحضور والتأخير واحتساب الخصومات والراتب المستحق</p>
</div>
""", unsafe_allow_html=True)

# Sidebar inputs
with st.sidebar:
    st.markdown("### 📁 رفع ملف الحضور")
    uploaded = st.file_uploader("اختر ملف الحضور (.xls / .xlsx)", type=["xls", "xlsx"])

    st.markdown("---")
    st.markdown("### ⚙️ إعدادات الموظف")

    required_hour = st.number_input("ساعة الحضور المطلوبة", min_value=0, max_value=23, value=7, step=1)
    required_minute = st.number_input("الدقيقة", min_value=0, max_value=59, value=0, step=1)
    required_time = time(required_hour, required_minute)
    st.caption(f"⏰ موعد الحضور: {required_time.strftime('%H:%M')}")

    st.markdown("---")
    off_days_selected = st.multiselect(
        "أيام الإجازة الأسبوعية",
        options=DAYS_EN,
        default=["الجمعة", "السبت"]
    )

    st.markdown("---")
    st.markdown("### 📅 الفترة الزمنية")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من", value=date(2026, 6, 1))
    with col2:
        end_date = st.date_input("إلى", value=date(2026, 6, 30))

    st.markdown("---")
    st.markdown("### 💰 بيانات الراتب")
    salary = st.number_input("الراتب الأساسي (جنيه)", min_value=0.0, value=5000.0, step=100.0)

    st.markdown("---")
    st.markdown("### ✏️ تعديلات يدوية")
    extra_deductions = st.number_input("خصومات إضافية أخرى (جنيه)", min_value=0.0, value=0.0, step=50.0,
                                       help="أي خصومات إضافية غير محسوبة تلقائياً")
    incentives = st.number_input("حوافز وإضافات (جنيه)", min_value=0.0, value=0.0, step=50.0,
                                 help="أي مكافآت أو حوافز إضافية")
    extra_deductions_note = st.text_input("ملاحظة الخصومات الإضافية", placeholder="سبب الخصم...")
    incentives_note = st.text_input("ملاحظة الحوافز", placeholder="سبب الحافز...")

    st.markdown("---")
    analyze_btn = st.button("🔍 تحليل الحضور")


# Main content
if not uploaded:
    st.info("👈 يرجى رفع ملف الحضور من الشريط الجانبي للبدء")

    st.markdown("""
    <div style='background:#1a1a2e;border-radius:12px;padding:25px;border:1px solid rgba(255,255,255,0.1);direction:rtl;margin-top:20px;'>
        <h3 style='color:#4facfe;margin-top:0;'>📌 كيفية استخدام النظام</h3>
        <ol style='color:#a0aec0;line-height:2.2;'>
            <li>ارفع ملف الحضور (XLS/XLSX) من الشريط الجانبي الأيسر</li>
            <li>حدد موعد الحضور المطلوب للموظف</li>
            <li>اختر أيام الإجازة الأسبوعية</li>
            <li>حدد الفترة الزمنية المراد تحليلها</li>
            <li>أدخل الراتب الأساسي للموظف</li>
            <li>أضف أي خصومات أو حوافز إضافية يدوية</li>
            <li>اضغط "تحليل الحضور" للحصول على النتائج</li>
        </ol>
        <hr style='border-color:rgba(255,255,255,0.1);'/>
        <h4 style='color:#f7971e;'>📐 قواعد الحساب</h4>
        <ul style='color:#a0aec0;line-height:2.2;'>
            <li>🔴 <strong style='color:#fc5c7d;'>غياب كامل:</strong> لا توجد بصمة في اليوم → خصم يوم كامل</li>
            <li>🟡 <strong style='color:#f7971e;'>ربع يوم خصم:</strong> تأخر من 15 إلى 29 دقيقة عن الموعد</li>
            <li>🟠 <strong style='color:#fd7238;'>نصف يوم خصم:</strong> تأخر 30 دقيقة أو أكثر عن الموعد</li>
            <li>💵 <strong style='color:#4facfe;'>سعر اليوم:</strong> الراتب ÷ 30</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

elif analyze_btn or True:
    try:
        engine = "xlrd" if uploaded.name.endswith(".xls") else "openpyxl"
        df_raw = pd.read_excel(uploaded, header=None, engine=engine)
        df_parsed = parse_attendance(df_raw)

        if df_parsed.empty:
            st.error("❌ لم يتم العثور على بيانات صالحة في الملف")
        else:
            # Filter by date range
            df_range = df_parsed[
                (df_parsed["Date"] >= start_date) &
                (df_parsed["Date"] <= end_date)
            ]

            emp_name = df_parsed["Name"].iloc[0] if "Name" in df_parsed.columns else "الموظف"

            results, day_rate, absent_deduction, quarter_deduction, half_deduction, total_auto = analyze_attendance(
                df_range, start_date, end_date, required_time, off_days_selected, salary
            )

            total_deductions = total_auto + extra_deductions
            net_salary = salary + incentives - total_deductions

            # ── Summary metrics ──
            st.markdown(f"""
            <div class="section-header">
                👤 تقرير الموظف: {emp_name} &nbsp;|&nbsp; 
                📅 الفترة: {start_date.strftime('%d/%m/%Y')} – {end_date.strftime('%d/%m/%Y')}
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">أيام الغياب</div>
                    <div class="metric-value red-val">{len(results['absent_days'])}</div>
                    <div class="metric-label">يوم</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">ربع يوم خصم</div>
                    <div class="metric-value yellow-val">{len(results['quarter_deductions'])}</div>
                    <div class="metric-label">مرة</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">نصف يوم خصم</div>
                    <div class="metric-value orange-val">{len(results['half_deductions'])}</div>
                    <div class="metric-label">مرة</div>
                </div>""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">سعر اليوم</div>
                    <div class="metric-value blue-val">{day_rate:.1f}</div>
                    <div class="metric-label">جنيه</div>
                </div>""", unsafe_allow_html=True)
            with c5:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">إجمالي الخصومات</div>
                    <div class="metric-value red-val">{total_deductions:.1f}</div>
                    <div class="metric-label">جنيه</div>
                </div>""", unsafe_allow_html=True)
            with c6:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">أيام بالموعد</div>
                    <div class="metric-value green-val">{len(results['on_time_days'])}</div>
                    <div class="metric-label">يوم</div>
                </div>""", unsafe_allow_html=True)

            # ── Salary breakdown ──
            st.markdown('<div class="section-header">💰 تفصيل الراتب</div>', unsafe_allow_html=True)

            s1, s2 = st.columns(2)
            with s1:
                st.markdown(f"""
                <div style='background:#1a1a2e;border-radius:12px;padding:20px;border:1px solid rgba(255,255,255,0.1);direction:rtl;'>
                    <h4 style='color:#4facfe;margin-top:0;'>📊 تفاصيل الخصومات</h4>
                    <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                        <span style='color:#a0aec0;'>الراتب الأساسي</span>
                        <span style='color:white;font-weight:600;'>{salary:,.1f} جنيه</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                        <span style='color:#a0aec0;'>خصم الغياب ({len(results['absent_days'])} × {day_rate:.1f})</span>
                        <span style='color:#fc5c7d;font-weight:600;'>- {absent_deduction:,.1f} جنيه</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                        <span style='color:#a0aec0;'>خصم ربع يوم ({len(results['quarter_deductions'])} × {day_rate/4:.1f})</span>
                        <span style='color:#f7971e;font-weight:600;'>- {quarter_deduction:,.1f} جنيه</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                        <span style='color:#a0aec0;'>خصم نصف يوم ({len(results['half_deductions'])} × {day_rate/2:.1f})</span>
                        <span style='color:#fd7238;font-weight:600;'>- {half_deduction:,.1f} جنيه</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                        <span style='color:#a0aec0;'>خصومات إضافية {f"({extra_deductions_note})" if extra_deductions_note else ""}</span>
                        <span style='color:#fc5c7d;font-weight:600;'>- {extra_deductions:,.1f} جنيه</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                        <span style='color:#a0aec0;'>حوافز وإضافات {f"({incentives_note})" if incentives_note else ""}</span>
                        <span style='color:#38ef7d;font-weight:600;'>+ {incentives:,.1f} جنيه</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;padding:12px 0 0 0;margin-top:5px;'>
                        <span style='color:white;font-weight:700;font-size:1.1rem;'>إجمالي الخصومات</span>
                        <span style='color:#fc5c7d;font-weight:700;font-size:1.1rem;'>- {total_deductions:,.1f} جنيه</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with s2:
                st.markdown(f"""
                <div class="salary-box">
                    <div class="label">✅ الراتب المستحق</div>
                    <div class="amount">{net_salary:,.1f}</div>
                    <div class="label">جنيه مصري</div>
                </div>
                """, unsafe_allow_html=True)

            # ── Absence details ──
            if results["absent_days"]:
                st.markdown('<div class="section-header">🔴 تفاصيل أيام الغياب</div>', unsafe_allow_html=True)
                absence_data = []
                for i, d in enumerate(results["absent_days"], 1):
                    absence_data.append({
                        "#": i,
                        "التاريخ": d["date"].strftime("%d/%m/%Y"),
                        "اليوم": d["day"],
                        "السبب": d["reason"],
                        "الخصم": f"{day_rate:.1f} جنيه"
                    })
                df_absence = pd.DataFrame(absence_data)
                st.dataframe(df_absence, use_container_width=True, hide_index=True)

            # ── Quarter deductions ──
            if results["quarter_deductions"]:
                st.markdown('<div class="section-header">🟡 تفاصيل خصم ربع اليوم (تأخر 15-29 دقيقة)</div>', unsafe_allow_html=True)
                q_data = []
                for i, d in enumerate(results["quarter_deductions"], 1):
                    q_data.append({
                        "#": i,
                        "التاريخ": d["date"].strftime("%d/%m/%Y"),
                        "اليوم": d["day"],
                        "وقت البصمة": d["punch_time"].strftime("%H:%M:%S"),
                        "الموعد المطلوب": required_time.strftime("%H:%M"),
                        "التأخير": d["delay"],
                        "الخصم": f"{day_rate/4:.1f} جنيه"
                    })
                df_q = pd.DataFrame(q_data)
                st.dataframe(df_q, use_container_width=True, hide_index=True)

            # ── Half deductions ──
            if results["half_deductions"]:
                st.markdown('<div class="section-header">🟠 تفاصيل خصم نصف اليوم (تأخر 30 دقيقة أو أكثر)</div>', unsafe_allow_html=True)
                h_data = []
                for i, d in enumerate(results["half_deductions"], 1):
                    h_data.append({
                        "#": i,
                        "التاريخ": d["date"].strftime("%d/%m/%Y"),
                        "اليوم": d["day"],
                        "وقت البصمة": d["punch_time"].strftime("%H:%M:%S"),
                        "الموعد المطلوب": required_time.strftime("%H:%M"),
                        "التأخير": d["delay"],
                        "الخصم": f"{day_rate/2:.1f} جنيه"
                    })
                df_h = pd.DataFrame(h_data)
                st.dataframe(df_h, use_container_width=True, hide_index=True)

            # ── On-time days ──
            if results["on_time_days"]:
                with st.expander(f"✅ أيام الحضور بالموعد أو قبله ({len(results['on_time_days'])} يوم)"):
                    on_data = []
                    for i, d in enumerate(results["on_time_days"], 1):
                        on_data.append({
                            "#": i,
                            "التاريخ": d["date"].strftime("%d/%m/%Y"),
                            "اليوم": d["day"],
                            "وقت البصمة": d["punch_time"].strftime("%H:%M:%S")
                        })
                    st.dataframe(pd.DataFrame(on_data), use_container_width=True, hide_index=True)

            # ── Export ──
            st.markdown('<div class="section-header">📥 تصدير التقرير</div>', unsafe_allow_html=True)

            export_data = {
                "البيان": ["الراتب الأساسي", "خصم الغياب", "خصم ربع يوم", "خصم نصف يوم",
                           "خصومات إضافية", "حوافز وإضافات", "إجمالي الخصومات", "الراتب المستحق"],
                "القيمة (جنيه)": [salary, -absent_deduction, -quarter_deduction, -half_deduction,
                                   -extra_deductions, incentives, -total_deductions, net_salary]
            }
            df_export = pd.DataFrame(export_data)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_export.to_excel(writer, sheet_name="ملخص الراتب", index=False)
                if results["absent_days"]:
                    pd.DataFrame([{
                        "التاريخ": d["date"].strftime("%d/%m/%Y"),
                        "اليوم": d["day"],
                        "الخصم": day_rate
                    } for d in results["absent_days"]]).to_excel(writer, sheet_name="الغياب", index=False)
                if results["quarter_deductions"]:
                    pd.DataFrame([{
                        "التاريخ": d["date"].strftime("%d/%m/%Y"),
                        "اليوم": d["day"],
                        "وقت البصمة": d["punch_time"].strftime("%H:%M:%S"),
                        "التأخير": d["delay"],
                        "الخصم": day_rate / 4
                    } for d in results["quarter_deductions"]]).to_excel(writer, sheet_name="ربع يوم", index=False)
                if results["half_deductions"]:
                    pd.DataFrame([{
                        "التاريخ": d["date"].strftime("%d/%m/%Y"),
                        "اليوم": d["day"],
                        "وقت البصمة": d["punch_time"].strftime("%H:%M:%S"),
                        "التأخير": d["delay"],
                        "الخصم": day_rate / 2
                    } for d in results["half_deductions"]]).to_excel(writer, sheet_name="نصف يوم", index=False)

            st.download_button(
                label="📥 تحميل التقرير (Excel)",
                data=buffer.getvalue(),
                file_name=f"تقرير_حضور_{emp_name}_{start_date}_{end_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ خطأ في معالجة الملف: {str(e)}")
        st.exception(e)
