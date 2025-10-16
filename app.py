import streamlit as st
import pandas as pd

BACKGROUND_URL = "https://raw.githubusercontent.com/leomarjms26-netizen/app.py/refs/heads/main/Copilot_20251016_121602.png"

st.markdown(
    f"""
    <style>
    /* Fundo do app */
    html, body, [class*="stAppViewContainer"], [class*="stApp"], [data-testid="stAppViewContainer"] {{
        background: linear-gradient(rgba(5,85,119,0.75), rgba(5,85,119,0.75)),
                    url('{BACKGROUND_URL}') !important;
        background-size: cover !important;
        background-position: center center !important;
        background-attachment: fixed !important;
    }}

    /* Cabeçalho e barra lateral */
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {{
        background: rgba(5,85,119,0.7) !important;
        backdrop-filter: blur(6px);
    }}

    /* Texto e títulos em branco */
    h1, h2, h3, h4, h5, h6, p, label, span, div {{
        color: #f8f9fa !important;
    }}

    /* Caixas escuras translúcidas para componentes */
    .stFileUploader, .stDownloadButton, .stTextInput, .stSelectbox, .stAlert {{
        background-color: rgba(0, 0, 0, 0.55) !important;
        border-radius: 12px;
        padding: 14px;
        color: #ffffff !important;
    }}

    /* Borda e sombra sutil */
    .stFileUploader, .stDownloadButton {{
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255,255,255,0.1);
    }}

    /* Botões principais e de download */
    button[kind="primary"], .stDownloadButton > button, div.stButton > button {{
        background-color: rgb(32, 201, 58) !important;
        color: #ffffff !important;
        border: none !important;
    }}
    button[kind="primary"]:hover, .stDownloadButton > button:hover, div.stButton > button:hover {{
        background-color: rgb(20, 160, 45) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Ícones da aba
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


entrada = st.text_input("", "").upper()


buscar = st.button("🔍 Buscar")

if buscar and entrada:
    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRrExQYNSa64iJs2DK5MrnUhsXSrPhrxqYswB1zTRYCoGlAw9gMqh5d5G5SMaDaJtDd78gy4Ud-UHFW/pub?output=xlsx"
        df = pd.read_excel(url)
        df.columns = [
            "CABO", "PRIMARIA", "CAIXA", "ID", "PORTA", "CAPACIDADE",
            "INTERFACE", "DATA_DE_ATUALIZACAO", "OCUPADA", "OBSERVACAO", "ADICIONOU_CLIENTE"
        ]

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

            colunas_ate_capacidade = filtro.loc[:, :"CAPACIDADE"]
            df_sem_indice = colunas_ate_capacidade.copy()
            df_sem_indice.index = [""] * len(df_sem_indice)

            html_tabela = df_sem_indice.to_html(index=False, escape=False)
            html_tabela = html_tabela.replace('<table border="1" class="dataframe">', '<table style="width:100%; border-collapse: collapse;">')

            st.markdown(
                f"""
                <div style="
                    background-color: rgba(0,0,0,0.55);
                    padding: 12px;
                    border-radius: 12px;
                    overflow-x: auto;
                ">
                    {html_tabela}
                </div>
                """,
                unsafe_allow_html=True
            )

