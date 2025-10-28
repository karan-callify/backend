from os import getenv
import streamlit as st
import pandas as pd
from pymongo import MongoClient
import json
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# -----------------------------
# MongoDB Connection
# -----------------------------
MONGO_URI = getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = getenv("MONGO_DB_NAME", "callify")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="MongoDB Dashboard", layout="wide")
st.title("📊 MongoDB Data Viewer with Search")

# --- Sidebar: Collection Selection & Filters ---
st.sidebar.header("MongoDB Settings")

# List all collections in the DB
collections = db.list_collection_names()
selected_collection = st.sidebar.selectbox("Select Collection", collections)

collection = db[selected_collection]

# --- Search/Filter Input ---
st.sidebar.subheader("Search Filters")
path_filter = st.sidebar.text_input("Search by Path (partial match)")
job_id_filter = st.sidebar.text_input("Search by Job ID (exact match)")
request_id_filter = st.sidebar.text_input("Search by Request ID (exact match)")

# --- Build MongoDB Query ---
query = {}
if path_filter:
    query["path"] = {"$regex": path_filter, "$options": "i"}  # case-insensitive partial match
if job_id_filter:
    query["job_id"] = job_id_filter
if request_id_filter:
    query["request_id"] = request_id_filter

# --- Debug Info ---
st.sidebar.subheader("Debug Info")
total_docs = collection.count_documents({})
filtered_docs = collection.count_documents(query)
st.sidebar.write(f"Total documents in '{selected_collection}': {total_docs}")
st.sidebar.write(f"Documents matching filters: {filtered_docs}")

# --- Fetch Data ---
try:
    data = list(collection.find(query))  # fetch all matching documents
except Exception as e:
    st.error(f"Error fetching data from MongoDB: {e}")
    st.stop()

if not data:
    st.warning("No data found for the given search/filter.")
else:
    # Convert Mongo documents → DataFrame
    df = pd.DataFrame(data)

    # --- Flatten 'logs' array if present ---
    if "logs" in df.columns:
        def format_logs(log_list):
            try:
                # Convert each log object to JSON string
                return "\n".join([json.dumps(log, ensure_ascii=False) for log in log_list])
            except:
                return ""
        df["logs"] = df["logs"].apply(format_logs)

    # Drop MongoDB _id column for cleaner view
    if "_id" in df.columns:
        df.drop(columns=["_id"], inplace=True)

    # Display data table
    st.dataframe(df, use_container_width=True)

    # CSV download option
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"{selected_collection}_filtered_data.csv",
        mime="text/csv",
    )
