import streamlit as st
import pandas as pd
from supabase import create_client
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="StudyFacil Pro", 
    page_icon="🎓", 
    layout="wide"
)

# CSS de Limpeza Total e Responsividade Profissional
st.markdown("""
    <style>
    /* Esconde menus técnicos do Streamlit Cloud */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    div[data-testid="stDecoration"] {display:none !important;}
    
    /* Estilo dos Cards de Cursos */
    .course-card {
        background-color: #ffffff;
        padding: 1.2rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #2E7D32;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Força botões a serem grandes e fáceis de clicar no Celular */
    @media (max-width: 640px) {
        .stButton>button { 
            width: 100% !important; 
            height: 50px !important; 
            margin-bottom: 10px !important;
            font-size: 16px !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# 2. Conexão com Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- CATEGORIAS ---
categorias_estudo = [
    "IA e Machine Learning", "Desenvolvimento de Software", "Ciência de Dados", 
    "Segurança da Informação", "Cloud Computing", "UX/UI Design", "Administração e Gestão", 
    "Marketing Digital", "Finanças e Contabilidade", "Logística", "Enfermagem", 
    "Psicologia", "Educação Física", "Nutrição", "Pedagogia", "Idiomas", 
    "Engenharia e Arquitetura", "Design Gráfico", "Edição de Vídeo", 
    "Curso Preparatório", "Curso Técnico", "Horas Complementares", "Outros"
]

# Inicializa sessão
if 'user' not in st.session_state:
    st.session_state.user = None

# --- TELA DE LOGIN / CADASTRO ---
if st.session_state.user is None:
    col_auth = st.columns([0.05, 0.9, 0.05])[1]
    with col_auth:
        st.title("🎓 StudyFacil")
        tab1, tab2 = st.tabs(["Entrar", "Criar Conta"])
        
        with tab1:
            with st.form("login"):
                email = st.text_input("E-mail")
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Acessar"):
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                        if res.user:
                            st.session_state.user = res.user
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
        
        with tab2:
            with st.form("cadastro"):
                new_email = st.text_input("E-mail para cadastro")
                new_senha = st.text_input("Senha (mín. 6 dígitos)", type="password")
                if st.form_submit_button("Cadastrar"):
                    try:
                        supabase.auth.sign_up({"email": new_email, "password": new_senha})
                        st.success("Conta criada! Já pode fazer login.")
                    except Exception as e:
                        st.error(f"Erro: {e}")

# --- APP PRINCIPAL (LOGADO) ---
else:
    user_id = st.session_state.user.id
    
    # Cabeçalho com Opção de Sair
    c_tit, c_sair = st.columns([4, 1])
    with c_tit:
        st.title("🎓 StudyFacil")
    with c_sair:
        if st.button("🔴 Sair", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

    # --- CADASTRO DE CURSO (AGORA NO CORPO DA PÁGINA PARA MELHORAR O MOBILE) ---
    with st.expander("➕ Adicionar Novo Curso", expanded=False):
        with st.form("add_curso", clear_on_submit=True):
            nome = st.text_input("Nome do Curso")
            url = st.text_input("Link (URL)")
            cat = st.selectbox("Área/Categoria", categorias_estudo)
            if st.form_submit_button("Salvar no Banco"):
                if nome and url:
                    if not url.startswith("http"): url = "https://" + url
                    data = {"nome": nome, "url": url, "categoria": cat, "user_id": user_id, "concluido": False}
                    supabase.table("cursos").insert(data).execute()
                    st.rerun()

    st.divider()

    # --- BUSCA E FILTROS ---
    c_busca, c_filtro = st.columns([1, 1])
    busca = c_busca.text_input("🔍 Buscar", placeholder="Nome do curso...")
    filtro_cat = c_filtro.selectbox("Área", ["Todas"] + categorias_estudo)

    # --- LISTAGEM ---
    try:
        response = supabase.table("cursos").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        df = pd.DataFrame(response.data)
    except:
        df = pd.DataFrame()

    if not df.empty:
        if busca: df = df[df['nome'].str.contains(busca, case=False)]
        if filtro_cat != "Todas": df = df[df['categoria'] == filtro_cat]

        for _, row in df.iterrows():
            st.markdown(f"""<div class="course-card">
                <h4 style="margin:0;">{'✅ ' if row['concluido'] else '📖 '} {row['nome']}</h4>
                <p style="font-size: 0.85rem; color: #666; margin-top: 5px;">Área: {row['categoria']}</p>
            </div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([2, 1, 0.5])
            c1.link_button("🚀 Abrir Aula", row['url'], use_container_width=True)
            
            label_btn = "Refazer" if row['concluido'] else "Concluir"
            if c2.button(label_btn, key=f"ch_{row['id']}", use_container_width=True):
                supabase.table("cursos").update({"concluido": not row['concluido']}).eq("id", row['id']).execute()
                st.rerun()
                
            if c3.button("🗑️", key=f"del_{row['id']}", use_container_width=True):
                supabase.table("cursos").delete().eq("id", row['id']).execute()
                st.rerun()
    else:
        st.info("Nenhum curso cadastrado.")