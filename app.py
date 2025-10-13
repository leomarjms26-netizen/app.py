import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Verificador de Portas", page_icon="🔌")
st.title("Verificador de Portas Disponíveis")
st.markdown("Digite o identificador (ex: CB07-SP06-CX15)\nObservação: Caso o Bairro seja Jaguaré, sempre será o CB16")

# Entrada do usuário
entrada = st.text_input("Identificador", "").upper()
buscar = st.button("🔍 Buscar")

# Conectar ao Google Sheets via secret
try:
    cred_json = st.secrets["google_sheets"]["cred_json"]
    creds = Credentials.from_service_account_info(pd.io.json.loads(cred_json))
    gc = gspread.authorize(creds)

    # Abra a planilha pelo link
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1PLSVD3VxmgfWKOyr3Z700TbxCIZr1sT8IlOiSIvDvxM/edit"
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1  # primeira aba

except Exception as e:
    st.error(f"❌ Erro ao conectar ao Google Sheets: {e}")
    st.stop()

# Função para carregar DataFrame da planilha
def carregar_planilha(ws):
    all_values = ws.get_all_values()
    if len(all_values) > 1:
        df = pd.DataFrame(all_values[1:], columns=all_values[0])
    else:
        df = pd.DataFrame(columns=["CABO","PRIMARIA","CAIXA","ID","PORTA","CAPACIDADE",
                                   "INTERFACE","DATA_DE_ATUALIZACAO","OCUPADA","OBSERVACAO","ADICIONOU_CLIENTE"])
    return df

# Função para atualizar planilha ao clicar SIM
def atualizar_cliente(row_index):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    worksheet.update(f"K{row_index+2}", f"SIM, {agora}")  # Coluna K = ADICIONOU_CLIENTE?
    worksheet.update(f"I{row_index+2}", "SIM")  # Coluna I = OCUPADA

# Executa busca
if buscar and entrada:
    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        df = carregar_planilha(worksheet)

        # Filtra portos disponíveis
        filtro = df[
            (df["CABO"].str.upper().str.strip() == cabo_val) &
            (df["PRIMARIA"].str.upper().str.strip() == primaria_val) &
            (df["CAIXA"].str.upper().str.strip() == caixa_val) &
            (df["OCUPADA"].str.upper().str.strip() == "NÃO")
        ]

        if filtro.empty:
            st.error(
                f"❌ Nenhuma porta disponível encontrada para: {entrada}\n"
                f"📞 Ligue para o TI ou clique no Whatsapp abaixo"
            )
            st.markdown(
                "<a href='https://wa.link/xcmibx' target='_blank'>"
                "<img src='https://logodownload.org/wp-content/uploads/2015/04/whatsapp-logo-2-1.png' width='40'></a>",
                unsafe_allow_html=True
            )
        else:
            st.success(f"🟢 Portas disponíveis para: {entrada}")

            # Mostra tabela sem índice
            df_mostrar = filtro.loc[:, :"CAPACIDADE"].copy()
            df_mostrar.index = [""] * len(df_mostrar)
            st.table(df_mostrar)

            # Botões SIM/NÃO
            for idx, row in filtro.iterrows():
                col1, col2 = st.columns([1,1])
                with col1:
                    if st.button(f"SIM ({row['ID']})"):
                        atualizar_cliente(idx)
                        st.success(f"✅ Porta {row['ID']} marcada como ADICIONOU CLIENTE e OCUPADA")
                with col2:
                    if st.button(f"NÃO ({row['ID']})"):
                        st.info(f"❌ Porta {row['ID']} não alterada")
