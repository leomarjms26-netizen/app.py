import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ===================== CONFIGURAÇÃO =====================
st.set_page_config(
    page_title="Verificador de Portas",
    page_icon="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png"
)

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
st.markdown(
    "Digite o identificador (ex: CB07-SP06-CX15)  \n"
    "Observação: Caso o Bairro for Jaguaré, sempre será o CB16"
)

# ===================== CONEXÃO GOOGLE SHEETS =====================
CRED_PATH = "credenciais.json"  # arquivo que você subiu no GitHub
SHEET_URL = "https://docs.google.com/spreadsheets/d/1PLSVD3VxmgfWKOyr3Z700TbxCIZr1sT8IlOiSIvDvxM/edit#gid=0"

scope = ["https://www.googleapis.com/auth/spreadsheets", 
         "https://www.googleapis.com/auth/drive"]

try:
    creds = Credentials.from_service_account_file(CRED_PATH, scopes=scope)
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Google Sheets: {e}")
    st.stop()

# ===================== ENTRADA =====================
entrada = st.text_input("Identificador", "").upper()
buscar = st.button("🔍 Buscar")

# ===================== BUSCA =====================
if buscar and entrada:
    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        # Lê dados da planilha
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Garantir colunas necessárias
        required_cols = ["CABO", "PRIMARIA", "CAIXA", "ID", "PORTA", "CAPACIDADE",
                         "INTERFACE", "DATA_DE_ATUALIZACAO", "OCUPADA", "OBSERVACAO", "ADICIONOU_CLIENTE?"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        
        # Filtra portas disponíveis
        filtro = df[
            (df["CABO"].astype(str).str.upper().str.strip() == cabo_val.upper()) &
            (df["PRIMARIA"].astype(str).str.upper().str.strip() == primaria_val.upper()) &
            (df["CAIXA"].astype(str).str.upper().str.strip() == caixa_val.upper()) &
            (df["OCUPADA"].astype(str).str.upper().str.strip() == "NÃO")
        ]
        
        if filtro.empty:
            st.error(
                f"❌ Nenhuma Porta disponível encontrada para: {entrada}  \n"
                f"📞 Ligue para o TI para Atualizar a Caixa: (11) 94484-7040 ou clique no ícone do Whatsapp"
            )
            st.markdown(
                "<a href='https://wa.link/xcmibx' target='_blank'>"
                "<img src='https://logodownload.org/wp-content/uploads/2015/04/whatsapp-logo-2-1.png' width='40'></a>",
                unsafe_allow_html=True
            )
        else:
            st.success(f"🟢 Portas Disponíveis para: {entrada}")
            
            # Mostrar tabela simplificada
            colunas_ate_capacidade = filtro.loc[:, :"CAPACIDADE"]
            df_sem_indice = colunas_ate_capacidade.copy()
            df_sem_indice.index = [""] * len(df_sem_indice)
            st.table(df_sem_indice)
            
            # ===================== BOTÕES SIM / NÃO =====================
            for i, row in filtro.iterrows():
                st.write(f"Porta {row['PORTA']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"SIM - Porta {row['PORTA']}", key=f"sim_{i}"):
                        # Atualiza Data e colunas no DataFrame
                        now = datetime.now().strftime("%d/%m/%Y %H:%M")
                        df.at[i, "ADICIONOU_CLIENTE?"] = f"SIM, {now}"
                        df.at[i, "OCUPADA"] = "SIM"
                        # Atualiza na planilha
                        worksheet.update_cell(i+2, df.columns.get_loc("ADICIONOU_CLIENTE?")+1, df.at[i, "ADICIONOU_CLIENTE?"])
                        worksheet.update_cell(i+2, df.columns.get_loc("OCUPADA")+1, "SIM")
                        st.success(f"✅ Porta {row['PORTA']} atualizada com SIM")
                with col2:
                    if st.button(f"NÃO - Porta {row['PORTA']}", key=f"nao_{i}"):
                        st.info(f"❌ Porta {row['PORTA']} marcada como NÃO")
