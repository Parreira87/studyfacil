import streamlit as st
import pandas as pd
from supabase import create_client
import os

# 1. Configuração de Estilo e Página
st.set_page_config(page_title="StudyFacil Pro", page_icon="🎓", layout="wide")

# CSS para criar os Cards Profissionais
st.markdown("""
    <style>
    .course-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #4CAF50;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Conexão com Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- CABEÇALHO ---
col_logo, col_text = st.columns([1, 5])
if os.path.exists("logo.png"):
    with col_logo: st.image("logo.png", width=120)
    with col_text:
        st.title("StudyFacil")
        st.subheader("Sua Central de Estudos Profissional")
else:
    st.title("🎓 StudyFacil")

st.divider()

# --- BARRA LATERAL (CADASTRO E BACKUP) ---
st.sidebar.header("📝 Novo Curso")
with st.sidebar.form("form_cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do Curso")
    url = st.text_input("Link (URL)")
    cat = st.selectbox("Categoria", ["Programação", "IA", "No-Code", "Marketing", "Outros"])
    if st.form_submit_button("Salvar no Banco"):
        if nome and url:
            if not url.startswith("http"): url = "https://" + url
            data = {"nome": nome, "url": url, "categoria": cat, "concluido": False}
            supabase.table("cursos").insert(data).execute()
            st.success("Salvo!")
            st.rerun()

# --- BUSCA E FILTROS ---
st.write("### 🔍 Seus Cursos")
col_busca, col_filtro = st.columns([3, 1])
busca = col_busca.text_input("Buscar por nome...", placeholder="O que você quer estudar hoje?")
filtro_cat = col_filtro.selectbox("Filtrar Categoria", ["Todos", "Programação", "IA", "No-Code", "Marketing", "Outros"])

# --- LISTAGEM ---
try:
    response = supabase.table("cursos").select("*").order("created_at", desc=True).execute()
    df = pd.DataFrame(response.data)
except Exception:
    df = pd.DataFrame()

if not df.empty:
    # Lógica de Filtros
    if busca: df = df[df['nome'].str.contains(busca, case=False)]
    if filtro_cat != "Todos": df = df[df['categoria'] == filtro_cat]

    # Botão de Backup CSV na Sidebar
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Baixar Backup (CSV)", data=csv, file_name="meus_cursos.csv", use_container_width=True)

    # Exibição em Cards
    for _, row in df.iterrows():
        st.markdown(f"""<div class="course-card">
            <h4 style="margin:0;">{'✅ ' if row['concluido'] else '📖 '} {row['nome']}</h4>
            <small>Categoria: {row['categoria']}</small>
        </div>""", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([3, 1, 0.5])
        c1.link_button("🚀 Estudar Agora", row['url'], use_container_width=True)
        
        label_btn = "Refazer" if row['concluido'] else "Concluir"
        if c2.button(label_btn, key=f"btn_{row['id']}", use_container_width=True):
            supabase.table("cursos").update({"concluido": not row['concluido']}).eq("id", row['id']).execute()
            st.rerun()
            
        if c3.button("🗑️", key=f"del_{row['id']}"):
            supabase.table("cursos").delete().eq("id", row['id']).execute()
            st.rerun()
        st.write("")
else:
    st.info("Nenhum curso encontrado.")