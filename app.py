import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json

# Carrega credenciais do Streamlit Secrets
cred_json = st.secrets["google_sheets"]["cred_json"]
cred_dict = json.loads(cred_json)
creds = Credentials.from_service_account_info(cred_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
gc = gspread.authorize(creds)

# Use o ID da planilha
SHEET_ID = "1PLSVD3VxmgfWKOyr3Z700TbxCIZr1sT8IlOiSIvDvxM"
sh = gc.open_by_key(SHEET_ID)
worksheet = sh.sheet1

# --- Configurações Streamlit ---
st.set_page_config(page_title="Verificador de Portas", page_icon="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png")
st.title("Verificador de Portas Disponíveis")
st.markdown(
    "Digite o identificador (ex: CB07-SP06-CX15)  \n"
    "Observação: Caso o Bairro for Jaguaré, sempre será o CB16"
)

# --- Entrada ---
entrada = st.text_input("", "").upper()
buscar = st.button("🔍 Buscar")

if buscar and entrada:

    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        # --- Conexão com Google Sheets via Service Account ---
        try:
            cred_dict = json.loads(st.secrets["google_sheets"]["cred_json"])
            SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_info(cred_dict, scopes=SCOPES)
            gc = gspread.authorize(creds)
        except Exception as e:
            st.error(f"❌ Erro ao conectar ao Google Sheets: {e}")
            st.stop()

        # --- Abrir a planilha ---
        SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE"
        sh = gc.open_by_url(SHEET_URL)
        worksheet = sh.sheet1  # ou sh.worksheet("Aba1")

        # --- Lê os dados ---
        df = pd.DataFrame(worksheet.get_all_records())

        # --- Adiciona colunas se não existirem ---
        for col in ["ADICIONOU_CLIENTE", "OCUPADA"]:
            if col not in df.columns:
                df[col] = ""

        # --- Filtra porta disponível ---
        filtro = df[
            (df["CABO"].astype(str).str.upper().str.strip() == cabo_val) &
            (df["PRIMARIA"].astype(str).str.upper().str.strip() == primaria_val) &
            (df["CAIXA"].astype(str).str.upper().str.strip() == caixa_val) &
            (df["OCUPADA"].astype(str).str.upper().str.strip() == "NÃO")
        ]

        if filtro.empty:
            st.error(
                f"❌ Nenhuma Porta disponível encontrada para: {entrada}  \n"
                f"📞 Ligue para o TI ou clique no WhatsApp abaixo"
            )
            st.markdown(
                "<a href='https://wa.link/xcmibx' target='_blank'>"
                "<img src='https://logodownload.org/wp-content/uploads/2015/04/whatsapp-logo-2-1.png' width='40'></a>",
                unsafe_allow_html=True
            )
        else:
            st.success(f"🟢 Portas Disponíveis para: {entrada}")

            # --- Mostra cada porta com opção SIM/NÃO ---
            for idx, row in filtro.iterrows():
                cols = st.columns([3, 2])
                with cols[0]:
                    st.write(f"{row['CABO']}-{row['PRIMARIA']}-{row['CAIXA']} | PORTA {row['PORTA']}")
                with cols[1]:
                    escolha = st.radio(
                        "Adicionou Cliente?",
                        options=["", "SIM", "NÃO"],
                        key=f"{row['ID']}"
                    )
                    if escolha == "SIM":
                        # Atualiza DataFrame
                        df.at[idx, "ADICIONOU_CLIENTE"] = f"SIM, {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                        df.at[idx, "OCUPADA"] = "SIM"

                        # Atualiza Google Sheet
                        worksheet.update_cell(idx + 2, df.columns.get_loc("ADICIONOU_CLIENTE") + 1,
                                              df.at[idx, "ADICIONOU_CLIENTE"])
                        worksheet.update_cell(idx + 2, df.columns.get_loc("OCUPADA") + 1, "SIM")

