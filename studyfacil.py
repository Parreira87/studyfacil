import streamlit as st
import pandas as pd
from supabase import create_client
import os

# 1. Configuração da Página e Estilo Profissional
st.set_page_config(page_title="StudyFacil Pro", page_icon="🎓", layout="wide")

# CSS para esconder o menu do Streamlit, o ícone do GitHub e estilizar os cards
st.markdown("""
    <style>
    /* Esconde o menu do Streamlit (canto superior direito) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Esconde o ícone do GitHub que aparece no deploy do Streamlit Cloud */
    .stAppDeployButton {display:none;}
    
    .course-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #2E7D32;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .stButton>button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# 2. Conexão com Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- CATEGORIAS ORGANIZADAS ---
categorias_estudo = [
    "IA e Machine Learning", "Desenvolvimento de Software (Web/Mobile)", "Ciência de Dados", 
    "Segurança da Informação", "Cloud Computing", "UX/UI Design", "Administração e Gestão", 
    "Marketing Digital", "Finanças e Contabilidade", "RH", "Gestão de Projetos", 
    "Logística", "Enfermagem", "Psicologia", "Educação Física", "Nutrição", 
    "Pedagogia", "Idiomas", "Engenharia e Arquitetura", "Automação", "Design Gráfico", 
    "Edição de Vídeo", "Curso Preparatório", "Curso Técnico", "Horas Complementares", "Outros"
]

# --- GERENCIAMENTO DE SESSÃO ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- TELAS DE ACESSO (LOGIN / CADASTRO) ---
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🎓 StudyFacil")
        tab1, tab2 = st.tabs(["Entrar", "Criar Conta"])
        
        with tab1:
            with st.form("login"):
                email = st.text_input("E-mail")
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Acessar Sistema"):
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                        if res.user:
                            st.session_state.user = res.user
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro no login: {e}")
        
        with tab2:
            st.info("Cadastre-se para ter sua própria lista de cursos.")
            with st.form("cadastro"):
                new_email = st.text_input("Novo E-mail")
                new_senha = st.text_input("Senha (mín. 6 dígitos)", type="password")
                if st.form_submit_button("Finalizar Cadastro"):
                    try:
                        supabase.auth.sign_up({"email": new_email, "password": new_senha})
                        st.success("Conta criada! Já pode tentar o login.")
                    except Exception as e:
                        st.error(f"Erro no cadastro: {e}")

# --- APP PRINCIPAL (USUÁRIO LOGADO) ---
else:
    user_id = st.session_state.user.id
    
    # Barra Lateral com Logout
    st.sidebar.markdown(f"👤 Conectado como:\n**{st.session_state.user.email}**")
    if st.sidebar.button("🔴 Sair da Conta", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()
    
    st.sidebar.divider()
    st.sidebar.header("📝 Novo Curso")
    with st.sidebar.form("add_curso", clear_on_submit=True):
        nome = st.text_input("Nome do Curso")
        url = st.text_input("Link (URL)")
        cat = st.selectbox("Categoria", categorias_estudo)
        if st.form_submit_button("Salvar no Banco"):
            if nome and url:
                if not url.startswith("http"): url = "https://" + url
                data = {"nome": nome, "url": url, "categoria": cat, "user_id": user_id, "concluido": False}
                supabase.table("cursos").insert(data).execute()
                st.rerun()

    # Cabeçalho Principal com Logo
    col_l, col_t = st.columns([1, 5])
    if os.path.exists("logo.png"):
        with col_l: st.image("logo.png", width=100)
    with col_t:
        st.title("Meus Estudos")
        st.caption("Central de Cursos Organizada")

    st.divider()

    # Busca e Filtros
    c_busca, c_filtro = st.columns([3, 1])
    busca = c_busca.text_input("🔍 Buscar por nome...", placeholder="Ex: Python, Marketing...")
    filtro_cat = c_filtro.selectbox("Filtrar por Área", ["Todas"] + categorias_estudo)

    # Listagem de Dados do Usuário
    try:
        response = supabase.table("cursos").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        df = pd.DataFrame(response.data)
    except:
        df = pd.DataFrame()

    if not df.empty:
        if busca: df = df[df['nome'].str.contains(busca, case=False)]
        if filtro_cat != "Todas": df = df[df['categoria'] == filtro_cat]

        # Backup CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📥 Baixar Backup (CSV)", csv, "meus_estudos.csv", use_container_width=True)

        for _, row in df.iterrows():
            st.markdown(f"""<div class="course-card">
                <h4 style="margin:0;">{'✅ ' if row['concluido'] else '📖 '} {row['nome']}</h4>
                <small><b>Área:</b> {row['categoria']}</small>
            </div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([3, 1, 0.5])
            c1.link_button("🚀 Abrir Aula", row['url'], use_container_width=True)
            
            label_btn = "Refazer" if row['concluido'] else "Concluir"
            if c2.button(label_btn, key=f"check_{row['id']}"):
                supabase.table("cursos").update({"concluido": not row['concluido']}).eq("id", row['id']).execute()
                st.rerun()
                
            if c3.button("🗑️", key=f"del_{row['id']}"):
                supabase.table("cursos").delete().eq("id", row['id']).execute()
                st.rerun()
    else:
        st.info("Sua lista está vazia.")