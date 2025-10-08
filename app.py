import streamlit as st
import pandas as pd
import json
import os

# Caminho do arquivo manifest.json
manifest_path = "manifest.json"

if os.path.exists(manifest_path):
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # Monta as meta tags dinamicamente com todos os ícones do manifest
    meta_tags = ""
    for icon in manifest.get("icons", []):
        sizes = icon.get("sizes", "")
        src = icon.get("src", "")
        if sizes and src:
            meta_tags += f'<link rel="icon" type="image/png" sizes="{sizes}" href="{src}">\n'
    
    # Adiciona o apple-touch-icon (primeiro ícone como padrão)
    if manifest.get("icons"):
        apple_icon = manifest["icons"][0].get("src", "")
        if apple_icon:
            meta_tags = f'<link rel="apple-touch-icon" sizes="180x180" href="{apple_icon}">\n' + meta_tags

    # Link para o manifest
    meta_tags += f'<link rel="manifest" href="{manifest_path}">'

    st.markdown(meta_tags, unsafe_allow_html=True)
else:
    st.warning("Arquivo manifest.json não encontrado.")

# Links fixos para fallback (usando PNG)
st.markdown(
    """
    <link rel="apple-touch-icon" sizes="180x180" href="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png">
    <link rel="icon" type="image/png" sizes="32x32" href="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png">
    <link rel="icon" type="image/png" sizes="16x16" href="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png">
    <link rel="manifest" href="manifest.json">
    """,
    unsafe_allow_html=True
)

# Atualiza o ícone da página
st.set_page_config(
    page_title="Verificador de Portas",
    page_icon="c64a4e55-0ce2-40c5-9392-fdc6f50f8b1aPNG.png"
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
            st.error(f"❌ Nenhuma Porta disponível encontrada para: {entrada}\n📞 Ligue para o TI para Atualizar a Caixa: (11) 94484-7040 ou Clique no Ícone do Whatsapp para ser redirecionado")
            st.markdown(
                "<a href='https://wa.link/xcmibx' target='_blank'>"
                "<img src='https://logodownload.org/wp-content/uploads/2015/04/whatsapp-logo-2-1.png' width='40'></a>",
                unsafe_allow_html=True
            )
        else:
            st.success(f"🟢 Portas Disponíveis para: {entrada}")
            
            # Seleciona apenas as colunas até 'CAPACIDADE'
            colunas_ate_capacidade = filtro.loc[:, :"CAPACIDADE"]
            
            # Cria um novo DataFrame sem índice
            df_sem_indice = colunas_ate_capacidade.copy()
            df_sem_indice.index = [""] * len(df_sem_indice)  # esconde o índice lateral
            
            # Mostra no Streamlit
            st.table(df_sem_indice)


















