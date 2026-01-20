import streamlit as st
import pandas as pd
from supabase import create_client
import os

# Configuração da Página
st.set_page_config(page_title="StudyFacil", page_icon="🎓", layout="wide")

# Conexão com Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- CABEÇALHO ---
col_logo, col_text = st.columns([1, 4])
if os.path.exists("logo.png"):
    with col_logo:
        st.image("logo.png", width=120)
    with col_text:
        st.title("StudyFacil")
        st.subheader("Sua Central de Cursos Organizada")
else:
    st.title("🎓 StudyFacil")

st.divider()

# --- BARRA LATERAL ---
st.sidebar.header("📝 Novo Curso")
with st.sidebar.form("form_cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do Curso")
    url = st.text_input("Link (URL)")
    cat = st.selectbox("Categoria", ["Programação", "IA", "Marketing", "Outros"])
    if st.form_submit_button("Salvar no Banco"):
        if nome and url:
            if not url.startswith("http"): url = "https://" + url
            # Ajuste: Enviando apenas os campos que você criou manualmente
            data = {"nome": nome, "url": url, "categoria": cat}
            try:
                supabase.table("cursos").insert(data).execute()
                st.success("Salvo com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# --- LISTAGEM ---
try:
    # Busca simplificada para evitar erros de ordenação se a coluna não existir
    response = supabase.table("cursos").select("*").execute()
    df = pd.DataFrame(response.data)
except Exception:
    df = pd.DataFrame()

if not df.empty:
    for _, row in df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 0.5])
            c1.markdown(f"### {row['nome']}")
            c1.caption(f"Categoria: {row['categoria']}")
            c2.markdown("<br>", unsafe_allow_html=True)
            c2.link_button("🚀 Estudar Agora", row['url'], use_container_width=True)
            if c3.button("🗑️", key=f"del_{row['id']}"):
                supabase.table("cursos").delete().eq("id", row['id']).execute()
                st.rerun()
            st.divider()
else:
    st.info("Nenhum curso salvo no Supabase ainda.")