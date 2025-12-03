import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------- CONFIG GIAO DIỆN -----------------
st.set_page_config(page_title="Dashboard KPI", layout="wide", page_icon="📊")
st.markdown("""
<style>
.kpi-card {
    background-color: #ffffff;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    text-align: center;
    margin-bottom: 10px;
}
.kpi-number { font-size: 28px; font-weight: bold; color: #2E86C1; }
.kpi-title { font-size: 16px; font-weight: 600; color: #444444; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard KPI – Tổng hợp & Theo Nhân viên / Phòng ban")

# ----------------- UPLOAD FILE -----------------
st.sidebar.header("📁 Tải file Excel KPI")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel (*.xlsx)", type=["xlsx"])

if not uploaded_file:
    st.info("⬆️ Vui lòng upload file KPI")
    st.stop()

# ----------------- LOAD DATA -----------------
@st.cache_data
def load_excel(file):
    df_data = pd.read_excel(file, sheet_name="Du_Lieu")
    df_meta = pd.read_excel(file, sheet_name="Dinh_nghia_KPI")
    df_nv = pd.read_excel(file, sheet_name="Danh_sach_nhan_vien")
    # Loại bỏ khoảng trắng cột
    df_data.columns = df_data.columns.str.strip()
    df_meta.columns = df_meta.columns.str.strip()
    df_nv.columns = df_nv.columns.str.strip()
    df_data["Ngay"] = pd.to_datetime(df_data["Ngay"])
    return df_data, df_meta, df_nv

df, df_kpi, df_nv = load_excel(uploaded_file)

# ----------------- MENU BÊN TRÁI -----------------
st.sidebar.header("🔍 Chức năng")
menu = st.sidebar.radio(
    "Chọn chức năng",
    ["Tổng quát dữ liệu", "Dashboard KPI", "Hiện bảng dữ liệu"]
)

# ----------------- LỌC NGÀY CHUNG -----------------
min_date = df["Ngay"].min()
max_date = df["Ngay"].max()
start_date, end_date = st.sidebar.date_input("Chọn khoảng ngày", [min_date, max_date])
df_filtered = df[(df["Ngay"] >= pd.to_datetime(start_date)) & (df["Ngay"] <= pd.to_datetime(end_date))]

# ----------------- TỔNG QUÁT DỮ LIỆU -----------------
if menu == "Tổng quát dữ liệu":
    st.title("📊 Tổng quát dữ liệu KPI")
    
    st.subheader("📌 Thống kê nhanh")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Số nhân viên", df_filtered["Ten_nhan_vien"].nunique())
    col2.metric("Số phòng ban", df_filtered["Phong_ban"].nunique())
    col3.metric("Số KPI theo dõi", df_filtered["KPI"].nunique())
    col4.metric("Tổng giá trị KPI", df_filtered["Gia_tri"].sum())

    st.subheader("📈 Tổng hợp KPI theo Phòng ban")
    df_pb = df_filtered.groupby("Phong_ban")["Gia_tri"].sum().reset_index()
    fig_pb = px.bar(df_pb, x="Phong_ban", y="Gia_tri", color="Phong_ban",
                    title="Tổng giá trị KPI theo Phòng ban")
    st.plotly_chart(fig_pb, use_container_width=True)

    st.subheader("📈 Tổng hợp KPI theo Nhân viên")
    df_nv_sum = df_filtered.groupby("Ten_nhan_vien")["Gia_tri"].sum().reset_index()
    fig_nv = px.bar(df_nv_sum, x="Ten_nhan_vien", y="Gia_tri", color="Ten_nhan_vien",
                    title="Tổng giá trị KPI theo Nhân viên")
    st.plotly_chart(fig_nv, use_container_width=True)

    st.subheader("🔥 Heatmap tổng quan KPI")
    df_pivot_total = df_filtered.pivot_table(index="Ten_nhan_vien", columns="KPI", values="Gia_tri", aggfunc="sum")
    fig_heat_total = px.imshow(df_pivot_total, aspect="auto", color_continuous_scale="RdYlGn")
    st.plotly_chart(fig_heat_total, use_container_width=True)

    st.stop()

# ----------------- HIỆN BẢNG DỮ LIỆU -----------------
# ----------------- HIỆN BẢNG DỮ LIỆU -----------------
if menu == "Hiện bảng dữ liệu":
    st.title("📄 Bảng dữ liệu Excel")

    # ----------------- Lọc phòng ban -----------------
    list_pb = sorted(df_filtered["Phong_ban"].unique())
    selected_pb = st.sidebar.selectbox("Chọn phòng ban", ["Tất cả"] + list_pb)
    if selected_pb != "Tất cả":
        df_filtered = df_filtered[df_filtered["Phong_ban"] == selected_pb]

    # ----------------- Tìm kiếm nhân viên -----------------
    search = st.text_input("Tìm nhân viên")
    if search:
        df_filtered = df_filtered[df_filtered["Ten_nhan_vien"].str.contains(search, case=False)]

    # ----------------- Hiển thị bảng -----------------
    st.dataframe(df_filtered)
    st.stop()


# ----------------- DASHBOARD KPI -----------------
st.sidebar.header("🔍 Bộ lọc Dashboard")
view_mode = st.sidebar.radio("Chế độ xem", ["Theo Nhân viên", "Theo Phòng ban"])

list_nv = sorted(df_filtered["Ten_nhan_vien"].unique())
list_pb = sorted(df_filtered["Phong_ban"].unique())
list_kpi = sorted(df_filtered["KPI"].unique())

# Lọc theo chế độ
if view_mode == "Theo Nhân viên":
    selected_nv = st.sidebar.selectbox("Chọn nhân viên", list_nv)
    selected_kpi = st.sidebar.selectbox("Chọn KPI", list_kpi)
    df_view = df_filtered[(df_filtered["Ten_nhan_vien"] == selected_nv) & (df_filtered["KPI"] == selected_kpi)]
    st.header(f"📊 Dashboard KPI – Nhân viên: {selected_nv}")
    st.subheader(f"KPI: **{selected_kpi}**")
else:
    selected_pb = st.sidebar.selectbox("Chọn phòng ban", list_pb)
    selected_kpi = st.sidebar.selectbox("Chọn KPI", list_kpi)
    df_view = df_filtered[(df_filtered["Phong_ban"] == selected_pb) & (df_filtered["KPI"] == selected_kpi)]
    st.header(f"🏢 Dashboard KPI – Phòng ban: {selected_pb}")
    st.subheader(f"KPI: **{selected_kpi}**")

# ----------------- KPI CARDS -----------------
st.subheader("📌 Tổng quan KPI")
col1, col2, col3, col4 = st.columns(4)

def kpi_card(title, number):
    return f"""<div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-number">{number}</div>
            </div>"""

col1.markdown(kpi_card("Số dòng dữ liệu", len(df_view)), unsafe_allow_html=True)
col2.markdown(kpi_card("Số nhân viên", df_view["Ten_nhan_vien"].nunique()), unsafe_allow_html=True)
col3.markdown(kpi_card("Số KPI theo dõi", df_view["KPI"].nunique()), unsafe_allow_html=True)
col4.markdown(kpi_card("Số phòng ban", df_view["Phong_ban"].nunique()), unsafe_allow_html=True)

# ----------------- KPI BAR NGANG (Thay Gauge) -----------------
st.subheader("🟢 KPI – Thực tế vs Mục tiêu")
if len(df_view) > 0:
    df_latest = df_view.sort_values("Ngay").groupby("KPI").last().reset_index()
    fig_bar_goal = go.Figure()
    fig_bar_goal.add_trace(go.Bar(
        x=df_latest["Gia_tri"],
        y=df_latest["KPI"],
        orientation='h',
        name="Thực tế",
        marker_color='blue'
    ))
    fig_bar_goal.add_trace(go.Bar(
        x=df_latest["Muc_tieu"],
        y=df_latest["KPI"],
        orientation='h',
        name="Mục tiêu",
        marker_color='orange'
    ))
    fig_bar_goal.update_layout(barmode='overlay', xaxis_title="Giá trị", yaxis_title="KPI")
    st.plotly_chart(fig_bar_goal, use_container_width=True)

# ----------------- BIỂU ĐỒ LINE -----------------
st.subheader("📈 Xu hướng KPI theo thời gian")
if len(df_view) > 0:
    fig_line = px.line(df_view.sort_values("Ngay"), x="Ngay", y="Gia_tri", color="KPI", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

# ----------------- BIỂU ĐỒ BAR -----------------
st.subheader("📊 So sánh KPI theo trạng thái")
df_grp = df_view.groupby(["Ten_nhan_vien", "KPI"])["Gia_tri"].mean().reset_index()
if len(df_grp) > 0:
    fig_bar = px.bar(df_grp, x="Ten_nhan_vien", y="Gia_tri", color="KPI", barmode="group")
    st.plotly_chart(fig_bar, use_container_width=True)

# ----------------- HEATMAP -----------------
st.subheader("🔥 Heatmap KPI")
df_pivot = df_view.pivot_table(index="Ten_nhan_vien", columns="KPI", values="Gia_tri", aggfunc="mean")
if df_pivot.shape[0] > 0:
    fig_heat = px.imshow(df_pivot, aspect="auto", color_continuous_scale="RdYlGn")
    st.plotly_chart(fig_heat, use_container_width=True)

# ----------------- BẢNG DỮ LIỆU -----------------
st.subheader("📄 Chi tiết dữ liệu")
st.dataframe(df_view)
