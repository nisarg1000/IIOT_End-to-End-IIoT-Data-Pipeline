import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
 
DB_USER = "postgres"
DB_PASS = 1234
DB_HOST = "localhost" 
DB_PORT = "5432"
DB_NAME = "lab12"

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}', echo=False)

st.title("Sense HAT Live Data Dashboard")

# choose time window
minutes = st.sidebar.selectbox("Show last N minutes", [5, 15, 30, 60, 180, 1440], index=1)

query = f"""
SELECT recorded_at AT TIME ZONE 'UTC' as ts, temp_c, humidity, pressure, orientation_roll, orientation_pitch, orientation_yaw
FROM sense_readings
WHERE recorded_at >= now() - interval '{minutes} minutes' 
ORDER BY recorded_at ASC; 
"""

df = pd.read_sql(query, engine, parse_dates=['ts'])
st.write(f"Showing last {minutes} minutes — {len(df)} rows")

if len(df) == 0:
    st.info("No data in the selected time window.")
else:
    # Plot data
    fig_t = px.line(df, x='ts', y='temp_c', title='Temperature (°C)')
    st.plotly_chart(fig_t, use_container_width=True)

    fig_h = px.line(df, x='ts', y='humidity', title='Humidity (%)')
    st.plotly_chart(fig_h, use_container_width=True)

    fig_p = px.line(df, x='ts', y='pressure', title='Pressure (hPa)')
    st.plotly_chart(fig_p, use_container_width=True)

    st.subheader("Orientation (radians)")
    fig_o = px.line(df, x='ts', y=['orientation_roll','orientation_pitch','orientation_yaw'])
    st.plotly_chart(fig_o, use_container_width=True)

    st.dataframe(df.tail(20))
