import streamlit as st
import calendar
import plotly.graph_objects as go
from datetime import datetime

def render_festival_calendar(f_name, f_date_str):
    f_date = datetime.strptime(f_date_str, "%Y-%m-%d")
    year, month = f_date.year, f_date.month
    cal_grid = calendar.monthcalendar(year, month)
    
    z_data, text_data = [], []
    for week in cal_grid:
        z_week, t_week = [], []
        for day in week:
            if day == 0:
                z_week.append(0); t_week.append("")
            else:
                if day == f_date.day: z_week.append(2) # Peak Green
                elif abs(day - f_date.day) <= 2: z_week.append(1) # Window Orange
                else: z_week.append(0.2) # Normal Dark
                t_week.append(str(day))
        z_data.append(z_week); text_data.append(t_week)

    fig = go.Figure(data=go.Heatmap(
        z=z_data, x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        colorscale=[[0, "#1e1e1e"], [0.1, "#2d2d2d"], [0.5, "orange"], [1, "green"]],
        showscale=False, xgap=3, ygap=3
    ))
    
    for i, row in enumerate(text_data):
        for j, val in enumerate(row):
            fig.add_annotation(x=j, y=i, text=val, showarrow=False, font=dict(color="white"))
            
    fig.update_layout(title=f"{f_name} - {calendar.month_name[month]}", 
                      height=280, yaxis_autorange='reversed', template="plotly_dark",
                      margin=dict(l=10, r=10, t=40, b=10))
    return fig
