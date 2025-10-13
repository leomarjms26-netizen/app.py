import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- Configurações Streamlit ---
st.set_page_config(
    page_title="Verificador de Portas",
    page_icon="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png"
)
st.title("Verificador de Portas Disponíveis")

# --- Entrada do usuário ---
entrada = st.text_input("Digite o identificador (ex: CB07-SP06-CX15)").upper()
buscar = st.button("🔍 Buscar")

# --- Conexão Google Sheets ---
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credenciais.json", scopes=scope)
gc = gspread.authorize(creds)
sheet_url = "URL_DA_PLANILHA_AQUI"
sh = gc.open_by_url(sheet_url)
worksheet = sh.sheet1  # ou worksheet pelo nome: sh.worksheet("Nome da aba")

if buscar and entrada:
    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        # --- Lê a planilha como DataFrame ---
        df = pd.DataFrame(worksheet.get_all_records())
        df.columns = [ "CABO", "PRIMARIA", "CAIXA", "ID", "PORTA", "CAPACIDADE",
                       "INTERFACE", "DATA_DE_ATUALIZACAO", "OCUPADA", "OBSERVACAO", "ADICIONOU_CLIENTE" ]

        filtro = df[
            (df["CABO"].str.upper().str.strip() == cabo_val.upper()) &
            (df["PRIMARIA"].str.upper().str.strip() == primaria_val.upper()) &
            (df["CAIXA"].str.upper().str.strip() == caixa_val.upper()) &
            (df["OCUPADA"].str.upper().str.strip() == "NÃO")
        ]

        if filtro.empty:
            st.error(f"❌ Nenhuma Porta disponível encontrada para: {entrada}")
        else:
            st.success(f"🟢 Portas Disponíveis para: {entrada}")
            colunas_ate_capacidade = filtro.loc[:, :"CAPACIDADE"]
            df_sem_indice = colunas_ate_capacidade.copy()
            df_sem_indice.index = [""] * len(df_sem_indice)
            st.table(df_sem_indice)

            # --- Radio buttons para marcar se adicionou cliente ---
            escolha = st.radio(
                "ADICIONOU CLIENTE?",
                options=["NÃO", "SIM"],
                horizontal=True
            )

            if escolha == "SIM":
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                for idx in filtro.index:
                    # Atualiza no DataFrame local
                    df.at[idx, "ADICIONOU_CLIENTE"] = f"SIM, {now}"
                    df.at[idx, "OCUPADA"] = "SIM"

                    # Atualiza no Google Sheet
                    row_number = idx + 2  # +2 porque gspread conta a primeira linha como 1 (cabeçalho)
                    worksheet.update(f"K{row_number}", f"SIM, {now}")  # coluna ADICIONOU_CLIENTE
                    worksheet.update(f"I{row_number}", "SIM")          # coluna OCUPADA

                st.success("✅ Planilha atualizada com sucesso!")
