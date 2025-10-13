import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

# ==============================
# CONFIGURAÇÕES INICIAIS STREAMLIT
# ==============================
st.set_page_config(
    page_title="Verificador de Portas",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/4/4e/Question_mark_alternate.svg",
)

st.title("Verificador de Portas Disponíveis")
st.markdown(
    "Digite o identificador (ex: CB07-SP06-CX15)\n"
    "Observação: Caso o Bairro for Jaguaré, sempre será o CB16"
)

# ==============================
# AUTENTICAÇÃO GOOGLE SHEETS
# ==============================
cred_json = st.secrets["google_sheets"]["cred_json"]
cred_dict = json.loads(cred_json)

creds = Credentials.from_service_account_info(
    cred_dict,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)
gc = gspread.authorize(creds)

# ID da planilha (extraído da URL completa)
SHEET_ID = "1PLSVD3VxmgfWKOyr3Z700TbxCIZr1sT8IlOiSIvDvxM"
sh = gc.open_by_key(SHEET_ID)
worksheet = sh.sheet1  # Seleciona a primeira aba

# ==============================
# ENTRADA DO USUÁRIO
# ==============================
entrada = st.text_input("Identificador", "").upper()
buscar = st.button("🔍 Buscar")

if buscar and entrada:
    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        # Converte planilha em DataFrame
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        # Certifique-se de ter essas colunas
        colunas_necessarias = [
            "CABO", "PRIMARIA", "CAIXA", "ID", "PORTA", "CAPACIDADE",
            "INTERFACE", "DATA_DE_ATUALIZACAO", "OCUPADA", "OBSERVACAO", "ADICIONOU_CLIENTE"
        ]
        for col in colunas_necessarias:
            if col not in df.columns:
                df[col] = ""

        # Filtra as portas disponíveis
        filtro = df[
            (df["CABO"].astype(str).str.upper().str.strip() == cabo_val) &
            (df["PRIMARIA"].astype(str).str.upper().str.strip() == primaria_val) &
            (df["CAIXA"].astype(str).str.upper().str.strip() == caixa_val) &
            (df["OCUPADA"].astype(str).str.upper().str.strip() != "SIM")
        ]

        if filtro.empty:
            st.error(f"❌ Nenhuma porta disponível para {entrada}")
            st.markdown(
                "<a href='https://wa.link/xcmibx' target='_blank'>"
                "<img src='https://logodownload.org/wp-content/uploads/2015/04/whatsapp-logo-2-1.png' width='40'></a>",
                unsafe_allow_html=True
            )
        else:
            st.success(f"🟢 Portas Disponíveis para {entrada}")
            
            # Mostra tabela resumida
            colunas_mostrar = ["PORTA", "CAPACIDADE", "INTERFACE", "OBSERVACAO", "ADICIONOU_CLIENTE"]
            st.table(filtro[colunas_mostrar].fillna(""))

            # ==============================
            # BOTÕES SIM / NÃO PARA ADICIONAR CLIENTE
            # ==============================
            for idx, row in filtro.iterrows():
                st.write(f"Porta: {row['PORTA']}")
                col1, col2 = st.columns(2)
                if col1.button(f"SIM - {row['PORTA']}", key=f"sim_{idx}"):
                    # Atualiza no DataFrame
                    df.at[idx, "ADICIONOU_CLIENTE"] = f"SIM, {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                    df.at[idx, "OCUPADA"] = "SIM"
                    
                    # Atualiza no Google Sheets
                    worksheet.update(f"K{idx+2}", df.at[idx, "ADICIONOU_CLIENTE"])  # coluna K = ADICIONOU_CLIENTE
                    worksheet.update(f"I{idx+2}", df.at[idx, "OCUPADA"])  # coluna I = OCUPADA
                    st.success(f"✅ Portador {row['PORTA']} atualizado com sucesso!")

                if col2.button(f"NÃO - {row['PORTA']}", key=f"nao_{idx}"):
                    st.info(f"Porta {row['PORTA']} não foi alterada.")
