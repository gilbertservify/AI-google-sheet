import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --------------------------
# Google Sheets Connection via REST API
# --------------------------

def load_data():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SERVICE_ACCOUNT_FILE = 'service_account.json'  # Make sure this file is present

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Connect to the Sheets API
    service = build('sheets', 'v4', credentials=creds)
    
    # Define spreadsheet ID and range
    SPREADSHEET_ID = '1LaA8MP9YlOYZJXb5S7JHlNidl88V5OxQMQ1BuNRTCLE'
    RANGE_NAME = 'Data'  # Or 'Sheet1!A1:F100' if you want a specific range

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        raise ValueError("No data found in the spreadsheet.")

    # Convert to DataFrame
    header, *rows = values
    df = pd.DataFrame(rows, columns=header)
    return df

# --------------------------
# Main Logic
# --------------------------
try:
    df = load_data()
    print("✅ Data loaded successfully:")
    print(df.head())
except Exception as e:
    print("❌ Failed to load data:", repr(e))
    exit()

# Convert columns
if "Amount" in df.columns:
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# --------------------------
# Summary
# --------------------------
print(f"\nTotal Rows: {len(df)}")
if "Amount" in df.columns:
    print(f"Total Amount: ${df['Amount'].sum():,.2f}")

# --------------------------
# Charts (saved as HTML)
# --------------------------

# Pie Chart
if "Category" in df.columns:
    fig1 = px.pie(df, names="Category", title="Category Distribution")
    fig1.write_html("pie_chart.html")
    print("📊 Pie chart saved to pie_chart.html")

# Bar Chart
if "Date" in df.columns and "Amount" in df.columns:
    df_grouped = df.groupby(df["Date"].dt.date)["Amount"].sum().reset_index()
    fig2 = px.bar(df_grouped, x="Date", y="Amount", title="Amount Over Time")
    fig2.write_html("bar_chart.html")
    print("📊 Bar chart saved to bar_chart.html")
