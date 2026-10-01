
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# Page setup
# =========================================================
st.set_page_config(
    page_title="Tourism South Decision Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CSS: dashboard anatomy style
# =========================================================
st.markdown(
    """
<style>
:root {
    --navy: #08285a;
    --blue: #1e7be8;
    --light-blue: #edf6ff;
    --pale-yellow: #fff4d8;
    --pale-green: #edf8ef;
    --pale-purple: #f3f0ff;
    --text: #0b1f3a;
    --muted: #65758b;
    --border: #d7e0ee;
}

.main {
    background: linear-gradient(180deg, #f7fbff 0%, #ffffff 55%);
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
}

.app-title {
    font-size: 2.2rem;
    font-weight: 900;
    color: var(--navy);
    margin: 0;
    line-height: 1.1;
}

.app-subtitle {
    color: var(--muted);
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.stage-row {
    display: flex;
    gap: 0.35rem;
    align-items: center;
    margin: 1rem 0 1.1rem 0;
    flex-wrap: wrap;
}

.stage {
    padding: 0.48rem 1rem;
    border-radius: 999px;
    background: #e8edf6;
    color: #253858;
    font-weight: 700;
    font-size: 0.88rem;
}

.stage.active {
    background: var(--navy);
    color: white;
    box-shadow: 0 5px 15px rgba(8, 40, 90, 0.22);
}

.section-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem 1.1rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px rgba(15, 43, 80, 0.07);
}

.question-card {
    background: linear-gradient(90deg, #eef6ff 0%, #ffffff 100%);
    border-left: 6px solid var(--blue);
}

.insight-card {
    background: linear-gradient(90deg, #fff4d8 0%, #fffaf0 100%);
    border-left: 6px solid #f6b21a;
}

.recommend-card {
    background: linear-gradient(90deg, #eefaf0 0%, #ffffff 100%);
    border-left: 6px solid #2fb160;
}

.action-card {
    background: linear-gradient(90deg, #f2efff 0%, #ffffff 100%);
    border-left: 6px solid #6955d9;
}

.section-label {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    font-size: 1.25rem;
    font-weight: 900;
    color: var(--navy);
    margin-bottom: 0.4rem;
}

.bubble {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    color: white;
    background: var(--navy);
    display: inline-flex;
    justify-content: center;
    align-items: center;
    font-weight: 900;
}

.kpi-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem;
    box-shadow: 0 8px 24px rgba(15, 43, 80, 0.07);
    min-height: 118px;
}

.kpi-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--muted);
    margin-bottom: 0.3rem;
}

.kpi-value {
    font-size: 1.55rem;
    font-weight: 900;
    color: var(--navy);
    margin-bottom: 0.2rem;
}

.kpi-delta-positive {
    color: #178348;
    font-weight: 800;
}

.kpi-delta-negative {
    color: #c0392b;
    font-weight: 800;
}

.small-note {
    color: var(--muted);
    font-size: 0.88rem;
}

.badge {
    display: inline-block;
    border-radius: 999px;
    padding: 0.22rem 0.6rem;
    background: #eef4ff;
    color: var(--navy);
    font-weight: 700;
    margin-right: 0.3rem;
    margin-bottom: 0.3rem;
    font-size: 0.85rem;
}

hr {
    margin-top: 0.7rem;
    margin-bottom: 0.7rem;
}

[data-testid="stMetric"] {
    background: white;
    border-radius: 14px;
    padding: 0.65rem;
    border: 1px solid var(--border);
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# Data helpers
# =========================================================
DEFAULT_CSV_NAMES = [
    "tourismSouthCSV.csv",
    "tourismSouth.csv",
    "Internal_tourism_in_South.csv",
]


def _clean_number(value):
    """Convert values such as '1,234', '+ 2.26', '- 1.52' to float."""
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if text == "":
        return pd.NA
    text = text.replace(",", "")
    text = text.replace("+", "")
    text = text.replace(" ", "")
    try:
        return float(text)
    except ValueError:
        return pd.NA


def _pct_change(new_value, old_value):
    try:
        if pd.isna(new_value) or pd.isna(old_value) or float(old_value) == 0:
            return pd.NA
        return ((float(new_value) - float(old_value)) / float(old_value)) * 100
    except Exception:
        return pd.NA


def _find_default_csv():
    here = Path(__file__).resolve().parent
    candidates = [here / name for name in DEFAULT_CSV_NAMES]
    candidates += [Path.cwd() / name for name in DEFAULT_CSV_NAMES]
    # Sandbox fallback, useful while developing in ChatGPT
    candidates += [Path("/mnt/data") / name for name in DEFAULT_CSV_NAMES]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _get(raw, row, col):
    if col >= raw.shape[1]:
        return pd.NA
    return _clean_number(raw.iloc[row, col])


@st.cache_data(show_spinner=False)
def load_tourism_data_from_csv(path_or_buffer):
    raw = pd.read_csv(path_or_buffer, header=None)
    data_rows = raw.iloc[4:].copy()
    data_rows = data_rows[data_rows[1].notna()]
    data_rows = data_rows[data_rows[1].astype(str).str.strip() != ""]

    records = []
    for ridx in data_rows.index:
        province = str(raw.iloc[ridx, 1]).strip()

        visitor_thai_2025 = _get(raw, ridx, 2)
        visitor_thai_2024 = _get(raw, ridx, 3)
        visitor_foreign_2025 = _get(raw, ridx, 5)
        visitor_foreign_2024 = _get(raw, ridx, 6)

        tourist_thai_2025 = _get(raw, ridx, 8)
        tourist_thai_2024 = _get(raw, ridx, 9)
        tourist_foreign_2025 = _get(raw, ridx, 11)
        tourist_foreign_2024 = _get(raw, ridx, 12)

        excursionist_thai_2025 = _get(raw, ridx, 14)
        excursionist_thai_2024 = _get(raw, ridx, 15)
        excursionist_foreign_2025 = _get(raw, ridx, 17)
        excursionist_foreign_2024 = _get(raw, ridx, 18)

        visitor_2025 = visitor_thai_2025 + visitor_foreign_2025
        visitor_2024 = visitor_thai_2024 + visitor_foreign_2024
        tourist_2025 = tourist_thai_2025 + tourist_foreign_2025
        tourist_2024 = tourist_thai_2024 + tourist_foreign_2024
        excursionist_2025 = excursionist_thai_2025 + excursionist_foreign_2025
        excursionist_2024 = excursionist_thai_2024 + excursionist_foreign_2024

        record = {
            "Province": province,
            "Visitor_2025": visitor_2025,
            "Visitor_2024": visitor_2024,
            "Visitor_%Change": _pct_change(visitor_2025, visitor_2024),
            "Thai_Visitor_2025": visitor_thai_2025,
            "Foreign_Visitor_2025": visitor_foreign_2025,
            "Tourist_2025": tourist_2025,
            "Tourist_2024": tourist_2024,
            "Tourist_%Change": _pct_change(tourist_2025, tourist_2024),
            "Excursionist_2025": excursionist_2025,
            "Excursionist_2024": excursionist_2024,
            "Excursionist_%Change": _pct_change(excursionist_2025, excursionist_2024),
            "Avg_Stay_Thai_2025": _get(raw, ridx, 20),
            "Avg_Stay_Foreign_2025": _get(raw, ridx, 23),
            "Avg_Expenditure_Visitor_2025": _get(raw, ridx, 26),
            "Avg_Expenditure_Visitor_2024": _get(raw, ridx, 27),
            "Avg_Expenditure_Visitor_%Change": _get(raw, ridx, 28),
            "Revenue_2025": _get(raw, ridx, 53),
            "Revenue_2024": _get(raw, ridx, 54),
            "Revenue_%Change": _get(raw, ridx, 55),
            "Thai_Revenue_2025": _get(raw, ridx, 56),
            "Foreign_Revenue_2025": _get(raw, ridx, 59),
            "Rooms_2025": _get(raw, ridx, 62),
            "Rooms_2024": _get(raw, ridx, 63),
            "Rooms_%Change": _get(raw, ridx, 64),
            "Occupancy_2025": _get(raw, ridx, 65),
            "Occupancy_2024": _get(raw, ridx, 66),
            "Occupancy_Change": _get(raw, ridx, 67),
            "Guest_Arrivals_2025": _get(raw, ridx, 68),
            "Guest_Arrivals_2024": _get(raw, ridx, 69),
            "Guest_Arrivals_%Change": _get(raw, ridx, 70),
        }
        records.append(record)

    df = pd.DataFrame(records)
    for col in df.columns:
        if col != "Province":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Province-level data excludes the overall South row.
    province_df = df[df["Province"] != "ภาคใต้"].copy()
    south_df = df[df["Province"] == "ภาคใต้"].copy()

    # Derived decision metrics
    province_df["Revenue_per_Visitor_2025"] = (
        province_df["Revenue_2025"] * 1_000_000 / province_df["Visitor_2025"]
    )
    province_df["Visitor_Rank"] = province_df["Visitor_2025"].rank(ascending=False, method="min")
    province_df["Revenue_Rank"] = province_df["Revenue_2025"].rank(ascending=False, method="min")
    province_df["Growth_Rank"] = province_df["Revenue_%Change"].rank(ascending=False, method="min")
    province_df["Occupancy_Rank"] = province_df["Occupancy_2025"].rank(ascending=False, method="min")

    revenue_q75 = province_df["Revenue_2025"].quantile(0.75)
    growth_q75 = province_df["Revenue_%Change"].quantile(0.75)
    occupancy_q25 = province_df["Occupancy_2025"].quantile(0.25)
    visitor_median = province_df["Visitor_2025"].median()
    yield_median = province_df["Revenue_per_Visitor_2025"].median()

    def classify(row):
        if row["Revenue_2025"] >= revenue_q75:
            return "Revenue leader"
        if row["Revenue_%Change"] >= growth_q75:
            return "Growth opportunity"
        if row["Occupancy_2025"] <= occupancy_q25 or row["Occupancy_Change"] < 0:
            return "Need attention"
        if row["Visitor_2025"] >= visitor_median and row["Revenue_per_Visitor_2025"] < yield_median:
            return "High visitor, low yield"
        return "Stable / monitor"

    province_df["Segment"] = province_df.apply(classify, axis=1)

    return df, province_df, south_df


def fmt_number(value, digits=0):
    if pd.isna(value):
        return "-"
    return f"{value:,.{digits}f}"


def fmt_million(value):
    if pd.isna(value):
        return "-"
    return f"{value:,.2f} ลบ."


def fmt_pct(value, digits=2):
    if pd.isna(value):
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{digits}f}%"


def kpi_card(title, value, delta=None, note=None):
    delta_class = "kpi-delta-positive"
    if delta is not None and str(delta).strip().startswith("-"):
        delta_class = "kpi-delta-negative"
    delta_html = f'<div class="{delta_class}">{delta}</div>' if delta is not None else ""
    note_html = f'<div class="small-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# Sidebar and load data
# =========================================================
with st.sidebar:
    st.markdown("### ⚙️ Data source")
    uploaded = st.file_uploader("Upload tourismSouthCSV.csv", type=["csv"])
    default_path = _find_default_csv()

    if uploaded is not None:
        data_source = uploaded
        st.success("ใช้ไฟล์ที่อัปโหลดแล้ว")
    elif default_path is not None:
        data_source = default_path
        st.info(f"ใช้ไฟล์: {default_path.name}")
    else:
        data_source = None
        st.error("ไม่พบไฟล์ tourismSouthCSV.csv กรุณาอัปโหลดไฟล์ CSV")

if data_source is None:
    st.stop()

all_df, province_df, south_df = load_tourism_data_from_csv(data_source)

with st.sidebar:
    st.markdown("### 🔎 Filters")
    segment_filter = st.multiselect(
        "Province segment",
        options=province_df["Segment"].dropna().unique().tolist(),
        default=province_df["Segment"].dropna().unique().tolist(),
    )
    selected_provinces = st.multiselect(
        "Province",
        options=province_df["Province"].tolist(),
        default=province_df["Province"].tolist(),
    )

filtered_df = province_df[
    province_df["Segment"].isin(segment_filter) & province_df["Province"].isin(selected_provinces)
].copy()

# =========================================================
# Header: anatomy
# =========================================================
st.markdown('<div class="app-title">Internal Tourism in South Decision Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">January–December 2025 vs 2024 | Tourism revenue decision interface</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="stage-row">
  <span class="stage">Problem</span>
  <span class="stage">Question</span>
  <span class="stage">Data</span>
  <span class="stage">Analysis</span>
  <span class="stage">Evidence</span>
  <span class="stage">Insight</span>
  <span class="stage active">Decision</span>
  <span class="stage active">Action</span>
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# Decision question
# =========================================================
st.markdown(
    """
<div class="section-card question-card">
    <div class="section-label"><span class="bubble">?</span>Decision Question</div>
    <div style="font-size:1.05rem; color:#0b1f3a;">
    ควรให้ความสำคัญกับจังหวัดใด และควรสนับสนุนประเด็นใด
    เพื่อเพิ่มรายได้ทางการท่องเที่ยวของภาคใต้ ปี 2568 เมื่อเทียบกับปี 2567?
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# KPI row
# =========================================================
south = south_df.iloc[0] if not south_df.empty else all_df.iloc[0]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    kpi_card(
        "Visitor 2025",
        fmt_number(south["Visitor_2025"]),
        fmt_pct(south["Visitor_%Change"]),
        "ภาคใต้รวม",
    )
with kpi2:
    kpi_card(
        "Revenue 2025",
        fmt_million(south["Revenue_2025"]),
        fmt_pct(south["Revenue_%Change"]),
        "ล้านบาท",
    )
with kpi3:
    kpi_card(
        "Occupancy rate",
        fmt_pct(south["Occupancy_2025"]),
        fmt_pct(south["Occupancy_Change"]),
        "เปลี่ยนแปลงเทียบปี 2024",
    )
with kpi4:
    top_growth = province_df.sort_values("Revenue_%Change", ascending=False).iloc[0]
    kpi_card(
        "Top revenue growth",
        top_growth["Province"],
        fmt_pct(top_growth["Revenue_%Change"]),
        "จังหวัดที่รายได้โตสูงสุด",
    )

# =========================================================
# Evidence charts
# =========================================================
st.markdown(
    """
<div class="section-card">
    <div class="section-label"><span class="bubble">1</span>Evidence Charts</div>
    <div class="small-note">แสดงหลักฐานเชิงภาพไม่เกิน 4 ชิ้น เพื่อช่วยตอบคำถามเชิงตัดสินใจ</div>
</div>
""",
    unsafe_allow_html=True,
)

chart_left, chart_right = st.columns(2)

with chart_left:
    rev_data = filtered_df.sort_values("Revenue_2025", ascending=True)
    fig_rev = px.bar(
        rev_data,
        x="Revenue_2025",
        y="Province",
        orientation="h",
        title="Revenue 2025 by province",
        labels={"Revenue_2025": "Revenue 2025 (Million Baht)", "Province": "Province"},
        hover_data={
            "Revenue_2025": ":,.2f",
            "Revenue_%Change": ":.2f",
            "Visitor_2025": ":,.0f",
            "Occupancy_2025": ":.2f",
        },
    )
    fig_rev.update_layout(height=430, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig_rev, width="stretch")

with chart_right:
    growth_data = filtered_df.sort_values("Revenue_%Change", ascending=True)
    fig_growth = px.bar(
        growth_data,
        x="Revenue_%Change",
        y="Province",
        orientation="h",
        title="Revenue %Change by province",
        labels={"Revenue_%Change": "Revenue %Change", "Province": "Province"},
        hover_data={"Revenue_2025": ":,.2f", "Revenue_2024": ":,.2f"},
    )
    fig_growth.update_layout(height=430, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig_growth, width="stretch")

chart_left2, chart_right2 = st.columns(2)

with chart_left2:
    fig_scatter = px.scatter(
        filtered_df,
        x="Visitor_2025",
        y="Revenue_2025",
        size="Occupancy_2025",
        color="Segment",
        hover_name="Province",
        title="Visitor vs Revenue 2025",
        labels={
            "Visitor_2025": "Visitor 2025",
            "Revenue_2025": "Revenue 2025 (Million Baht)",
            "Occupancy_2025": "Occupancy rate",
        },
        hover_data={
            "Visitor_%Change": ":.2f",
            "Revenue_%Change": ":.2f",
            "Avg_Expenditure_Visitor_2025": ":,.2f",
        },
    )
    fig_scatter.update_layout(height=430, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig_scatter, width="stretch")

with chart_right2:
    occ_data = filtered_df.sort_values("Occupancy_2025", ascending=True)
    fig_occ = px.bar(
        occ_data,
        x="Occupancy_2025",
        y="Province",
        orientation="h",
        color="Segment",
        title="Occupancy rate 2025 by province",
        labels={"Occupancy_2025": "Occupancy rate (%)", "Province": "Province"},
        hover_data={"Occupancy_Change": ":.2f", "Guest_Arrivals_2025": ":,.0f"},
    )
    fig_occ.update_layout(height=430, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig_occ, width="stretch")

# =========================================================
# Insight headline
# =========================================================
top_revenue = province_df.sort_values("Revenue_2025", ascending=False).iloc[0]
top_growth = province_df.sort_values("Revenue_%Change", ascending=False).iloc[0]
declining_occ = province_df[province_df["Occupancy_Change"] < 0].sort_values("Occupancy_Change").head(3)

insight_text = (
    f"จังหวัดที่สร้างรายได้สูงสุดคือ {top_revenue['Province']} "
    f"({fmt_million(top_revenue['Revenue_2025'])}) "
    f"แต่จังหวัดที่รายได้เติบโตสูงสุดคือ {top_growth['Province']} "
    f"({fmt_pct(top_growth['Revenue_%Change'])}) "
    "จึงควรแยกกลยุทธ์ระหว่างจังหวัดรายได้หลักและจังหวัดที่มีศักยภาพเติบโต"
)

if not declining_occ.empty:
    occ_list = ", ".join(declining_occ["Province"].tolist())
    insight_text += f" ขณะเดียวกันจังหวัดที่ Occupancy ลดลง เช่น {occ_list} ควรได้รับการวิเคราะห์เพิ่มเติม"

st.markdown(
    f"""
<div class="section-card insight-card">
    <div class="section-label"><span class="bubble">2</span>Insight Headline</div>
    <div style="font-size:1.02rem; color:#0b1f3a;">{insight_text}</div>
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# Recommendation
# =========================================================
revenue_leaders = province_df[province_df["Segment"] == "Revenue leader"].sort_values("Revenue_2025", ascending=False)
growth_opps = province_df[province_df["Segment"] == "Growth opportunity"].sort_values("Revenue_%Change", ascending=False)
need_attention = province_df[province_df["Segment"] == "Need attention"].sort_values("Occupancy_Change")

st.markdown(
    """
<div class="section-card recommend-card">
    <div class="section-label"><span class="bubble">3</span>Recommendation</div>
    <div class="small-note">ข้อเสนอแนะตามกลุ่มจังหวัด เพื่อเชื่อมโยงหลักฐานกับการตัดสินใจ</div>
</div>
""",
    unsafe_allow_html=True,
)

rec1, rec2, rec3 = st.columns(3)
with rec1:
    st.markdown("#### Revenue leader")
    for p in revenue_leaders["Province"].head(4).tolist():
        st.markdown(f'<span class="badge">{p}</span>', unsafe_allow_html=True)
    st.write("รักษาคุณภาพตลาด เพิ่มมูลค่าต่อหัว และพัฒนา high-value tourism")

with rec2:
    st.markdown("#### Growth opportunity")
    for p in growth_opps["Province"].head(4).tolist():
        st.markdown(f'<span class="badge">{p}</span>', unsafe_allow_html=True)
    st.write("สนับสนุนแคมเปญ การตลาด และโครงสร้างพื้นฐานเพื่อเร่งการเติบโต")

with rec3:
    st.markdown("#### Need attention")
    for p in need_attention["Province"].head(4).tolist():
        st.markdown(f'<span class="badge">{p}</span>', unsafe_allow_html=True)
    st.write("วิเคราะห์ปัญหา Occupancy ฤดูกาล ช่องทางตลาด และศักยภาพที่พัก")

# =========================================================
# Action plan
# =========================================================
action_plan = pd.DataFrame(
    [
        {
            "Action": "เลือกจังหวัดเป้าหมาย 3–5 จังหวัดเพื่อทำ Dashboard รายจังหวัด",
            "Target Province Group": "Revenue leader / Growth opportunity",
            "KPI to Track": "Revenue, Visitor, Occupancy",
            "Next Step": "จัดทำ profile รายจังหวัดและดูข้อมูลรายเดือน",
        },
        {
            "Action": "วิเคราะห์จังหวัดที่ Visitor สูงแต่ Revenue yield ต่ำ",
            "Target Province Group": "High visitor, low yield",
            "KPI to Track": "Average expenditure, Revenue per visitor",
            "Next Step": "ออกแบบกิจกรรมเพิ่มค่าใช้จ่ายต่อทริป",
        },
        {
            "Action": "จัดทำแผนส่งเสริมการท่องเที่ยวเฉพาะกลุ่มจังหวัด",
            "Target Province Group": "Growth opportunity",
            "KPI to Track": "Revenue %Change, Visitor %Change",
            "Next Step": "กำหนด campaign และ partner รายพื้นที่",
        },
        { 
            "Action": "ติดตาม Occupancy และ Guest arrivals รายเดือน",
            "Target Province Group": "Need attention",
            "KPI to Track": "Occupancy rate, Guest arrivals",
            "Next Step": "ตรวจสอบฤดูกาลและปัญหา supply ที่พัก",
        },
    ]
)

st.markdown(
    """
<div class="section-card action-card">
    <div class="section-label"><span class="bubble">4</span>Action Plan</div>
</div>
""",
    unsafe_allow_html=True,
)
st.dataframe(action_plan, hide_index=True, width="stretch")

# =========================================================
# Data layer / Analysis summary layer
# =========================================================
with st.expander("ดู Analysis Summary Layer และ Data Layer"):
    summary_cols = [
        "Province",
        "Visitor_2025",
        "Visitor_2024",
        "Visitor_%Change",
        "Revenue_2025",
        "Revenue_2024",
        "Revenue_%Change",
        "Avg_Expenditure_Visitor_2025",
        "Occupancy_2025",
        "Occupancy_Change",
        "Guest_Arrivals_2025",
        "Guest_Arrivals_%Change",
        "Revenue_per_Visitor_2025",
        "Revenue_Rank",
        "Growth_Rank",
        "Visitor_Rank",
        "Occupancy_Rank",
        "Segment",
    ]
    st.dataframe(
        province_df[summary_cols].sort_values("Revenue_2025", ascending=False),
        hide_index=True,
        width="stretch",
        column_config={
            "Visitor_2025": st.column_config.NumberColumn(format="%.0f"),
            "Visitor_2024": st.column_config.NumberColumn(format="%.0f"),
            "Visitor_%Change": st.column_config.NumberColumn(format="%.2f%%"),
            "Revenue_2025": st.column_config.NumberColumn(format="%.2f"),
            "Revenue_2024": st.column_config.NumberColumn(format="%.2f"),
            "Revenue_%Change": st.column_config.NumberColumn(format="%.2f%%"),
            "Avg_Expenditure_Visitor_2025": st.column_config.NumberColumn(format="%.2f"),
            "Occupancy_2025": st.column_config.NumberColumn(format="%.2f%%"),
            "Occupancy_Change": st.column_config.NumberColumn(format="%.2f"),
            "Guest_Arrivals_2025": st.column_config.NumberColumn(format="%.0f"),
            "Guest_Arrivals_%Change": st.column_config.NumberColumn(format="%.2f%%"),
            "Revenue_per_Visitor_2025": st.column_config.NumberColumn(format="%.2f"),
        },
    )

st.caption(
    "หมายเหตุ: Dashboard นี้ใช้ข้อมูล January–December 2025 เทียบกับ 2024 "
    "จากไฟล์ tourismSouthCSV.csv โดยรายได้อยู่ในหน่วยล้านบาท"
)
