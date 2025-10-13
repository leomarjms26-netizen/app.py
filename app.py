import json
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st

SHEET_URL = "https://docs.google.com/spreadsheets/d/…"

cred_json = st.secrets["gcp_service_account"]["key"]
cred_dict = json.loads(cred_json)

scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_info(cred_dict, scopes=scope)
gc = gspread.authorize(creds)
sh = gc.open_by_url(SHEET_URL)
