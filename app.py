import streamlit as st
import pandas as pd

# Define a cor de fundo RGB
r, g, b = 37, 247, 93

# Injeta CSS para mudar o background
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: rgb({r}, {g}, {b});
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Verificador de Portas Disponíveis" )

st.markdown(
    "Digite o identificador (ex: CB07-SP06-CX15)  \n"
    "Observação: Caso o Bairro for Jaguaré, sempre será o CB16"
)

entrada = st.text_input("", "").upper()

if entrada:
    try:
        cabo_val, primaria_val, caixa_val = [x.strip() for x in entrada.split("-")]
    except ValueError:
        st.error("❌ Formato inválido. Use: CB01-SP01-CX01")
    else:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRrExQYNSa64iJs2DK5MrnUhsXSrPhrxqYswB1zTRYCoGlAw9gMqh5d5G5SMaDaJtDd78gy4Ud-UHFW/pub?output=xlsx"
        df = pd.read_excel(url)
        df.columns = [
            "CABO", "PRIMARIA", "CAIXA", "ID", "PORTA", "CAPACIDADE",
            "INTERFACE", "DATA_DE_ATUALIZACAO", "OCUPADA", "OBSERVACAO"
        ]

        filtro = df[
            (df["CABO"].astype(str).str.upper().str.strip() == cabo_val.upper()) &
            (df["PRIMARIA"].astype(str).str.upper().str.strip() == primaria_val.upper()) &
            (df["CAIXA"].astype(str).str.upper().str.strip() == caixa_val.upper()) &
            (df["OCUPADA"].astype(str).str.upper().str.strip() == "NÃO")
        ]

        if filtro.empty:
            st.error(f"❌ Nenhuma Porta disponível encontrada para: {entrada}\n📞 Ligue para o TI para Atualizar a Caixa: (11) 94484-7040")
        else:
            st.success(f"🟢 Portas Disponíveis para: {entrada}")

            st.dataframe(filtro)





