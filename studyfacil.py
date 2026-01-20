import streamlit as st
import pandas as pd
from supabase import create_client
import os

# 1. Configuração da Página - Forçando a barra lateral aberta
st.set_page_config(
    page_title="StudyFacil Pro", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Avançado: Remove TODOS os ícones técnicos e melhora o layout
st.markdown("""
    <style>
    /* 1. Esconde menus padrão e rodapés */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. Remove o botão flutuante 'Manage App' e ícones de deploy */
    .stAppDeployButton {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    
    /* 3. Remove especificamente os ícones que sobraram no canto inferior (Streamlit/Cloud) */
    div[data-testid="stDecoration"] {display:none !important;}
    div[class^="st-emotion-cache-"] button {display:none !important;}
    .viewerBadge_container__1QSob {display:none !important;}
    
    /* 4. Estilo dos Cards de Cursos */
    .course-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #2E7D32;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* 5. Responsividade para botões no celular */
    @media (max-width: 640px) {
        .stButton>button { width: 100% !important; margin-bottom: 8px; height: 45px; }
    }
    </style>
""", unsafe_allow_html=True)

# 2. Conexão com Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- CATEGORIAS PROFISSIONAIS ---
categorias_estudo = [
    "IA e Machine Learning", "Desenvolvimento de Software (Web/Mobile)", "Ciência de Dados", 
    "Segurança da Informação", "Cloud Computing", "UX/UI Design", "Administração e Gestão", 
    "Marketing Digital", "Finanças e Contabilidade", "RH", "Gestão de Projetos", 
    "Logística", "Enfermagem", "Psicologia", "Educação Física", "Nutrição", 
    "Pedagogia", "Idiomas", "Engenharia e Arquitetura", "Automação", "Design Gráfico", 
    "Edição de Vídeo", "Curso Preparatório", "Curso Técnico", "Horas Complementares", "Outros"
]

if 'user' not in st.session_state:
    st.session_state.user = None

# --- TELAS DE ACESSO (LOGIN / CADASTRO) ---
if st.session_state.user is None:
    col1, col2, col3 = st.columns([0.05, 0.9, 0.05])
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
                        st.error(f"Erro: {e}")
        
        with tab2:
            st.info("Crie sua conta para salvar seus cursos.")
            with st.form("cadastro"):
                new_email = st.text_input("E-mail")
                new_senha = st.text_input("Senha (mín. 6 dígitos)", type="password")
                if st.form_submit_button("Criar Conta"):
                    try:
                        supabase.auth.sign_up({"email": new_email, "password": new_senha})
                        st.success("Cadastro realizado!")
                    except Exception as e:
                        st.error(f"Erro: {e}")

# --- APP PRINCIPAL (USUÁRIO LOGADO) ---
else:
    user_id = st.session_state.user.id
    
    # Barra Lateral
    st.sidebar.markdown(f"👤 **{st.session_state.user.email}**")
    if st.sidebar.button("🔴 Sair da Conta", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()
    
    st.sidebar.divider()
    st.sidebar.header("📝 Novo Curso")
    with st.sidebar.form("add_curso", clear_on_submit=True):
        nome = st.text_input("Nome")
        url = st.text_input("Link URL")
        cat = st.selectbox("Área", categorias_estudo)
        if st.form_submit_button("Salvar no Banco"):
            if nome and url:
                if not url.startswith("http"): url = "https://" + url
                data = {"nome": nome, "url": url, "categoria": cat, "user_id": user_id, "concluido": False}
                supabase.table("cursos").insert(data).execute()
                st.rerun()

    # Título Principal
    st.title("Meus Estudos")

    # Busca e Filtros - Ajustado para ocupar menos espaço no Mobile
    st.divider()
    c_busca, c_filtro = st.columns([1, 1])
    busca = c_busca.text_input("🔍 Buscar", placeholder="Nome...")
    filtro_cat = c_filtro.selectbox("Área", ["Todas"] + categorias_estudo)

    # Listagem de Dados
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
                <p style="font-size: 0.8rem; color: gray; margin-top: 5px;">{row['categoria']}</p>
            </div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([2, 1, 0.5])
            c1.link_button("🚀 Abrir Aula", row['url'], use_container_width=True)
            
            label_btn = "Refazer" if row['concluido'] else "Concluir"
            if c2.button(label_btn, key=f"check_{row['id']}", use_container_width=True):
                supabase.table("cursos").update({"concluido": not row['concluido']}).eq("id", row['id']).execute()
                st.rerun()
                
            if c3.button("🗑️", key=f"del_{row['id']}", use_container_width=True):
                supabase.table("cursos").delete().eq("id", row['id']).execute()
                st.rerun()
    else:
        st.info("Nenhum curso encontrado.")