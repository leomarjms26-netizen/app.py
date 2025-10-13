import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- Configurações Streamlit ---
st.markdown(
    """
    <link rel="apple-touch-icon" sizes="180x180" href="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png">
    <link rel="icon" type="image/png" sizes="32x32" href="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png">
    <link rel="icon" type="image/png" sizes="16x16" href="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png">
    <link rel="manifest" href="manifest.json">
    """,
    unsafe_allow_html=True
)

st.set_page_config(
    page_title="Verificador de Portas",
    page_icon="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png"
)

st.title("Verificador de Portas Disponíveis")
st.markdown(
    "Digite o identificador (ex: CB07-SP06-CX15)  \n"
    "Observação: Caso o Bairro for Jaguaré, sempre será o CB16"
)

# Entrada de texto
entrada = st.text_input("", "").upper()

# Botão de busca com lupa
buscar = st.button("🔍 Buscar")

# --- Conexão Google Sheets ---
json_path = "/mount/src/app.py/credenciais.json"
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(json_path, scopes=scope)
gc = gspread.authorize(creds)

# Substitua pelo link da sua planilha
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRrExQYNSa64iJs2DK5MrnUhsXSrPhrxqYswB1zTRYCoGlAw9gMqh5d5G5SMaDaJtDd78gy4Ud-UHFW/edit#gid=0"
sh = gc.open_by_url(sheet_url)
worksheet = sh.sheet1  # ou sh.worksheet("Nome da aba")

# Executa a busca somente quando o botão é clicado
if buscar and entrada:
    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        # Lê toda a planilha como DataFrame
        df = pd.DataFrame(worksheet.get_all_records())
        df.columns = [
            "CABO", "PRIMARIA", "CAIXA", "ID", "PORTA", "CAPACIDADE",
            "INTERFACE", "DATA_DE_ATUALIZACAO", "OCUPADA", "OBSERVACAO", "ADICIONOU_CLIENTE"
        ]

        # Filtra apenas portas disponíveis
        filtro = df[
            (df["CABO"].astype(str).str.upper().str.strip() == cabo_val.upper()) &
            (df["PRIMARIA"].astype(str).str.upper().str.strip() == primaria_val.upper()) &
            (df["CAIXA"].astype(str).str.upper().str.strip() == caixa_val.upper()) &
            (df["OCUPADA"].astype(str).str.upper().str.strip() == "NÃO")
        ]

        if filtro.empty:
            st.error(
                f"❌ Nenhuma Porta disponível encontrada para: \n{entrada}  \n"
                f"📞 Ligue para o TI para Atualizar a Caixa: (11) 94484-7040 ou Clique no Ícone do Whatsapp para ser redirecionado"
            )
            st.markdown(
                "<a href='https://wa.link/xcmibx' target='_blank'>"
                "<img src='https://logodownload.org/wp-content/uploads/2015/04/whatsapp-logo-2-1.png' width='40'></a>",
                unsafe_allow_html=True
            )
        else:
            st.success(f"🟢 Portas Disponíveis para: {entrada}")

            # Seleciona apenas as colunas até 'CAPACIDADE'
            colunas_ate_capacidade = filtro.loc[:, :"CAPACIDADE"]
            df_sem_indice = colunas_ate_capacidade.copy()
            df_sem_indice.index = [""] * len(df_sem_indice)  # esconde índice lateral

            st.table(df_sem_indice)

            # --- Radio buttons horizontal para marcar se adicionou cliente ---
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

                    # Atualiza no Google Sheet (gspread)
                    row_number = idx + 2  # +2 porque a primeira linha é cabeçalho
                    worksheet.update(f"K{row_number}", f"SIM, {now}")  # coluna ADICIONOU_CLIENTE
                    worksheet.update(f"I{row_number}", "SIM")          # coluna OCUPADA

                st.success("✅ Planilha atualizada com sucesso!")
