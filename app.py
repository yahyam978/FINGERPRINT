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
        border: 1px solid #e94560; border-radius: 16px; padding: 30px;
        text-align: center; margin-bottom: 25px; box-shadow: 0 8px 32px rgba(233,69,96,0.3);
    }
    .main-header h1 { color: #ffffff; font-size: 2.2rem; font-weight: 700; margin: 0; text-shadow: 0 0 20px rgba(233,69,96,0.5); }
    .main-header p { color: #a0aec0; margin: 8px 0 0 0; font-size: 1rem; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 20px;
        text-align: center; border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3); margin-bottom: 10px;
    }
    .metric-value { font-size: 2.5rem; font-weight: 700; margin: 5px 0; }
    .metric-label { color: #a0aec0; font-size: 0.9rem; font-weight: 600; }
    .red-val { color: #fc5c7d; } .yellow-val { color: #f7971e; }
    .orange-val { color: #fd7238; } .green-val { color: #11998e; }
    .blue-val { color: #4facfe; } .purple-val { color: #c471ed; }
    .teal-val { color: #38ef7d; }
    .salary-box {
        background: linear-gradient(135deg, #11998e, #38ef7d); border-radius: 16px;
        padding: 30px; text-align: center; margin: 20px 0; box-shadow: 0 8px 32px rgba(17,153,142,0.4);
    }
    .salary-box .amount { font-size: 3rem; font-weight: 700; color: white; text-shadow: 0 2px 10px rgba(0,0,0,0.3); }
    .salary-box .label { color: rgba(255,255,255,0.9); font-size: 1.1rem; font-weight: 600; }
    .section-header {
        background: linear-gradient(90deg, #0f3460, #1a1a2e); border-right: 4px solid #e94560;
        border-radius: 8px; padding: 12px 18px; margin: 20px 0 12px 0;
        color: white; font-weight: 700; font-size: 1.1rem; direction: rtl;
    }
    .excuse-header {
        background: linear-gradient(90deg, #0f3460, #1a1a2e); border-right: 4px solid #38ef7d;
        border-radius: 8px; padding: 12px 18px; margin: 20px 0 12px 0;
        color: white; font-weight: 700; font-size: 1.1rem; direction: rtl;
    }
    div[data-testid="stSidebar"] { background: #0f2027 !important; }
    .stButton > button {
        background: linear-gradient(90deg, #e94560, #0f3460) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        font-family: 'Cairo', sans-serif !important; font-weight: 600 !important;
        padding: 12px 30px !important; width: 100% !important; font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(233,69,96,0.3) !important;
    }
    .recalc-btn > button {
        background: linear-gradient(90deg, #11998e, #38ef7d) !important;
        box-shadow: 0 4px 15px rgba(17,153,142,0.4) !important;
    }
    label { color: #a0aec0 !important; font-weight: 600 !important; direction: rtl !important; }
    .stTextInput input, .stNumberInput input {
        background: #1a1a2e !important; color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 8px !important; direction: rtl !important;
    }
    .stMultiSelect > div { direction: rtl !important; }
    .excuse-box {
        background: rgba(56,239,125,0.08); border: 1px solid rgba(56,239,125,0.3);
        border-radius: 10px; padding: 14px 18px; margin: 4px 0; direction: rtl;
        display: flex; align-items: center; gap: 10px;
    }
    .excuse-date { color: #38ef7d; font-weight: 700; font-size: 1rem; min-width: 120px; }
    .excuse-type { color: #f7971e; font-size: 0.85rem; }
    .excuse-reason { color: #a0aec0; font-size: 0.85rem; font-style: italic; }
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
        s = ''.join(c for c in str(val).strip() if c.isdigit() or c in '/:- ')
        try:
            return datetime.strptime(s.strip()[:19], "%d/%m/%Y %H:%M:%S")
        except:
            return None

    df["ParsedDT"] = df["DateTime"].apply(clean_dt)
    df = df[df["ParsedDT"].notna()]
    df["Date"] = df["ParsedDT"].dt.date
    df["Time"] = df["ParsedDT"].dt.time
    return df


def analyze_attendance(df_parsed, start_date, end_date, required_time, off_days, salary, excused_keys=None):
    """
    excused_keys: set of strings like "2026-06-01|absent" or "2026-06-03|quarter"
    """
    if excused_keys is None:
        excused_keys = set()

    results = {"absent_days": [], "quarter_deductions": [], "half_deductions": [], "on_time_days": []}
    required_dt = datetime.combine(date.today(), required_time)
    quarter_limit = (required_dt + timedelta(minutes=15)).time()
    half_limit = (required_dt + timedelta(minutes=30)).time()

    current = start_date
    while current <= end_date:
        day_name = DAYS_AR[current.weekday()]
        if day_name in off_days:
            current += timedelta(days=1)
            continue

        day_records = df_parsed[df_parsed["Date"] == current]

        if day_records.empty:
            key = f"{current}|absent"
            results["absent_days"].append({
                "date": current, "day": day_name,
                "reason": "غياب كامل - لا توجد بصمة",
                "excused": key in excused_keys, "key": key
            })
        else:
            first_punch = day_records["ParsedDT"].min().time()
            if first_punch >= half_limit:
                key = f"{current}|half"
                results["half_deductions"].append({
                    "date": current, "day": day_name, "punch_time": first_punch,
                    "delay": f"تأخر {_diff_min(required_time, first_punch)} دقيقة",
                    "excused": key in excused_keys, "key": key
                })
            elif first_punch >= quarter_limit:
                key = f"{current}|quarter"
                results["quarter_deductions"].append({
                    "date": current, "day": day_name, "punch_time": first_punch,
                    "delay": f"تأخر {_diff_min(required_time, first_punch)} دقيقة",
                    "excused": key in excused_keys, "key": key
                })
            else:
                results["on_time_days"].append({"date": current, "day": day_name, "punch_time": first_punch})

        current += timedelta(days=1)

    day_rate = salary / 30
    absent_count = sum(1 for d in results["absent_days"] if not d["excused"])
    quarter_count = sum(1 for d in results["quarter_deductions"] if not d["excused"])
    half_count = sum(1 for d in results["half_deductions"] if not d["excused"])

    absent_deduction = absent_count * day_rate
    quarter_deduction = quarter_count * (day_rate / 4)
    half_deduction = half_count * (day_rate / 2)
    total_auto = absent_deduction + quarter_deduction + half_deduction

    return results, day_rate, absent_deduction, quarter_deduction, half_deduction, total_auto


def _diff_min(t1, t2):
    dt1 = datetime.combine(date.today(), t1)
    dt2 = datetime.combine(date.today(), t2)
    return (dt2 - dt1).seconds // 60


# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "excused_keys" not in st.session_state:
    st.session_state.excused_keys = set()
if "excused_reasons" not in st.session_state:
    st.session_state.excused_reasons = {}
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "df_parsed" not in st.session_state:
    st.session_state.df_parsed = None
if "params" not in st.session_state:
    st.session_state.params = {}

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🕐 نظام تحليل الحضور والانصراف</h1>
    <p>تحليل شامل للحضور والتأخير واحتساب الخصومات والراتب المستحق</p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📁 رفع ملف الحضور")
    uploaded = st.file_uploader("اختر ملف الحضور (.xls / .xlsx)", type=["xls", "xlsx"])

    st.markdown("---")
    st.markdown("### ⚙️ إعدادات الموظف")
    required_hour = st.number_input("ساعة الحضور المطلوبة", 0, 23, 7)
    required_minute = st.number_input("الدقيقة", 0, 59, 0)
    required_time = time(required_hour, required_minute)
    st.caption(f"⏰ موعد الحضور: {required_time.strftime('%H:%M')}")

    st.markdown("---")
    off_days_selected = st.multiselect("أيام الإجازة الأسبوعية", options=DAYS_EN, default=["الجمعة", "السبت"])

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
    extra_deductions = st.number_input("خصومات إضافية أخرى (جنيه)", min_value=0.0, value=0.0, step=50.0)
    incentives = st.number_input("حوافز وإضافات (جنيه)", min_value=0.0, value=0.0, step=50.0)
    extra_deductions_note = st.text_input("ملاحظة الخصومات الإضافية", placeholder="سبب الخصم...")
    incentives_note = st.text_input("ملاحظة الحوافز", placeholder="سبب الحافز...")

    st.markdown("---")
    if st.button("🔍 تحليل الحضور"):
        if uploaded:
            try:
                engine = "xlrd" if uploaded.name.endswith(".xls") else "openpyxl"
                df_raw = pd.read_excel(uploaded, header=None, engine=engine)
                df_parsed = parse_attendance(df_raw)
                st.session_state.df_parsed = df_parsed
                st.session_state.excused_keys = set()
                st.session_state.excused_reasons = {}
                st.session_state.analysis_done = True
                st.session_state.params = {
                    "required_time": required_time,
                    "off_days": off_days_selected,
                    "start_date": start_date,
                    "end_date": end_date,
                    "salary": salary,
                }
            except Exception as e:
                st.error(f"❌ خطأ: {e}")
        else:
            st.warning("يرجى رفع ملف الحضور أولاً")


# ─── MAIN CONTENT ──────────────────────────────────────────────────────────────
if not uploaded and not st.session_state.analysis_done:
    st.info("👈 يرجى رفع ملف الحضور من الشريط الجانبي للبدء")
    st.markdown("""
    <div style='background:#1a1a2e;border-radius:12px;padding:25px;border:1px solid rgba(255,255,255,0.1);direction:rtl;margin-top:20px;'>
        <h3 style='color:#4facfe;margin-top:0;'>📌 كيفية استخدام النظام</h3>
        <ol style='color:#a0aec0;line-height:2.5;'>
            <li>ارفع ملف الحضور (XLS/XLSX) من الشريط الجانبي</li>
            <li>حدد موعد الحضور وأيام الإجازة والفترة الزمنية والراتب</li>
            <li>اضغط "تحليل الحضور" لعرض المخالفات</li>
            <li><strong style='color:#38ef7d;'>✨ جديد:</strong> اختر الأيام التي لها عذر وأدخل السبب — سيُعاد الحساب تلقائياً</li>
            <li>راجع النتائج النهائية وحمّل التقرير</li>
        </ol>
        <hr style='border-color:rgba(255,255,255,0.1);'/>
        <h4 style='color:#f7971e;'>📐 قواعد الحساب</h4>
        <ul style='color:#a0aec0;line-height:2.2;'>
            <li>🔴 غياب كامل → خصم يوم كامل</li>
            <li>🟡 تأخر 15–29 دقيقة → خصم ربع يوم</li>
            <li>🟠 تأخر 30 دقيقة أو أكثر → خصم نصف يوم</li>
            <li>✅ عذر مقبول → لا خصم</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.analysis_done and st.session_state.df_parsed is not None:
    p = st.session_state.params
    req_time = p.get("required_time", required_time)
    off_days = p.get("off_days", off_days_selected)
    s_date = p.get("start_date", start_date)
    e_date = p.get("end_date", end_date)
    sal = p.get("salary", salary)

    df_range = st.session_state.df_parsed[
        (st.session_state.df_parsed["Date"] >= s_date) &
        (st.session_state.df_parsed["Date"] <= e_date)
    ]
    emp_name = st.session_state.df_parsed["Name"].iloc[0]

    results, day_rate, absent_deduction, quarter_deduction, half_deduction, total_auto = analyze_attendance(
        df_range, s_date, e_date, req_time, off_days, sal, st.session_state.excused_keys
    )

    all_violations = (
        [("absent", d) for d in results["absent_days"]] +
        [("quarter", d) for d in results["quarter_deductions"]] +
        [("half", d) for d in results["half_deductions"]]
    )
    all_violations.sort(key=lambda x: x[1]["date"])

    # ── Excuse section ──────────────────────────────────────────────────────────
    if all_violations:
        st.markdown('<div class="excuse-header">✅ إدارة الأعذار — اختر الأيام المعفوة</div>', unsafe_allow_html=True)

        st.markdown("""
        <p style='color:#a0aec0;direction:rtl;margin-bottom:15px;'>
        ✏️ ضع علامة ✔ على أي يوم لديه عذر مقبول وأدخل السبب — سيُستبعد تلقائياً من حساب الخصومات.
        </p>
        """, unsafe_allow_html=True)

        TYPE_LABEL = {"absent": ("🔴 غياب", "#fc5c7d"), "quarter": ("🟡 تأخر ربع يوم", "#f7971e"), "half": ("🟠 تأخر نصف يوم", "#fd7238")}

        for vtype, d in all_violations:
            key = d["key"]
            label_text, label_color = TYPE_LABEL[vtype]
            date_str = d["date"].strftime("%d/%m/%Y")
            day_str = d["day"]
            extra = f" — بصمة: {d['punch_time'].strftime('%H:%M')} ({d['delay']})" if vtype != "absent" else ""

            col_chk, col_info, col_reason = st.columns([1, 3, 4])
            with col_chk:
                checked = st.checkbox("عذر", value=(key in st.session_state.excused_keys),
                                      key=f"chk_{key}", label_visibility="collapsed")
            with col_info:
                st.markdown(f"""
                <div style='padding:8px 0;direction:rtl;'>
                    <span style='color:{label_color};font-weight:700;'>{label_text}</span>
                    <span style='color:white;font-weight:600;'> — {date_str} ({day_str})</span>
                    <span style='color:#a0aec0;font-size:0.85rem;'>{extra}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_reason:
                if checked:
                    reason = st.text_input("سبب العذر", value=st.session_state.excused_reasons.get(key, ""),
                                           key=f"reason_{key}", placeholder="مثال: إجازة مرضية، أمر طارئ...",
                                           label_visibility="collapsed")
                    st.session_state.excused_reasons[key] = reason
                else:
                    st.markdown("<div style='height:38px;'></div>", unsafe_allow_html=True)

            # Update excused set
            if checked:
                st.session_state.excused_keys.add(key)
            else:
                st.session_state.excused_keys.discard(key)

        # Re-run analysis with updated excuses
        results, day_rate, absent_deduction, quarter_deduction, half_deduction, total_auto = analyze_attendance(
            df_range, s_date, e_date, req_time, off_days, sal, st.session_state.excused_keys
        )

        # Show excused summary
        excused_count = len(st.session_state.excused_keys)
        if excused_count > 0:
            st.markdown(f"""
            <div style='background:rgba(56,239,125,0.1);border:1px solid rgba(56,239,125,0.4);border-radius:10px;
                        padding:14px 18px;margin:10px 0;direction:rtl;'>
                <span style='color:#38ef7d;font-weight:700;font-size:1rem;'>
                    ✅ تم التغاضي عن {excused_count} {"يوم/تأخير" if excused_count == 1 else "أيام/تأخيرات"} بعذر مقبول
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

    # ── Metrics ────────────────────────────────────────────────────────────────
    eff_absent = sum(1 for d in results["absent_days"] if not d["excused"])
    eff_quarter = sum(1 for d in results["quarter_deductions"] if not d["excused"])
    eff_half = sum(1 for d in results["half_deductions"] if not d["excused"])
    excused_total = len(st.session_state.excused_keys)

    st.markdown(f"""
    <div class="section-header">
        👤 تقرير الموظف: {emp_name} &nbsp;|&nbsp;
        📅 {s_date.strftime('%d/%m/%Y')} – {e_date.strftime('%d/%m/%Y')}
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, val, lbl, sub, cls in [
        (c1, eff_absent, "أيام الغياب", "يوم", "red-val"),
        (c2, eff_quarter, "ربع يوم خصم", "مرة", "yellow-val"),
        (c3, eff_half, "نصف يوم خصم", "مرة", "orange-val"),
        (c4, excused_total, "أيام بعذر", "معفي", "teal-val"),
        (c5, f"{day_rate:.0f}", "سعر اليوم", "جنيه", "blue-val"),
        (c6, len(results["on_time_days"]), "حضور بالموعد", "يوم", "green-val"),
    ]:
        with col:
            col.markdown(f"""<div class="metric-card">
                <div class="metric-label">{lbl}</div>
                <div class="metric-value {cls}">{val}</div>
                <div class="metric-label">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # ── Salary breakdown ────────────────────────────────────────────────────────
    total_deductions = total_auto + extra_deductions
    net_salary = sal + incentives - total_deductions

    st.markdown('<div class="section-header">💰 تفصيل الراتب</div>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1:
        excuse_line = f"<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'><span style='color:#38ef7d;'>أيام/تأخيرات معفوة بعذر</span><span style='color:#38ef7d;font-weight:600;'>✅ {excused_total} بند</span></div>" if excused_total > 0 else ""
        st.markdown(f"""
        <div style='background:#1a1a2e;border-radius:12px;padding:20px;border:1px solid rgba(255,255,255,0.1);direction:rtl;'>
            <h4 style='color:#4facfe;margin-top:0;'>📊 تفاصيل الخصومات</h4>
            <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                <span style='color:#a0aec0;'>الراتب الأساسي</span>
                <span style='color:white;font-weight:600;'>{sal:,.1f} جنيه</span>
            </div>
            {excuse_line}
            <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                <span style='color:#a0aec0;'>خصم الغياب ({eff_absent} × {day_rate:.1f})</span>
                <span style='color:#fc5c7d;font-weight:600;'>- {absent_deduction:,.1f} جنيه</span>
            </div>
            <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                <span style='color:#a0aec0;'>خصم ربع يوم ({eff_quarter} × {day_rate/4:.1f})</span>
                <span style='color:#f7971e;font-weight:600;'>- {quarter_deduction:,.1f} جنيه</span>
            </div>
            <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                <span style='color:#a0aec0;'>خصم نصف يوم ({eff_half} × {day_rate/2:.1f})</span>
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

    # ── Excused days detail ─────────────────────────────────────────────────────
    if st.session_state.excused_keys:
        with st.expander(f"✅ تفاصيل الأيام المعفوة بعذر ({excused_total} بند)"):
            for vtype, d in all_violations:
                if d["key"] in st.session_state.excused_keys:
                    reason = st.session_state.excused_reasons.get(d["key"], "—")
                    label_text, label_color = {"absent": ("غياب", "#fc5c7d"), "quarter": ("تأخر ربع يوم", "#f7971e"), "half": ("تأخر نصف يوم", "#fd7238")}[vtype]
                    st.markdown(f"""
                    <div class="excuse-box">
                        <span class="excuse-date">{d['date'].strftime('%d/%m/%Y')} ({d['day']})</span>
                        <span style='color:{label_color};font-weight:600;font-size:0.85rem;'>{label_text}</span>
                        <span style='color:#a0aec0;font-size:0.85rem;'>السبب: {reason if reason else "لم يُذكر"}</span>
                    </div>
                    """, unsafe_allow_html=True)

    # ── Detail tables ───────────────────────────────────────────────────────────
    active_absent = [d for d in results["absent_days"] if not d["excused"]]
    active_quarter = [d for d in results["quarter_deductions"] if not d["excused"]]
    active_half = [d for d in results["half_deductions"] if not d["excused"]]

    if active_absent:
        st.markdown('<div class="section-header">🔴 تفاصيل أيام الغياب (المحتسبة)</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([{
            "#": i+1, "التاريخ": d["date"].strftime("%d/%m/%Y"), "اليوم": d["day"],
            "السبب": d["reason"], "الخصم": f"{day_rate:.1f} جنيه"
        } for i, d in enumerate(active_absent)]), use_container_width=True, hide_index=True)

    if active_quarter:
        st.markdown('<div class="section-header">🟡 تفاصيل خصم ربع اليوم (المحتسبة)</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([{
            "#": i+1, "التاريخ": d["date"].strftime("%d/%m/%Y"), "اليوم": d["day"],
            "وقت البصمة": d["punch_time"].strftime("%H:%M:%S"),
            "الموعد المطلوب": req_time.strftime("%H:%M"),
            "التأخير": d["delay"], "الخصم": f"{day_rate/4:.1f} جنيه"
        } for i, d in enumerate(active_quarter)]), use_container_width=True, hide_index=True)

    if active_half:
        st.markdown('<div class="section-header">🟠 تفاصيل خصم نصف اليوم (المحتسبة)</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([{
            "#": i+1, "التاريخ": d["date"].strftime("%d/%m/%Y"), "اليوم": d["day"],
            "وقت البصمة": d["punch_time"].strftime("%H:%M:%S"),
            "الموعد المطلوب": req_time.strftime("%H:%M"),
            "التأخير": d["delay"], "الخصم": f"{day_rate/2:.1f} جنيه"
        } for i, d in enumerate(active_half)]), use_container_width=True, hide_index=True)

    if results["on_time_days"]:
        with st.expander(f"✅ أيام الحضور بالموعد أو قبله ({len(results['on_time_days'])} يوم)"):
            st.dataframe(pd.DataFrame([{
                "#": i+1, "التاريخ": d["date"].strftime("%d/%m/%Y"),
                "اليوم": d["day"], "وقت البصمة": d["punch_time"].strftime("%H:%M:%S")
            } for i, d in enumerate(results["on_time_days"])]), use_container_width=True, hide_index=True)

    # ── Export ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📥 تصدير التقرير</div>', unsafe_allow_html=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({
            "البيان": ["الراتب الأساسي", "خصم الغياب", "خصم ربع يوم", "خصم نصف يوم",
                       "أيام/تأخيرات معفوة", "خصومات إضافية", "حوافز وإضافات",
                       "إجمالي الخصومات", "الراتب المستحق"],
            "القيمة (جنيه)": [sal, -absent_deduction, -quarter_deduction, -half_deduction,
                               0, -extra_deductions, incentives, -total_deductions, net_salary],
            "ملاحظة": ["", "", "", "", f"{excused_total} بند معفي بعذر",
                        extra_deductions_note, incentives_note, "", ""]
        }).to_excel(writer, sheet_name="ملخص الراتب", index=False)

        if st.session_state.excused_keys:
            excused_rows = []
            for vtype, d in all_violations:
                if d["key"] in st.session_state.excused_keys:
                    lbl = {"absent": "غياب", "quarter": "تأخر ربع يوم", "half": "تأخر نصف يوم"}[vtype]
                    excused_rows.append({
                        "التاريخ": d["date"].strftime("%d/%m/%Y"), "اليوم": d["day"],
                        "نوع المخالفة": lbl,
                        "سبب العذر": st.session_state.excused_reasons.get(d["key"], "—")
                    })
            pd.DataFrame(excused_rows).to_excel(writer, sheet_name="الأيام المعفوة", index=False)

        if active_absent:
            pd.DataFrame([{"التاريخ": d["date"].strftime("%d/%m/%Y"), "اليوم": d["day"],
                           "الخصم": day_rate} for d in active_absent]).to_excel(writer, sheet_name="الغياب", index=False)
        if active_quarter:
            pd.DataFrame([{"التاريخ": d["date"].strftime("%d/%m/%Y"), "اليوم": d["day"],
                           "وقت البصمة": d["punch_time"].strftime("%H:%M:%S"),
                           "التأخير": d["delay"], "الخصم": day_rate/4} for d in active_quarter]).to_excel(writer, sheet_name="ربع يوم", index=False)
        if active_half:
            pd.DataFrame([{"التاريخ": d["date"].strftime("%d/%m/%Y"), "اليوم": d["day"],
                           "وقت البصمة": d["punch_time"].strftime("%H:%M:%S"),
                           "التأخير": d["delay"], "الخصم": day_rate/2} for d in active_half]).to_excel(writer, sheet_name="نصف يوم", index=False)

    st.download_button(
        label="📥 تحميل التقرير الكامل (Excel)",
        data=buffer.getvalue(),
        file_name=f"تقرير_حضور_{emp_name}_{s_date}_{e_date}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
