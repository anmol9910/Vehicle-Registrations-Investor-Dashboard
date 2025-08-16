📊 Vehicle Registrations – Investor Dashboard
Overview

This project builds an interactive investor dashboard using Streamlit and Plotly.
The dashboard analyzes vehicle registration data from Vahan and provides key investor insights such as:

Total registrations over time

Quarterly and yearly growth (QoQ & YoY) by manufacturer

Category-wise performance (2W / 3W / 4W)

Automated investor insights & risk signals

🚀 Setup Instructions
1. Clone Repo & Install Dependencies
git clone https://github.com/<your-repo>/vahan-investor-dashboard.git
cd vahan-investor-dashboard
pip install -r requirements.txt

2. Required Files

Ensure these CSV files are in the same directory as the code:


category_year_bucketed.csv
category_year_bucketed_growth.csv
category_year_detail.csv
manufacturer_latest_quarter (1).csv
manufacturer_latest_quarter.csv
manufacturer_monthly.csv
manufacturer_quarterly (1).csv
manufacturer_quarterly.csv
manufacturer_quarterly_growth.csv

3. Run the App
streamlit run e4d295f1-cd1e-446a-b8b1-1f65562f03de.py


The dashboard will open in your browser at http://localhost:8501.

📂 Data Assumptions

Category buckets mapped heuristically:

TWO WHEELER* → 2W

THREE WHEELER* → 3W

LMV/MMV/HMV/Light/Medium/Heavy → 4W

Missing growth columns (qoq_pct, yoy_pct) are computed programmatically.

Null values are treated as 0 to avoid chart errors.

📊 Features

✅ Filter by manufacturer, time period, and vehicle category
✅ KPI metrics (total registrations, QoQ growth, YoY growth)
✅ Trend charts for manufacturers and categories
✅ Top & weakest performers automatically highlighted
✅ Risk/Market signal alerts

🛣 Feature Roadmap (if continued)

🔹 Add forecasting models (ARIMA / Prophet) for future sales prediction

🔹 Drilldown analysis by state / region

🔹 Compare EV vs ICE vehicles

🔹 Export insights as PDF reports
