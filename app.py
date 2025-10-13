import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ========================================
# Conexão com o Google Sheets
# ========================================
# Caminho para o seu arquivo JSON baixado
CRED_PATH = "credenciais.json"

# Escopos necessários
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Carrega credenciais e autoriza
creds = Credentials.from_service_account_file(CRED_PATH, scopes=scope)
gc = gspread.authorize(creds)

# URL da planilha
SHEET_URL = "https://docs.google.com/spreadsheets/d/1PLSVD3VxmgfWKOyr3Z700TbxCIZr1sT8IlOiSIvDvxM/edit#gid=0"
sh = gc.open_by_url(SHEET_URL)
worksheet = sh.sheet1  # pega a primeira aba, ajuste se precisar

# ========================================
# Interface Streamlit
# ========================================

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
buscar = st.button("🔍 Buscar")

# Executa busca
if buscar and entrada:
    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        # Pega dados da planilha
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        # Se colunas não existirem, adiciona
        if "ADICIONOU_CLIENTE" not in df.columns:
            df["ADICIONOU_CLIENTE"] = ""
        if "OCUPADA" not in df.columns:
            df["OCUPADA"] = ""

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
                f"📞 Ligue para o TI para Atualizar a Caixa: (11) 94484-7040 ou Clique no Ícone do Whatsapp para ser redirecionado"
            )
            st.markdown(
                "<a href='https://wa.link/xcmibx' target='_blank'>"
                "<img src='https://logodownload.org/wp-content/uploads/2015/04/whatsapp-logo-2-1.png' width='40'></a>",
                unsafe_allow_html=True
            )
        else:
            st.success(f"🟢 Portas Disponíveis para: {entrada}")

            # Exibe tabela
            colunas_ate_capacidade = filtro.loc[:, :"CAPACIDADE"]
            df_sem_indice = colunas_ate_capacidade.copy()
            df_sem_indice.index = [""] * len(df_sem_indice)
            st.table(df_sem_indice)

            # Botão SIM / NÃO
            col1, col2 = st.columns(2)
            adicionou_cliente = None
            with col1:
                if st.button("SIM", key="sim"):
                    adicionou_cliente = "SIM"
            with col2:
                if st.button("NÃO", key="nao"):
                    adicionou_cliente = "NÃO"

            # Atualiza planilha se SIM
            if adicionou_cliente == "SIM":
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                # pega índices da tabela filtrada
                for idx in filtro.index:
                    worksheet.update_cell(idx + 2, df.columns.get_loc("ADICIONOU_CLIENTE") + 1, f"SIM, {now}")
                    worksheet.update_cell(idx + 2, df.columns.get_loc("OCUPADA") + 1, "SIM")
                st.success("✅ Planilha atualizada com sucesso!")
