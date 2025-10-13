import streamlit as st
import pandas as pd
import gspread
import os
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==========================
# CONFIGURAÇÕES INICIAIS
# ==========================
st.set_page_config(page_title="Verificador de Portas", page_icon="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png")

st.markdown(
    """
    <link rel="apple-touch-icon" sizes="180x180" href="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png">
    <link rel="icon" type="image/png" sizes="32x32" href="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png">
    <link rel="icon" type="image/png" sizes="16x16" href="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png">
    <link rel="manifest" href="manifest.json">
    """,
    unsafe_allow_html=True
)

st.title("Verificador de Portas Disponíveis")
st.markdown("Digite o identificador (ex: CB07-SP06-CX15)  \nObservação: Caso o Bairro for Jaguaré, sempre será o CB16")

# ==========================
# CONEXÃO COM GOOGLE SHEETS
# ==========================
try:
    creds_json = os.environ.get("GOOGLE_CRED_JSON")
    creds_dict = json.loads(creds_json)
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    gc = gspread.authorize(creds)

    # Conecta à planilha
    sheet_url = "https://docs.google.com/spreadsheets/d/1PLSVD3VxmgfWKOyr3Z700TbxCIZr1sT8IlOiSIvDvxM/edit#gid=0"
    sh = gc.open_by_url(sheet_url)
    worksheet = sh.sheet1
except Exception as e:
    st.error(f"Erro ao conectar ao Google Sheets: {e}")

# ==========================
# BUSCA DE PORTAS
# ==========================
entrada = st.text_input("", "").upper()
buscar = st.button("🔍 Buscar")

if buscar and entrada:
    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        # Lê os dados da planilha
        df = pd.DataFrame(worksheet.get_all_records())
        df.columns = [col.strip().upper().replace(" ", "_") for col in df.columns]

        # Verifica se colunas esperadas existem
        colunas_esperadas = ["CABO", "PRIMARIA", "CAIXA", "PORTA", "OCUPADA", "ADICIONOU_CLIENTE"]
        for col in colunas_esperadas:
            if col not in df.columns:
                st.error(f"⚠️ Coluna ausente na planilha: {col}")
                st.stop()

        # Filtro das portas disponíveis
        filtro = df[
            (df["CABO"].astype(str).str.upper().str.strip() == cabo_val.upper()) &
            (df["PRIMARIA"].astype(str).str.upper().str.strip() == primaria_val.upper()) &
            (df["CAIXA"].astype(str).str.upper().str.strip() == caixa_val.upper()) &
            (df["OCUPADA"].astype(str).str.upper().str.strip() == "NÃO")
        ]

        if filtro.empty:
            st.error(
                f"❌ Nenhuma Porta disponível encontrada para: {entrada}  \n"
                f"📞 Ligue para o TI para Atualizar a Caixa: (11) 94484-7040 ou Clique no Ícone do Whatsapp"
            )
            st.markdown(
                "<a href='https://wa.link/xcmibx' target='_blank'>"
                "<img src='https://logodownload.org/wp-content/uploads/2015/04/whatsapp-logo-2-1.png' width='40'></a>",
                unsafe_allow_html=True
            )
        else:
            st.success(f"🟢 Portas Disponíveis para: {entrada}")
            st.table(filtro[["CABO", "PRIMARIA", "CAIXA", "PORTA"]])

            # --- Adicionou Cliente? ---
            st.markdown("### Adicionou Cliente?")
            col1, col2 = st.columns(2)
            with col1:
                sim = st.button("✅ SIM")
            with col2:
                nao = st.button("❌ NÃO")

            if sim:
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                # Atualiza a primeira linha correspondente no Google Sheets
                idx = filtro.index[0] + 2  # +2 porque planilhas começam na linha 2
                worksheet.update_acell(f"K{idx}", f"SIM, {agora}")  # Coluna ADICIONOU_CLIENTE
                worksheet.update_acell(f"I{idx}", "SIM")  # Coluna OCUPADA
                st.success("✅ Cliente adicionado e planilha atualizada com sucesso!")

            elif nao:
                st.info("Nenhuma alteração realizada.")
