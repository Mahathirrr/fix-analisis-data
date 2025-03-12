import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Bike Sharing Analysis Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    hour_df = pd.read_csv('/home/neonnex/dev/dbs/fix-analisis-data2/data/hour.csv')
    day_df = pd.read_csv('/home/neonnex/dev/dbs/fix-analisis-data2/data/day.csv')

    # Rename columns for better understanding
    hour_df = hour_df.rename(columns={
        'cnt': 'total_rentals',
        'hr': 'hour',
        'yr': 'year',
        'dteday': 'date',
        'casual': 'casual_users',
        'registered': 'registered_users',
        'weathersit': 'weather_condition'
    })

    day_df = day_df.rename(columns={
        'cnt': 'total_rentals',
        'yr': 'year',
        'dteday': 'date',
        'casual': 'casual_users',
        'registered': 'registered_users',
        'weathersit': 'weather_condition'
    })

    # Convert date
    hour_df['date'] = pd.to_datetime(hour_df['date'])
    day_df['date'] = pd.to_datetime(day_df['date'])

    # Create mappings
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weather_map = {
        1: 'Clear',
        2: 'Mist',
        3: 'Light Snow/Rain',
        4: 'Heavy Rain/Snow'
    }

    # Apply mappings
    hour_df['season'] = hour_df['season'].map(season_map)
    hour_df['weather_condition'] = hour_df['weather_condition'].map(weather_map)
    day_df['season'] = day_df['season'].map(season_map)
    day_df['weather_condition'] = day_df['weather_condition'].map(weather_map)

    return hour_df, day_df

# Load the data
hour_df, day_df = load_data()

# Title
st.title("🚲 Bike Sharing Analysis Dashboard")
st.write("Analysis of bike sharing patterns and user behavior")

# Sidebar - Filters
st.sidebar.header("Filters")

# Year Filter
selected_year = st.sidebar.selectbox(
    "Select Year",
    options=[2011, 2012]
)

# Month Filter
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
selected_month = st.sidebar.selectbox("Select Month", months)

# Date Filter
start_date = st.sidebar.date_input(
    "Start Date", value=day_df['date'].min()
)
end_date = st.sidebar.date_input(
    "End Date", value=day_df['date'].max()
)

# Filter data based on selection
hour_df_filtered = hour_df[
    (hour_df['year'] == (selected_year - 2011)) &
    (hour_df['date'].dt.month == months.index(selected_month) + 1) &
    (hour_df['date'] >= pd.to_datetime(start_date)) &
    (hour_df['date'] <= pd.to_datetime(end_date))
]

day_df_filtered = day_df[
    (day_df['year'] == (selected_year - 2011)) &
    (day_df['date'].dt.month == months.index(selected_month) + 1) &
    (day_df['date'] >= pd.to_datetime(start_date)) &
    (day_df['date'] <= pd.to_datetime(end_date))
]

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Hourly Usage Patterns")
    hourly_usage = hour_df_filtered.groupby('hour')['total_rentals'].mean().reset_index()
    fig_hourly = px.line(
        hourly_usage,
        x='hour',
        y='total_rentals',
        title='Average Hourly Bike Rentals'
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

with col2:
    st.subheader("Seasonal Patterns")
    seasonal_usage = day_df_filtered.groupby('season')['total_rentals'].mean().reset_index()
    fig_seasonal = px.bar(
        seasonal_usage,
        x='season',
        y='total_rentals',
        title='Average Daily Rentals by Season'
    )
    st.plotly_chart(fig_seasonal, use_container_width=True)

# User Type Analysis
st.subheader("User Type Analysis")
col3, col4 = st.columns(2)

with col3:
    user_daily = day_df_filtered[['casual_users', 'registered_users']].mean()
    fig_users = go.Figure(data=[
        go.Bar(
            x=['Casual Users', 'Registered Users'],
            y=user_daily.values,
            marker_color=['#636EFA', '#EF553B']
        )
    ])
    fig_users.update_layout(
        title='Average Daily Users by Type',
        xaxis_title='User Type',
        yaxis_title='Average Count'
    )
    st.plotly_chart(fig_users, use_container_width=True)

with col4:
    weather_impact = hour_df_filtered.groupby('weather_condition')['total_rentals'].mean().reset_index()
    fig_weather = px.bar(
        weather_impact,
        x='weather_condition',
        y='total_rentals',
        title='Average Rentals by Weather Condition'
    )
    st.plotly_chart(fig_weather, use_container_width=True)

# Key Metrics
st.subheader("Key Metrics")
col5, col6, col7 = st.columns(3)

with col5:
    total_rentals = day_df_filtered['total_rentals'].sum()
    st.metric("Total Rentals", f"{total_rentals:,}")

with col6:
    avg_daily = day_df_filtered['total_rentals'].mean()
    st.metric("Average Daily Rentals", f"{avg_daily:.0f}")

with col7:
    peak_hour = hour_df_filtered.groupby('hour')['total_rentals'].mean().idxmax()
    st.metric("Peak Hour", f"{peak_hour:02d}:00")