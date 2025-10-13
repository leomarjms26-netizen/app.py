import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configurações do app
st.set_page_config(
    page_title="Verificador de Portas",
    page_icon="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png"
)

st.title("Verificador de Portas Disponíveis")

st.markdown(
    "Digite o identificador (ex: CB07-SP06-CX15)  \n"
    "Observação: Caso o Bairro for Jaguaré, sempre será o CB16"
)

# Caminho da sua nova chave JSON
CRED_PATH = "arched-jigsaw-475014-p4-410881f0f9ec.json"

# URL da sua planilha
SHEET_URL = "https://docs.google.com/spreadsheets/d/1PLSVD3VxmgfWKOyr3Z700TbxCIZr1sT8IlOiSIvDvxM/edit#gid=0"

# Escopos necessários
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Conecta à planilha
try:
    creds = Credentials.from_service_account_file(CRED_PATH, scopes=scope)
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Google Sheets: {e}")
    st.stop()

# Entrada de texto
entrada = st.text_input("", "").upper()
buscar = st.button("🔍 Buscar")

if buscar and entrada:
    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        # Lê dados da planilha
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        # Ajusta nomes das colunas se necessário
        df.columns = [
            "CABO", "PRIMARIA", "CAIXA", "ID", "PORTA", "CAPACIDADE",
            "INTERFACE", "DATA_DE_ATUALIZACAO", "OCUPADA", "OBSERVACAO"
        ]

        # Filtra portas disponíveis
        filtro = df[
            (df["CABO"].astype(str).str.upper().str.strip() == cabo_val.upper()) &
            (df["PRIMARIA"].astype(str).str.upper().str.strip() == primaria_val.upper()) &
            (df["CAIXA"].astype(str).str.upper().str.strip() == caixa_val.upper()) &
            (df["OCUPADA"].astype(str).str.upper().str.strip() == "NÃO")
        ]

        if filtro.empty:
            st.error(
                f"❌ Nenhuma Porta disponível encontrada para: \n{entrada}  \n"
                f"📞 Ligue para o TI para Atualizar a Caixa: (11) 94484-7040"
            )
        else:
            st.success(f"🟢 Portas Disponíveis para: {entrada}")
            df_sem_indice = filtro.loc[:, :"CAPACIDADE"].copy()
            df_sem_indice.index = [""] * len(df_sem_indice)
            st.table(df_sem_indice)
