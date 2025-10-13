import streamlit as st
import pandas as pd
from datetime import datetime

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
            "INTERFACE", "DATA_DE_ATUALIZACAO", "OCUPADA", "OBSERVACAO", "ADICINOU_CLIENTE"
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

            # Pega apenas a primeira linha
            row = filtro.iloc[0]

            # Mostra as informações
            st.write({
                "CABO": row["CABO"],
                "PRIMARIA": row["PRIMARIA"],
                "CAIXA": row["CAIXA"],
                "ID": row["ID"],
                "PORTA": row["PORTA"],
                "CAPACIDADE": row["CAPACIDADE"]
            })

            # Botões lado a lado
            col1, col2 = st.columns(2)
            if col1.button("Sim", key="sim"):
                st.success(f"Cliente ADICIONADO em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            if col2.button("Não", key="nao"):
                st.info("Cliente NÃO adicionado")
