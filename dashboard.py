import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Air Quality Monitoring Dashboard",
    layout="wide",
    page_icon="🌍"
)

# --------------------------------------------------
# Load & Clean Data
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main.csv")

    # 🔥 Rebuild datetime to FIX 2013 issue
    df["datetime"] = pd.to_datetime(
        df[["year", "month", "day", "hour"]],
        errors="coerce"
    )

    df = df.dropna(subset=["datetime"])
    df = df.sort_values("datetime")

    return df

df = load_data()

# --------------------------------------------------
# Wind Direction Mapping (FULL NAMES)
# --------------------------------------------------
WIND_DIR_MAP = {
    "N": "North",
    "NNE": "North-Northeast",
    "NE": "Northeast",
    "ENE": "East-Northeast",
    "E": "East",
    "ESE": "East-Southeast",
    "SE": "Southeast",
    "SSE": "South-Southeast",
    "S": "South",
    "SSW": "South-Southwest",
    "SW": "Southwest",
    "WSW": "West-Southwest",
    "W": "West",
    "WNW": "West-Northwest",
    "NW": "Northwest",
    "NNW": "North-Northwest"
}

df["wind_direction_full"] = df["wd"].map(WIND_DIR_MAP)

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------
st.sidebar.header("🔎 Filters")

stations = st.sidebar.multiselect(
    "Select Station",
    df["station"].unique(),
    default=df["station"].unique()
)

seasons = st.sidebar.multiselect(
    "Select Season",
    df["season"].unique(),
    default=df["season"].unique()
)

pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
selected_pollutant = st.sidebar.selectbox(
    "Select Pollutant (Detailed View)",
    pollutants
)

# --------------------------------------------------
# Date Range (STRICT to data)
# --------------------------------------------------
min_date = df["datetime"].min().date()
max_date = df["datetime"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# --------------------------------------------------
# Apply Filters
# --------------------------------------------------
filtered_df = df[
    (df["station"].isin(stations)) &
    (df["season"].isin(seasons)) &
    (df["datetime"].dt.date >= date_range[0]) &
    (df["datetime"].dt.date <= date_range[1])
]

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("🌍 Air Quality Monitoring Dashboard")

# --------------------------------------------------
# KPI Metrics
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Average PSI", f"{filtered_df['PSI'].mean():.2f}")
col2.metric("Maximum PSI", f"{filtered_df['PSI'].max():.2f}")
col3.metric("Most Common Air Quality", filtered_df["Air_Quality"].mode()[0])
col4.metric("Total Records", f"{len(filtered_df):,}")

# ==================================================
# PSI & POLLUTANT TRENDS
# ==================================================
st.subheader("📈 PSI Trend Over Time")

fig_psi = px.line(
    filtered_df,
    x="datetime",
    y="PSI",
    color="station",
    title="PSI Over Time by Station"
)
st.plotly_chart(fig_psi, use_container_width=True)

st.subheader(f"🧪 {selected_pollutant} Trend Over Time")

fig_pollutant = px.line(
    filtered_df,
    x="datetime",
    y=selected_pollutant,
    color="station",
    title=f"{selected_pollutant} Concentration Over Time"
)
st.plotly_chart(fig_pollutant, use_container_width=True)

# ==================================================
# SEASONAL ANALYSIS
# ==================================================
st.subheader("🍂 Seasonal PSI Comparison")

seasonal_psi = (
    filtered_df
    .groupby("season")["PSI"]
    .mean()
    .reset_index()
)

fig_season_psi = px.bar(
    seasonal_psi,
    x="season",
    y="PSI",
    title="Average PSI by Season"
)
st.plotly_chart(fig_season_psi, use_container_width=True)

st.subheader(f"🌱 Seasonal {selected_pollutant} Comparison")

seasonal_pollutant = (
    filtered_df
    .groupby("season")[selected_pollutant]
    .mean()
    .reset_index()
)

fig_season_pollutant = px.bar(
    seasonal_pollutant,
    x="season",
    y=selected_pollutant,
    title=f"Average {selected_pollutant} by Season"
)
st.plotly_chart(fig_season_pollutant, use_container_width=True)

# ==================================================
# WIND & METEOROLOGY
# ==================================================
st.subheader("🌬️ Wind Speed vs PSI")

fig_wind_speed = px.scatter(
    filtered_df,
    x="WSPM",
    y="PSI",
    color="season",
    trendline="ols",
    title="Wind Speed Impact on PSI"
)
st.plotly_chart(fig_wind_speed, use_container_width=True)

st.subheader("🧭 Wind Direction Distribution")

wind_dir_counts = (
    filtered_df["wind_direction_full"]
    .value_counts()
    .reset_index()
)
wind_dir_counts.columns = ["Wind Direction", "Count"]

fig_wind_dir = px.bar(
    wind_dir_counts,
    x="Wind Direction",
    y="Count",
    title="Wind Direction Frequency"
)
st.plotly_chart(fig_wind_dir, use_container_width=True)

st.subheader("🌡️ Temperature vs PSI")

fig_temp = px.scatter(
    filtered_df,
    x="TEMP",
    y="PSI",
    color="season",
    trendline="ols",
    title="Temperature Impact on PSI"
)
st.plotly_chart(fig_temp, use_container_width=True)

# ==================================================
# STATION COMPARISON
# ==================================================
st.subheader("🏭 Station Ranking by Average PSI")

station_rank = (
    filtered_df
    .groupby("station")["PSI"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

fig_station = px.bar(
    station_rank,
    x="station",
    y="PSI",
    title="Average PSI by Station"
)
st.plotly_chart(fig_station, use_container_width=True)

# ==================================================
# DIURNAL PATTERN
# ==================================================
st.subheader("⏰ Hourly PSI Pattern")

filtered_df["hour"] = filtered_df["datetime"].dt.hour

hourly_psi = (
    filtered_df
    .groupby("hour")["PSI"]
    .mean()
    .reset_index()
)

fig_hour = px.line(
    hourly_psi,
    x="hour",
    y="PSI",
    title="Average PSI by Hour"
)
st.plotly_chart(fig_hour, use_container_width=True)

# ==================================================
# AIR QUALITY DISTRIBUTION
# ==================================================
st.subheader("🌫 Air Quality Category Distribution")

aq_counts = filtered_df["Air_Quality"].value_counts().reset_index()
aq_counts.columns = ["Air_Quality", "Count"]

fig_aq = px.bar(
    aq_counts,
    x="Air_Quality",
    y="Count",
    color="Air_Quality",
    title="Air Quality Classification"
)
st.plotly_chart(fig_aq, use_container_width=True)

# ==================================================
# CORRELATION HEATMAP
# ==================================================
st.subheader("🔗 Correlation: PSI, Pollutants & Meteorology")

corr_cols = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "TEMP", "WSPM", "PSI"]
corr = filtered_df[corr_cols].corr()

fig_corr, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig_corr)

# ==================================================
# RAW DATA
# ==================================================
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered_df)
