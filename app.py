import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ================================
# Configurações
# ================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1PLSVD3VxmgfWKOyr3Z700TbxCIZr1sT8IlOiSIvDvxM/edit"

# Escopos necessários
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ================================
# Carregar credenciais do Streamlit Secrets
# ================================
try:
    cred_json = st.secrets["gcp_service_account"]["key"]
    cred_dict = json.loads(cred_json)
    creds = Credentials.from_service_account_info(cred_dict, scopes=scope)
    gc = gspread.authorize(creds)
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Google Sheets: {e}")
    st.stop()

# ================================
# Abrir planilha
# ================================
try:
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1  # primeira aba
    data = worksheet.get_all_records()
except Exception as e:
    st.error(f"❌ Erro ao abrir a planilha: {e}")
    st.stop()

# ================================
# Exibir dados no Streamlit
# ================================
df = pd.DataFrame(data)
st.title("Visualização da Planilha")
st.dataframe(df)

# ================================
# Adicionar coluna "ADICIONOU CLIENTE?" com opções SIM/NÃO
# ================================
st.markdown("### Registrar Cliente")

col1, col2 = st.columns(2)

with col1:
    adicionou = st.radio("ADICIONOU CLIENTE?", ("SIM", "NÃO"))

# Quando o usuário selecionar SIM, registrar data/hora
if adicionou == "SIM":
    import datetime
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    df["ADICIONOU CLIENTE?"] = "SIM, " + agora
else:
    df["ADICIONOU CLIENTE?"] = "NÃO"

st.dataframe(df)

# ================================
# Salvar alterações de volta na planilha
# ================================
try:
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    st.success("✅ Dados atualizados na planilha!")
except Exception as e:
    st.error(f"❌ Erro ao atualizar a planilha: {e}")
