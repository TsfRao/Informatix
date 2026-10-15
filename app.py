import streamlit as st
import ee
import json

# Initialize Earth Engine using Streamlit secrets
try:
    ee_secrets = dict(st.secrets["earth_engine"])
    credentials = ee.ServiceAccountCredentials(
        ee_secrets["client_email"],
        key_data=json.dumps(ee_secrets)
    )
    ee.Initialize(credentials, project=ee_secrets["project_id"])
except Exception:
    # Fallback for local testing
    ee.Initialize(project='your-actual-gcp-project-id')

st.title("🌍 Hydroinformatics & GeoAI Research Dashboard")
st.write("Earth Engine initialized successfully!")
