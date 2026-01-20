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

# --- BARRA LATERAL (CADASTRO) ---
st.sidebar.image("logo.png") if os.path.exists("logo.png") else None
st.sidebar.header("📝 Novo Curso")

with st.sidebar.form("form_cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do Curso")
    url = st.text_input("Link (URL)")
    cat = st.selectbox("Categoria", ["Programação", "IA", "Marketing", "Outros"])
    if st.form_submit_button("Salvar"):
        if nome and url:
            if not url.startswith("http"): url = "https://" + url
            conn = sqlite3.connect('studyfacil.db')
            conn.execute("INSERT INTO cursos (nome, url, categoria) VALUES (?, ?, ?)", (nome, url, cat))
            conn.commit()
            conn.close()
            st.success("Cadastrado!")
            st.rerun()

# --- LISTAGEM ---
conn = sqlite3.connect('studyfacil.db')
df = pd.read_sql_query("SELECT * FROM cursos", conn)
conn.close()

if not df.empty:
    for _, row in df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 0.5])
            c1.markdown(f"**{row['nome']}** \n*{row['categoria']}*")
            c2.link_button("🚀 Estudar Agora", row['url'], use_container_width=True)
            if c3.button("🗑️", key=f"del_{row['id']}"):
                conn = sqlite3.connect('studyfacil.db')
                conn.execute("DELETE FROM cursos WHERE id=?", (row['id'],))
                conn.commit()
                conn.close()
                st.rerun()
            st.divider()
else:
    st.info("Cadastre seu primeiro link na barra lateral!")